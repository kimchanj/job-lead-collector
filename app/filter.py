from typing import Dict, List, Optional


Job = Dict[str, Optional[str]]

INCLUDE_KEYWORDS = (
    "엑셀",
    "주문관리",
    "쇼핑몰",
    "리포트",
    "데이터",
)

EXCLUDE_KEYWORDS = (
    "카페",
    "식당",
    "주방",
    "미용",
    "운전",
    "생산직",
)


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def filter_jobs(jobs: List[Job]) -> List[Job]:
    filtered_jobs: List[Job] = []

    for job in jobs:
        title = job.get("title") or ""
        description = job.get("description") or ""
        company = job.get("company") or ""
        haystack = f"{title} {description} {company}"

        if not haystack.strip():
            continue
        if _contains_any(haystack, EXCLUDE_KEYWORDS):
            continue
        if _contains_any(haystack, INCLUDE_KEYWORDS):
            filtered_jobs.append(job)

    return filtered_jobs
