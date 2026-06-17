"""Sidebar controls for Streamlit."""

import streamlit as st

from app.core.config import Settings


def render_sidebar(settings: Settings) -> dict[str, object]:
    """Render sidebar controls and return runtime options."""

    st.sidebar.title("SourceLens AI")
    st.sidebar.caption("Phase 1: web research with local-first summarization.")

    model = st.sidebar.text_input(
        "Ollama model",
        value=settings.ollama_model,
        help="Example: llama3.1, mistral, phi3",
    )
    max_results = st.sidebar.slider(
        "Search results",
        min_value=1,
        max_value=10,
        value=settings.search_max_results,
    )

    st.sidebar.divider()
    st.sidebar.markdown("**Workflow**")
    st.sidebar.markdown("Planner -> Search -> Summarization -> Report")
    st.sidebar.markdown("Verification and RAG are planned for later phases.")

    return {
        "ollama_model": model,
        "search_max_results": max_results,
    }
