import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from app.collector import collect_jobs
from app.exporter import export_leads
from app.filter import filter_jobs
from app.lead_enricher import enrich_jobs
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
        key = (
            (job.get("url") or "").strip(),
            (job.get("company") or "").strip(),
            (job.get("title") or "").strip(),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(job)

    return deduped


def run() -> None:
    logger = _get_logger()

    try:
        jobs = collect_jobs()
        logger.info("Collected jobs: %s", len(jobs))
    except Exception:
        logger.exception("collect_jobs failed")
        jobs = []

    try:
        deduped_jobs = _deduplicate_jobs(jobs)
        logger.info("Deduplicated jobs: %s", len(deduped_jobs))
    except Exception:
        logger.exception("deduplication failed")
        deduped_jobs = jobs

    try:
        filtered_jobs = filter_jobs(deduped_jobs)
        logger.info("Filtered jobs: %s", len(filtered_jobs))
    except Exception:
        logger.exception("filter_jobs failed")
        filtered_jobs = []

    qualified_jobs: List[Dict[str, Optional[str] | int]] = []
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
            logger.exception("calculate_score failed: title=%s", job.get("title"))

    logger.info("Qualified jobs (score>=5): %s", len(qualified_jobs))

    try:
        enriched_jobs = enrich_jobs(qualified_jobs, logger=logger)
        logger.info("Enriched jobs: %s", len(enriched_jobs))
    except Exception:
        logger.exception("enrich_jobs failed; exporting without contact enrichment")
        enriched_jobs = qualified_jobs

    try:
        output_file = export_leads(enriched_jobs)
        logger.info("Excel exported: %s", output_file)
        print(f"Saved {len(enriched_jobs)} leads to {output_file}")
    except Exception:
        logger.exception("export_leads failed")
        print("Saved 0 leads to out/leads.xlsx")