import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.collector import collect_jobs
from app.exporter import export_leads
from app.filter import filter_jobs
from app.scoring import calculate_score


Job = Dict[str, Optional[str]]


def _get_logger() -> logging.Logger:
    logger = logging.getLogger("pipeline")
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


def _deduplicate_jobs(jobs: List[Job]) -> List[Job]:
    deduped: List[Job] = []
    seen_keys: Set[Tuple[str, str, str]] = set()

    for job in jobs:
        url = (job.get("url") or "").strip()
        company = (job.get("company") or "").strip()
        title = (job.get("title") or "").strip()

        key = (url, company, title)
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(job)

    return deduped


def run() -> None:
    logger = _get_logger()

    try:
        jobs = collect_jobs()
        logger.info("수집 후 건수: %s", len(jobs))
    except Exception:
        logger.exception("collect_jobs 단계 실패")
        jobs = []

    try:
        deduped_jobs = _deduplicate_jobs(jobs)
        logger.info("중복 제거 후 건수: %s", len(deduped_jobs))
    except Exception:
        logger.exception("중복 제거 단계 실패")
        deduped_jobs = jobs

    try:
        filtered_jobs = filter_jobs(deduped_jobs)
        logger.info("필터링 후 건수: %s", len(filtered_jobs))
    except Exception:
        logger.exception("filter_jobs 단계 실패")
        filtered_jobs = []

    qualified_jobs = []
    for job in filtered_jobs:
        try:
            score = calculate_score(job)
            if score < 5:
                continue
            qualified_jobs.append(
                {
                    "score": score,
                    "company": job.get("company") or "",
                    "title": job.get("title") or "",
                    "location": job.get("location"),
                    "url": job.get("url") or "",
                }
            )
        except Exception:
            logger.exception("점수 계산 실패: title=%s", job.get("title"))

    logger.info("점수 기준 통과 건수: %s", len(qualified_jobs))

    try:
        output_file = export_leads(qualified_jobs)
        logger.info("엑셀 저장 완료: %s", output_file)
        print(f"Saved {len(qualified_jobs)} leads to {output_file}")
    except Exception:
        logger.exception("export_leads 단계 실패")
        print("Saved 0 leads to out/leads.xlsx")
