"""Reusable checks for validating a startup-validation report.

Used by both the unit tests (tests/) and the domain runner
(scripts/run_domain_validation.py).  Pure standard library.
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from typing import Any
from urllib.parse import urlparse

PLACEHOLDER_HOSTS = {"example.com", "example.org", "example.net", "localhost"}

REPORT_SECTIONS = [
    "startup_idea",
    "market_analysis",
    "competitor_analysis",
    "swot_and_risks",
    "mvp_recommendation",
    "sources",
    "final_summary",
]


# --------------------------------------------------------------------------
# Output format
# --------------------------------------------------------------------------
def check_report_format(report: dict[str, Any]) -> list[str]:
    """Return a list of problems (empty list = format OK)."""
    problems: list[str] = []
    for key in REPORT_SECTIONS:
        if key not in report:
            problems.append(f"missing section: {key}")
    for key in ("market_analysis", "competitor_analysis",
                "swot_and_risks", "mvp_recommendation"):
        val = report.get(key)
        if not isinstance(val, dict) or not val:
            problems.append(f"{key} must be a non-empty object")
    if not isinstance(report.get("final_summary"), str) or \
            not report.get("final_summary", "").strip():
        problems.append("final_summary must be a non-empty string")
    if not isinstance(report.get("sources"), list):
        problems.append("sources must be a list")
    try:
        json.dumps(report)
    except (TypeError, ValueError) as exc:
        problems.append(f"report is not JSON serialisable: {exc}")
    return problems


# --------------------------------------------------------------------------
# Source URLs
# --------------------------------------------------------------------------
def is_valid_http_url(url: str) -> bool:
    """Syntax check only: http(s) scheme and a host that contains a dot."""
    try:
        p = urlparse((url or "").strip())
    except ValueError:
        return False
    return p.scheme in ("http", "https") and bool(p.netloc) and "." in p.netloc


def is_placeholder_url(url: str) -> bool:
    host = (urlparse(url or "").hostname or "").lower()
    return host in PLACEHOLDER_HOSTS or host.endswith(".example.com")


def check_sources(sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Syntax / duplicate / placeholder checks on the sources list."""
    invalid = [s.get("url", "") for s in sources if not is_valid_http_url(s.get("url", ""))]
    placeholders = [s["url"] for s in sources if is_placeholder_url(s.get("url", ""))]
    urls = [s.get("url", "") for s in sources]
    duplicates = sorted({u for u in urls if urls.count(u) > 1})
    empty_content = [s.get("url", "") for s in sources if not (s.get("content") or "").strip()]
    return {
        "count": len(sources),
        "invalid_urls": invalid,
        "placeholder_urls": placeholders,
        "duplicate_urls": duplicates,
        "empty_content": empty_content,
    }


def check_url_reachable(url: str, timeout: float = 8.0) -> tuple[bool, str]:
    """Live reachability check (needs internet). Returns (ok, detail)."""
    req = urllib.request.Request(
        url, method="GET", headers={"User-Agent": "Mozilla/5.0 (validator-test)"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return 200 <= resp.status < 400, f"HTTP {resp.status}"
    except urllib.error.HTTPError as exc:
        # 403/429 usually means the site blocks bots but the URL exists.
        return exc.code in (401, 403, 429), f"HTTP {exc.code}"
    except Exception as exc:  # DNS failure, timeout, TLS error ...
        return False, f"{type(exc).__name__}: {exc}"


# --------------------------------------------------------------------------
# Relevance and grounding (heuristics - they flag items for human review)
# --------------------------------------------------------------------------
def _text(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False) if not isinstance(obj, str) else obj


def relevance_score(sources: list[dict[str, Any]], keywords: list[str]) -> float:
    """Share of sources whose title/content mention at least one keyword."""
    if not sources:
        return 0.0
    kws = [k.lower() for k in keywords]
    hits = 0
    for s in sources:
        blob = f"{s.get('title', '')} {s.get('content', '')}".lower()
        if any(k in blob for k in kws):
            hits += 1
    return hits / len(sources)


_NUMBER_RE = re.compile(
    r"(?:(?:₹|rs\.?|inr|\$|usd)\s*)?\d[\d,]*(?:\.\d+)?\s*"
    r"(?:%|percent|crore|lakh|million|billion|bn|cr|k)?",
    re.IGNORECASE,
)


def _norm_number(tok: str) -> str:
    return re.sub(r"[^\d.%]", "", tok.lower())


def ungrounded_statistics(analysis: Any, sources: list[dict[str, Any]]) -> list[str]:
    """Statistics in the analysis that appear in no source.

    Only 'statistic-like' numbers are checked (have %, a currency or a
    magnitude word such as crore/million/billion). Bare small integers like
    '3 risks' or '10 interviews' are ignored.
    """
    src_blob = " ".join(f"{s.get('title','')} {s.get('content','')}" for s in sources).lower()
    src_numbers = {_norm_number(m.group(0)) for m in _NUMBER_RE.finditer(src_blob)}
    flagged = []
    for m in _NUMBER_RE.finditer(_text(analysis)):
        tok = m.group(0).strip()
        statistic_like = bool(
            re.search(r"%|percent|crore|lakh|million|billion|bn|₹|\$|inr|usd|rs", tok, re.I)
        )
        if not statistic_like:
            continue
        if _norm_number(tok) not in src_numbers and tok.lower() not in src_blob:
            flagged.append(tok)
    return sorted(set(flagged))


_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "in", "on", "for", "to", "with", "this",
    "that", "these", "those", "india", "indian", "market", "direct", "indirect",
    "competitors", "competitor", "key", "risk", "risks", "swot", "mvp", "strengths",
    "weaknesses", "opportunities", "threats", "however", "while", "also", "there",
    "their", "they", "it", "its", "is", "are", "be", "can", "may", "should", "not",
    "no", "yes", "if", "as", "at", "by", "from", "one", "two", "three", "customer",
    "customers", "startup", "product", "platform", "app", "ai", "based", "such",
    "some", "many", "most", "other", "another", "company", "companies", "users",
    "user", "data", "analysis", "research", "evidence", "assumption", "assumptions",
    "demand", "pricing", "price", "growth", "trend", "trends", "positioning",
    "differentiation", "uncertainties", "uncertainty", "recommended", "next", "steps",
    "findings", "summary", "executive", "mitigation", "mitigations", "known", "facts",
    "hypotheses", "first", "second", "third", "overall", "note", "based", "source",
    "sources", "unknown", "low", "high", "medium", "mvp", "unclear",
}


def ungrounded_company_names(analysis: Any, sources: list[dict[str, Any]],
                             idea_name: str = "") -> list[str]:
    """Capitalised names in the competitor analysis that no source mentions.

    Heuristic: a name that is not in the research text may be an invented
    competitor. Results need human review (the LLM may legitimately know a
    company the search missed), but a long list is a red flag.
    """
    src_blob = " ".join(f"{s.get('title','')} {s.get('content','')}" for s in sources).lower()
    text = _text(analysis)
    # Capitalised tokens (allow internal caps / apostrophes: BYJU'S, PhysicsWallah)
    candidates = re.findall(r"\b[A-Z][A-Za-z0-9'&]{2,}(?:\s+[A-Z][A-Za-z0-9'&]{2,})?", text)
    flagged = []
    for c in candidates:
        key = c.strip(" .").lower()
        words = key.split()
        if not key or all(w in _STOPWORDS for w in words):
            continue
        if key in _STOPWORDS or (idea_name and key == idea_name.lower()):
            continue
        if key in src_blob or all(w in src_blob for w in words):
            continue
        # Sentence-initial ordinary words are not company names.
        if len(words) == 1 and key in _STOPWORDS:
            continue
        flagged.append(c.strip(" ."))
    return sorted(set(flagged))
