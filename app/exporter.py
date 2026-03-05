from pathlib import Path
from typing import Dict, List, Optional

import pandas as pd


JobWithScore = Dict[str, str | int | None]
OUTPUT_COLUMNS = ["score", "company", "title", "location", "summary", "url"]

DOMAIN_KEYWORDS = (
    "쇼핑몰",
    "스마트스토어",
    "쿠팡",
    "오픈마켓",
    "주문관리",
    "출고관리",
    "발주관리",
)

SKILL_KEYWORDS = (
    "엑셀",
    "리포트",
    "정산",
    "데이터",
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
        "score": job.get("score", 0),
        "company": (job.get("company") or "").strip(),
        "title": title,
        "location": job.get("location"),
        "summary": build_summary_from_title(title),
        "url": (job.get("url") or "").strip(),
    }


def export_leads(jobs: List[JobWithScore], output_path: str = "out/leads.xlsx") -> Path:
    """Export lead data to an Excel file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    normalized_jobs = [_normalize_job(job) for job in jobs]
    dataframe = pd.DataFrame(normalized_jobs, columns=OUTPUT_COLUMNS)
    dataframe.to_excel(path, index=False)
    return path
