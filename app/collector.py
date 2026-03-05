import logging
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


Job = Dict[str, Optional[str]]

DEFAULT_KEYWORDS = ("엑셀", "주문관리")
MAX_PAGES = 3
REQUEST_TIMEOUT = 15
MAX_RETRIES = 3
BACKOFF_SECONDS = (1, 2, 4)
SARAMIN_BASE_URL = "https://www.saramin.co.kr"
SARAMIN_SEARCH_URL = f"{SARAMIN_BASE_URL}/zf_user/search"
SARAMIN_API_URL = "https://oapi.saramin.co.kr/job-search"


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("collector")
    if logger.handlers:
        return logger

    out_dir = Path("out")
    out_dir.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(out_dir / "run.log", encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))

    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    logger.propagate = False
    return logger


LOGGER = _get_logger()


def _make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0.0.0 Safari/537.36"
            ),
            "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        }
    )
    return session


def _request_with_retry(
    session: requests.Session, method: str, url: str, **kwargs: Any
) -> Optional[requests.Response]:
    kwargs.setdefault("timeout", REQUEST_TIMEOUT)

    for attempt in range(MAX_RETRIES):
        try:
            response = session.request(method, url, **kwargs)
            if response.status_code >= 500:
                raise requests.HTTPError(f"server error: {response.status_code}")
            return response
        except (requests.ConnectionError, requests.Timeout, requests.HTTPError) as exc:
            if attempt == MAX_RETRIES - 1:
                LOGGER.error("Request failed after retries: %s %s (%s)", method, url, exc)
                return None
            time.sleep(BACKOFF_SECONDS[attempt])

    return None


def _safe_text(element: Any) -> Optional[str]:
    if element is None:
        return None
    text = element.get_text(" ", strip=True)
    return text or None


def _extract_location(item: Any) -> Optional[str]:
    span = item.select_one(".job_condition > span")
    if span is None:
        return None

    linked_parts = [a.get_text(" ", strip=True) for a in span.select("a") if a.get_text(strip=True)]
    if linked_parts:
        return " ".join(linked_parts)

    text = span.get_text(" ", strip=True)
    return text or None


def _parse_html_search(html: str) -> List[Job]:
    soup = BeautifulSoup(html, "html.parser")
    jobs: List[Job] = []

    for item in soup.select(".item_recruit"):
        title_link = item.select_one(".job_tit a") or item.select_one("h2 a")
        company_el = item.select_one(".corp_name a") or item.select_one(".corp_name")
        sector_el = item.select_one(".job_sector")

        href = title_link.get("href") if title_link else None
        job_url = urljoin(SARAMIN_BASE_URL, href) if href else None

        jobs.append(
            {
                "company": _safe_text(company_el),
                "title": _safe_text(title_link),
                "location": _extract_location(item),
                "url": job_url,
                "description": _safe_text(sector_el),
            }
        )

    return jobs


def _collect_from_search(session: requests.Session, keywords: List[str]) -> List[Job]:
    collected: List[Job] = []
    seen_urls = set()

    for keyword in keywords:
        for page in range(1, MAX_PAGES + 1):
            response = _request_with_retry(
                session,
                "GET",
                SARAMIN_SEARCH_URL,
                params={
                    "searchType": "search",
                    "searchword": keyword,
                    "recruitPage": page,
                },
            )
            if response is None:
                continue
            if response.status_code >= 400:
                LOGGER.warning(
                    "Search request rejected: keyword=%s page=%s status=%s",
                    keyword,
                    page,
                    response.status_code,
                )
                continue

            page_jobs = _parse_html_search(response.text)
            if not page_jobs:
                LOGGER.warning(
                    "No jobs parsed from search page: keyword=%s page=%s", keyword, page
                )
                continue

            for job in page_jobs:
                url = job.get("url")
                if not url or url in seen_urls:
                    continue
                seen_urls.add(url)
                collected.append(job)

    return collected


def _collect_from_api(session: requests.Session, keywords: List[str], api_key: str) -> List[Job]:
    collected: List[Job] = []
    seen_urls = set()

    for keyword in keywords:
        for page in range(1, MAX_PAGES + 1):
            response = _request_with_retry(
                session,
                "GET",
                SARAMIN_API_URL,
                params={
                    "access-key": api_key,
                    "keywords": keyword,
                    "count": 50,
                    "start": (page - 1) * 50,
                    "output": "json",
                },
            )
            if response is None or response.status_code >= 400:
                continue

            try:
                payload = response.json()
            except ValueError:
                LOGGER.warning("Saramin API returned non-JSON payload for keyword=%s", keyword)
                continue

            api_jobs = payload.get("jobs", {}).get("job", [])
            if isinstance(api_jobs, dict):
                api_jobs = [api_jobs]

            for item in api_jobs:
                position = item.get("position", {}) if isinstance(item, dict) else {}
                company = item.get("company", {}) if isinstance(item, dict) else {}
                company_detail = company.get("detail", {}) if isinstance(company, dict) else {}
                location = position.get("location", {}) if isinstance(position, dict) else {}

                job_url = position.get("url")
                if not job_url or job_url in seen_urls:
                    continue

                seen_urls.add(job_url)
                collected.append(
                    {
                        "company": company_detail.get("name"),
                        "title": position.get("title"),
                        "location": location.get("name"),
                        "url": job_url,
                        "description": None,
                    }
                )

    return collected


def collect_jobs() -> List[Job]:
    session = _make_session()
    keywords = list(DEFAULT_KEYWORDS)
    api_key = os.getenv("SARAMIN_API_KEY")

    try:
        if api_key:
            jobs = _collect_from_api(session, keywords, api_key)
            if jobs:
                LOGGER.info("수집 건수: %s (source=api)", len(jobs))
                return jobs
            LOGGER.warning("Saramin API returned no jobs. Falling back to HTML search parsing.")

        jobs = _collect_from_search(session, keywords)
        LOGGER.info("수집 건수: %s (source=search)", len(jobs))
        return jobs
    except Exception as exc:
        LOGGER.exception("Collector unexpected failure: %s", exc)
        return []
    finally:
        session.close()
