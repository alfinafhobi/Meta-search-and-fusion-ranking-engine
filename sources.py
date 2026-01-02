# sources.py
"""
Metasearch Sources (SerpApi multi-engine using ONE key)
- SerpApi (Google, Bing, DuckDuckGo, Yahoo, ...)
- (Optional) Google CSE (kept for comparison)
- Mock fallback

Each result item: {title, url, snippet, rank, source, score}
"""

from typing import List, Dict
import requests

from config import (
    ENABLED_ENGINES,
    SERPAPI_KEY,           # one key for all SerpApi engines
    GOOGLE_CSE_API_KEY,    # optional
    GOOGLE_CSE_CX,         # optional
)

Result = Dict[str, object]


# =========================
# Dispatcher
# =========================
def get_results_from_sources(query: str, top_k: int = 10) -> List[List[Result]]:
    """
    Build a list of per-source result lists based on ENABLED_ENGINES.
    Supported engine keys:
      - "serpapi_google"
      - "serpapi_bing"
      - "serpapi_duckduckgo"
      - "serpapi_yahoo"
      - "google_cse"   (optional, official Google API)
    """
    bags: List[List[Result]] = []
    used_any = False

    # ---- SerpApi engines (one key, many backends) ----
    serpapi_map = {
        "serpapi_google":    "google",
        "serpapi_bing":      "bing",
        "serpapi_duckduckgo":"duckduckgo",
        "serpapi_yahoo":     "yahoo",
        # You can add more supported SerpApi engines here:
        # "serpapi_yandex": "yandex", "serpapi_baidu": "baidu", etc.
    }

    if SERPAPI_KEY:
        for cfg_name, engine_name in serpapi_map.items():
            if cfg_name in ENABLED_ENGINES:
                try:
                    print(f"[INFO] Fetching from SerpApi/{engine_name} ...")
                    bags.append(serpapi_search(query, engine=engine_name, top_k=top_k))
                    used_any = True
                except Exception as e:
                    print(f"[WARN] serpapi_search({engine_name}) failed:", e)

    # ---- Optional: Google CSE (official) ----
    if "google_cse" in ENABLED_ENGINES and GOOGLE_CSE_API_KEY and GOOGLE_CSE_CX:
        try:
            print("[INFO] Fetching from Google CSE ...")
            bags.append(google_cse_search(query, top_k=top_k))
            used_any = True
        except Exception as e:
            print("[WARN] google_cse_search failed:", e)

    # ---- Fallback if nothing worked ----
    if not used_any:
        print("[WARN] No engines available. Using mock data.")
        bags.append(_mock_source("Alpha", query, top_k, kind="guide", decay_shift=2.0))

    return bags


# =========================
# SerpApi generic adapter
# =========================
def serpapi_search(query: str, engine: str, top_k: int = 10) -> List[Result]:
    """
    Generic SerpApi adapter. One key, many engines:
      engine in {"google", "bing", "duckduckgo", "yahoo", ...}
    Docs: https://serpapi.com/
    """
    if not SERPAPI_KEY:
        raise RuntimeError("SERPAPI_KEY not set.")

    # SerpApi expects different endpoints/params per engine; most support this base endpoint.
    # For engines that require a different endpoint, swap URL accordingly.
    url = "https://serpapi.com/search.json"
    params = {
        "engine": engine,
        "q": query,
        "api_key": SERPAPI_KEY,
        # Google supports 'num'; Bing/DDG/Yahoo may ignore or limit count server-side.
        "num": top_k,
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    data = r.json()

    # Normalize per engine: try common containers first, then fallbacks.
    candidates = (
        data.get("organic_results")
        or data.get("results")
        or data.get("items")
        or []
    )

    results: List[Result] = []
    for i, it in enumerate(candidates[:top_k], start=1):
        title = it.get("title") or it.get("name") or "(No title)"
        url_  = it.get("link") or it.get("url") or ""
        snippet = it.get("snippet") or it.get("description") or ""
        results.append({
            "title": title,
            "url": url_,
            "snippet": snippet,
            "rank": i,
            "source": f"SerpApi/{engine.capitalize()}",
            "score": None,
        })
    return results


# =========================
# Google CSE (optional)
# =========================
def google_cse_search(query: str, top_k: int = 10) -> List[Result]:
    if top_k <= 0:
        return []
    results: List[Result] = []
    remaining = top_k
    start = 1
    while remaining > 0:
        num = min(10, remaining)
        params = {
            "key": GOOGLE_CSE_API_KEY,
            "cx": GOOGLE_CSE_CX,
            "q": query,
            "num": num,
            "start": start,
        }
        r = requests.get("https://www.googleapis.com/customsearch/v1", params=params, timeout=20)
        r.raise_for_status()
        data = r.json()
        items = data.get("items") or []
        for it in items:
            results.append({
                "title": it.get("title") or "(No title)",
                "url": it.get("link") or "",
                "snippet": it.get("snippet") or (it.get("htmlSnippet") or ""),
                "rank": len(results) + 1,
                "source": "Google CSE",
                "score": None,
            })
        got = len(items)
        if got == 0:
            break
        remaining -= got
        start += got
        if start > 100:
            break
    return results


# =========================
# Mock fallback
# =========================
def _mock_source(name: str, query: str, top_k: int, kind: str, decay_shift: float):
    bag: List[Result] = []
    for i in range(1, top_k + 1):
        url = f"https://example.com/{name.lower()}/{kind}-{i}"
        score = 1.0 / (i + decay_shift)
        bag.append({
            "title": f"{query.title()} — {name} {kind.capitalize()} #{i}",
            "url": url,
            "snippet": f"{name} mock {kind} result {i} for '{query}'.",
            "rank": i,
            "source": name,
            "score": score,
        })
    return bag

