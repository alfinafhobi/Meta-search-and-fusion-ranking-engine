# app.py
import time
import streamlit as st
from typing import List, Dict

from sources import get_results_from_sources
from fusion import rrf_fusion, combsum_fusion
from utils import deduplicate

# -----------------------------
# Streamlit Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Metasearch + Fusion Ranking Engine",
    layout="wide",
)

# -----------------------------
# Header
# -----------------------------
st.title("🔎 Metasearch + Fusion Ranking Engine")
st.caption(
    "Type a query, fetch results from multiple sources, and fuse them into a single ranked list."
)

# -----------------------------
# Sidebar Controls
# -----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    top_k = st.slider("Results per source", min_value=3, max_value=20, value=10, step=1)
    fusion_method = st.selectbox(
        "Fusion method",
        ["Reciprocal Rank Fusion (RRF)", "CombSUM"],
        help="Choose how to merge rankings from different sources."
    )
    rrf_k = st.number_input(
        "RRF parameter k",
        min_value=1,
        max_value=200,
        value=60,
        step=1,
        help="Only used for RRF. Larger k reduces the impact of rank positions."
    )
    do_dedupe = st.checkbox(
        "De-duplicate by canonical URL",
        value=True,
        help="Removes duplicate URLs across sources after fusion."
    )
    show_source_panels = st.checkbox(
        "Show per-source panels",
        value=True,
        help="Expanders listing raw results from each source."
    )
    show_snippets = st.checkbox(
        "Show snippets in fused list",
        value=True,
    )

# -----------------------------
# Main Controls
# -----------------------------
query = st.text_input("Enter your search query", value="glaucoma detection using OCT")
search_clicked = st.button("🔍 Search", type="primary", use_container_width=True)

# -----------------------------
# Helper UI Renderers
# -----------------------------
def render_result_item(item: Dict, rank_num: int, show_snip: bool = True):
    """Render a single result line nicely."""
    title = item.get("title") or "(Untitled)"
    url = item.get("url") or ""
    source = item.get("source") or "unknown"
    snippet = item.get("snippet") or ""
    score = item.get("score")

    col_rank, col_main, col_meta = st.columns([0.08, 0.72, 0.2])
    with col_rank:
        st.markdown(f"### {rank_num}")
    with col_main:
        st.markdown(f"**[{title}]({url})**")
        if show_snip and snippet:
            st.caption(snippet)
    with col_meta:
        st.write(f"**Source:** {source}")
        if score is not None:
            st.write(f"Score: `{score:.4f}`")

def render_source_panel(source_name: str, items: List[Dict]):
    with st.expander(f"📦 {source_name} — {len(items)} results", expanded=False):
        for i, r in enumerate(items, start=1):
            render_result_item(r, i, show_snip=True)
            st.divider()

# -----------------------------
# Search + Fusion Flow
# -----------------------------
if search_clicked or (query and "auto_run_once" not in st.session_state):
    # Optional: run once on initial load
    st.session_state["auto_run_once"] = True

    if not query.strip():
        st.warning("Please enter a query to search.")
        st.stop()

    # 1) Gather results from multiple sources
    t0 = time.time()
    ranked_lists = get_results_from_sources(query=query, top_k=top_k)
    fetch_time = time.time() - t0

    # Validate shape
    if not isinstance(ranked_lists, list) or not all(isinstance(lst, list) for lst in ranked_lists):
        st.error("`get_results_from_sources` must return a list of lists (one list per source).")
        st.stop()

    # Show raw source panels
    if show_source_panels:
        st.subheader("Per-source Results")
        # Group by source name (each list is already per source, but ensure label)
        for source_list in ranked_lists:
            source_label = source_list[0]["source"] if source_list else "unknown"
            render_source_panel(source_label, source_list)

    # 2) Fuse rankings
    st.subheader("🧮 Fused Results")
    with st.status("Fusing results...", expanded=False) as status:
        if fusion_method.startswith("Reciprocal"):
            fused = rrf_fusion(ranked_lists, k=rrf_k)
            status.update(label="Applied Reciprocal Rank Fusion", state="complete")
        else:
            fused = combsum_fusion(ranked_lists)
            status.update(label="Applied CombSUM", state="complete")

    # 3) De-duplicate if requested
    if do_dedupe:
        before = len(fused)
        fused = deduplicate(fused)
        after = len(fused)
        st.caption(f"De-duplicated fused list: {before} → {after}")

    # 4) Render fused list
    if fused:
        st.write(f"**Query:** `{query}` • **Sources:** {len(ranked_lists)} • **Fetch time:** {fetch_time:.2f}s")
        st.success(f"Showing top {len(fused)} fused results")
        for i, item in enumerate(fused, start=1):
            render_result_item(item, i, show_snip=show_snippets)
            st.divider()
    else:
        st.info("No results found from the selected sources.")

# -----------------------------
# Footer
# -----------------------------
with st.container():
    st.markdown("---")
    st.caption(
        "Tip: You can plug in real search adapters (Bing API, SerpAPI, local corpus) in `sources.py`. "
        "Add more fusion methods in `fusion.py` (e.g., CombMNZ, Borda)."
    )
