# fusion.py
"""
Fusion ranking algorithms for Metasearch:
- Reciprocal Rank Fusion (RRF)
- CombSUM (with 1/rank fallback when score is None)

All functions accept a list of ranked lists (one per source), where each
result item is a dict with keys:
  title, url, snippet, rank (1-based), source, score (float|None)

They return a single fused list with the same schema. The 'score' field in
the fused list is set to the fused score; 'rank' is reassigned (1-based).
"""

from __future__ import annotations
from typing import Dict, List, Tuple


Result = Dict[str, object]


def rrf_fusion(ranked_lists: List[List[Result]], k: int = 60) -> List[Result]:
    """
    Reciprocal Rank Fusion:
      fused_score(doc) = sum_over_sources( 1 / (k + rank_in_that_source) )

    Args:
        ranked_lists: list of per-source ranked lists
        k: smoothing constant; higher k dampens the influence of top ranks

    Returns:
        Fused, re-ranked list of results (dicts). 'score' is the fused score.
    """
    fused_scores: Dict[str, float] = {}
    representative: Dict[str, Result] = {}

    for per_source in ranked_lists:
        for item in per_source:
            url = str(item.get("url", ""))
            rank = int(item.get("rank", 999999))  # fallback safety
            if not url:
                continue
            fused_scores[url] = fused_scores.get(url, 0.0) + 1.0 / (k + rank)
            # keep a representative (first seen is fine; we're replacing score later)
            if url not in representative:
                representative[url] = item

    # Sort by fused score desc
    ordered: List[Tuple[str, float]] = sorted(
        fused_scores.items(), key=lambda x: x[1], reverse=True
    )

    fused: List[Result] = []
    for i, (url, score) in enumerate(ordered, start=1):
        rep = representative[url].copy()
        rep["rank"] = i
        rep["source"] = "fused"
        rep["score"] = float(score)
        fused.append(rep)

    return fused


def combsum_fusion(ranked_lists: List[List[Result]]) -> List[Result]:
    """
    CombSUM fusion over normalized or raw scores.
    If a result has no score (None), we fallback to 1/rank as a pseudo-score.

    Returns:
        Fused, re-ranked list with 'score' = CombSUM score.
    """
    sums: Dict[str, float] = {}
    representative: Dict[str, Result] = {}

    for per_source in ranked_lists:
        for item in per_source:
            url = str(item.get("url", ""))
            if not url:
                continue

            raw_score = item.get("score", None)
            rank = int(item.get("rank", 999999))
            # Fallback when score is None: inverse-rank (simple, effective)
            contrib = (1.0 / max(rank, 1)) if raw_score is None else float(raw_score)

            sums[url] = sums.get(url, 0.0) + contrib
            if url not in representative:
                representative[url] = item

    ordered = sorted(sums.items(), key=lambda x: x[1], reverse=True)

    fused: List[Result] = []
    for i, (url, score) in enumerate(ordered, start=1):
        rep = representative[url].copy()
        rep["rank"] = i
        rep["source"] = "fused"
        rep["score"] = float(score)
        fused.append(rep)

    return fused
