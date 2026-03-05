import logging
from typing import Dict, List, Optional, Tuple

import requests

from app.contact_finder import find_company_contacts, make_discovery_links


Lead = Dict[str, Optional[str] | int]


def _normalize_company_key(company: str) -> str:
    return " ".join(company.lower().split())


def _empty_contact_payload(company: str) -> Dict[str, Optional[str]]:
    links = make_discovery_links(company)
    return {
        "address": None,
        "phone": None,
        "email": None,
        "homepage": None,
        "naver_map_link": links["naver_map_link"],
        "google_search_link": links["google_search_link"],
        "smartstore_link": links["smartstore_link"],
        "business_phone": None,
        "business_email": None,
        "business_address": None,
        "homepage_link": None,
    }


def _to_business_fields(contact: Dict[str, Optional[str]]) -> Dict[str, Optional[str]]:
    homepage = contact.get("homepage")
    return {
        "address": contact.get("address"),
        "phone": contact.get("phone"),
        "email": contact.get("email"),
        "homepage": homepage,
        "naver_map_link": contact.get("naver_map_link"),
        "google_search_link": contact.get("google_search_link"),
        "smartstore_link": contact.get("smartstore_link"),
        "business_phone": contact.get("phone"),
        "business_email": contact.get("email"),
        "business_address": contact.get("address"),
        "homepage_link": homepage,
    }


def enrich_jobs(jobs: List[Lead], logger: Optional[logging.Logger] = None) -> List[Lead]:
    cache: Dict[Tuple[str, str], Dict[str, Optional[str]]] = {}
    enriched: List[Lead] = []

    session = requests.Session()
    try:
        for job in jobs:
            company = (job.get("company") or "").strip() if isinstance(job.get("company"), str) else ""
            location = (job.get("location") or "").strip() if isinstance(job.get("location"), str) else ""

            if not company:
                payload = _empty_contact_payload(company="unknown")
                enriched.append({**job, **payload})
                continue

            key = (_normalize_company_key(company), _normalize_company_key(location))
            if key not in cache:
                try:
                    contact = find_company_contacts(company=company, location=location, session=session)
                    cache[key] = _to_business_fields(contact)
                except Exception:
                    if logger:
                        logger.exception("contact lookup failed: company=%s", company)
                    cache[key] = _empty_contact_payload(company)

            enriched.append({**job, **cache[key]})

        if logger:
            logger.info("Contact enrichment cache size: %s", len(cache))

        return enriched
    finally:
        session.close()