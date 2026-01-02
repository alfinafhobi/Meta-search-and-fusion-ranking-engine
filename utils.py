# utils.py
"""
Utilities:
- URL canonicalization (for robust de-duplication)
- Result de-duplication by canonical URL
- Optional score normalization helpers (min-max)

All functions operate on lists of dict results matching the schema used in the app.
"""

from __future__ import annotations
from typing import Dict, List, Optional
import re

Result = Dict[str, object]


def canonicalize_url(url: str) -> str:
    """
    Create a canonical form of a URL for duplicate detection:
      - lowercased
      - strip scheme (http/https) and leading www.
      - drop query params and fragments
      - remove trailing slash
    """
    u = url.strip().lower()
    u = re.sub(r"^https?://(www\.)?", "", u)
    u = re.sub(r"[#?].*$", "", u)
    if u.endswith("/"):
        u = u[:-1]
    return u


def deduplicate(results: List[Result]) -> List[Result]:
    """
    Remove duplicate items by canonical URL, preserving first occurrence order.
    """
    seen = set()
    unique: List[Result] = []
    for r in results:
        url = str(r.get("url", ""))
        if not url:
            # keep empty-url items once (rare), using object id as key
            key = f"__empty__:{id(r)}"
        else:
            key = canonicalize_url(url)
        if key in seen:
            continue
        seen.add(key)
        unique.append(r)
    # Reassign ranks after dedupe to keep list consistent
    for i, r in enumerate(unique, start=1):
        r["rank"] = i
    return unique


def minmax_normalize_scores(results: List[Result]) -> List[Result]:
    """
    In-place min-max normalization of 'score' across a single list of results.
    If all scores are None or identical, leaves them as-is (or sets to 1.0 if identical).
    """
    scores = [float(r["score"]) for r in results if r.get("score") is not None]
    if not scores:
        return results
    lo, hi = min(scores), max(scores)
    if hi == lo:
        for r in results:
            if r.get("score") is not None:
                r["score"] = 1.0
        return results
    rng = hi - lo
    for r in results:
        if r.get("score") is not None:
            r["score"] = (float(r["score"]) - lo) / rng
    return results
