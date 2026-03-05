import re
from typing import Dict, Optional
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup


CONTACT_EXCLUDED_DOMAINS = {
    "saramin.co.kr",
    "jobkorea.co.kr",
    "incruit.com",
    "wanted.co.kr",
    "map.naver.com",
    "google.com",
    "google.co.kr",
    "youtube.com",
    "facebook.com",
    "instagram.com",
}

EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}")
PHONE_PATTERN = re.compile(r"(?:\\+82[- ]?)?0\\d{1,2}[- )]?\\d{3,4}[- ]?\\d{4}")
ADDRESS_PATTERN = re.compile(
    r"(?:\\b(?:\\uc11c\\uc6b8|\\ubd80\\uc0b0|\\ub300\\uad6c|\\uc778\\ucc9c|\\uad11\\uc8fc|\\ub300\\uc804|\\uc6b8\\uc0b0|\\uc138\\uc885|\\uacbd\\uae30|\\uac15\\uc6d0|\\ucda9\\ubd81|\\ucda9\\ub0a8|\\uc804\\ubd81|\\uc804\\ub0a8|\\uacbd\\ubd81|\\uacbd\\ub0a8|\\uc81c\\uc8fc)\\b[^\\n]{0,80})"
)


def make_discovery_links(company: str) -> Dict[str, str]:
    encoded = quote_plus(company)
    return {
        "naver_map_link": f"https://map.naver.com/v5/search/{encoded}",
        "google_search_link": f"https://www.google.com/search?q={encoded}",
        "smartstore_link": f"https://search.shopping.naver.com/search/all?query={encoded}",
    }


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


def _first(values: list[str]) -> Optional[str]:
    return values[0] if values else None


def _is_allowed_link(url: str) -> bool:
    host = urlparse(url).netloc.lower()
    if not host:
        return False
    return all(excluded not in host for excluded in CONTACT_EXCLUDED_DOMAINS)


def _normalize_result_url(raw_url: str) -> Optional[str]:
    candidate = (raw_url or "").strip()
    if not candidate:
        return None
    if candidate.startswith("//"):
        candidate = f"https:{candidate}"

    parsed = urlparse(candidate)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        query = parse_qs(parsed.query)
        uddg = query.get("uddg", [])
        if uddg:
            return unquote(uddg[0])

    return candidate if candidate.startswith("http") else None


def _find_homepage(session: requests.Session, company: str, location: Optional[str]) -> Optional[str]:
    query = f"{company} {location or ''} homepage"
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"

    try:
        response = session.get(search_url, timeout=10)
        response.raise_for_status()
    except requests.RequestException:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    for anchor in soup.select("a.result__a"):
        href = _normalize_result_url(anchor.get("href") or "")
        if href and href.startswith("http") and _is_allowed_link(href):
            return href
    return None


def _extract_contacts(html: str) -> Dict[str, Optional[str]]:
    soup = BeautifulSoup(html, "html.parser")
    text = soup.get_text(" ", strip=True)

    emails = sorted(set(EMAIL_PATTERN.findall(text)))
    phones = sorted(set(PHONE_PATTERN.findall(text)))
    addresses = sorted(set(ADDRESS_PATTERN.findall(text)))

    return {
        "email": _first(emails),
        "phone": _first(phones),
        "address": _first(addresses),
    }


def find_company_contacts(
    company: str,
    location: Optional[str] = None,
    session: Optional[requests.Session] = None,
) -> Dict[str, Optional[str]]:
    local_session = session or _make_session()
    own_session = session is None

    links = make_discovery_links(company)
    result: Dict[str, Optional[str]] = {
        "address": None,
        "phone": None,
        "email": None,
        "homepage": None,
        **links,
    }

    try:
        homepage = _find_homepage(local_session, company, location)
        if not homepage:
            return result

        result["homepage"] = homepage

        try:
            response = local_session.get(homepage, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            return result

        extracted = _extract_contacts(response.text)
        result.update(extracted)
        return result
    finally:
        if own_session:
            local_session.close()
