from typing import Dict, Optional


Job = Dict[str, Optional[str]]

SHOPPING_KEYWORDS = ("쇼핑몰", "오픈마켓", "스마트스토어", "쿠팡")
ORDER_KEYWORDS = ("주문관리", "출고관리", "발주관리")
AUTOMATION_KEYWORDS = ("엑셀", "리포트", "정산", "데이터")


def _contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def calculate_score(job: Job) -> int:
    title = job.get("title") or ""
    description = job.get("description") or ""
    company = job.get("company") or ""
    haystack = f"{title} {description} {company}"

    score = 0
    if _contains_any(haystack, SHOPPING_KEYWORDS):
        score += 5
    if _contains_any(haystack, ORDER_KEYWORDS):
        score += 4
    if _contains_any(haystack, AUTOMATION_KEYWORDS):
        score += 3

    return score
