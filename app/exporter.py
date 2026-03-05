import time
from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


JobWithScore = Dict[str, str | int | None]
OUTPUT_COLUMNS = [
    "score",
    "company",
    "title",
    "location",
    "summary",
    "url",
    "address",
    "phone",
    "email",
    "homepage",
    "naver_map_link",
    "google_search_link",
    "smartstore_link",
    "business_phone",
    "business_email",
    "business_address",
    "homepage_link",
]

DOMAIN_KEYWORDS = (
    "\uc1fc\ud551\ubab0",
    "\uc2a4\ub9c8\ud2b8\uc2a4\ud1a0\uc5b4",
    "\ucfe0\ud321",
    "\uc624\ud508\ub9c8\ucf13",
    "\uc8fc\ubb38\uad00\ub9ac",
    "\ucd9c\uace0\uad00\ub9ac",
    "\ubc1c\uc8fc\uad00\ub9ac",
)

SKILL_KEYWORDS = (
    "\uc5d1\uc140",
    "\ub9ac\ud3ec\ud2b8",
    "\uc815\uc0b0",
    "\ub370\uc774\ud130",
)


def _extract_keywords(title: str, keywords: tuple[str, ...]) -> List[str]:
    found: List[str] = []
    for keyword in keywords:
        if keyword in title and keyword not in found:
            found.append(keyword)
    return found


def build_summary_from_title(title: Optional[str]) -> str:
    text = (title or "").strip()
    if not text:
        return ""

    domain_parts = _extract_keywords(text, DOMAIN_KEYWORDS)
    skill_parts = _extract_keywords(text, SKILL_KEYWORDS)

    if domain_parts and skill_parts:
        return f"{', '.join(domain_parts[:2])} / {', '.join(skill_parts[:2])}"
    if domain_parts:
        return ", ".join(domain_parts[:3])
    if skill_parts:
        return ", ".join(skill_parts[:3])

    return text[:60]


def _normalize_job(job: JobWithScore) -> Dict[str, str | int | None]:
    title = (job.get("title") or "").strip()
    return {
        "score": int(job.get("score") or 0),
        "company": (job.get("company") or "").strip(),
        "title": title,
        "location": job.get("location") or "",
        "summary": build_summary_from_title(title),
        "url": (job.get("url") or "").strip(),
        "address": (job.get("address") or "").strip() if isinstance(job.get("address"), str) else "",
        "phone": (job.get("phone") or "").strip() if isinstance(job.get("phone"), str) else "",
        "email": (job.get("email") or "").strip() if isinstance(job.get("email"), str) else "",
        "homepage": (job.get("homepage") or "").strip() if isinstance(job.get("homepage"), str) else "",
        "naver_map_link": (job.get("naver_map_link") or "").strip() if isinstance(job.get("naver_map_link"), str) else "",
        "google_search_link": (job.get("google_search_link") or "").strip() if isinstance(job.get("google_search_link"), str) else "",
        "smartstore_link": (job.get("smartstore_link") or "").strip() if isinstance(job.get("smartstore_link"), str) else "",
        "business_phone": (job.get("business_phone") or "").strip() if isinstance(job.get("business_phone"), str) else "",
        "business_email": (job.get("business_email") or "").strip() if isinstance(job.get("business_email"), str) else "",
        "business_address": (job.get("business_address") or "").strip() if isinstance(job.get("business_address"), str) else "",
        "homepage_link": (job.get("homepage_link") or "").strip() if isinstance(job.get("homepage_link"), str) else "",
    }


def export_leads(jobs: List[JobWithScore], output_path: str = "out/leads.xlsx") -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    normalized_jobs = [_normalize_job(job) for job in jobs]
    dataframe = pd.DataFrame(normalized_jobs, columns=OUTPUT_COLUMNS)
    dataframe = dataframe.sort_values(by="score", ascending=False, kind="stable")
    for wait_seconds in (0, 1, 2):
        try:
            if wait_seconds:
                time.sleep(wait_seconds)
            dataframe.to_excel(path, index=False)
            return path
        except PermissionError:
            continue

    fallback = path.parent / f"{path.stem}_latest{path.suffix}"
    dataframe.to_excel(fallback, index=False)
    return fallback
