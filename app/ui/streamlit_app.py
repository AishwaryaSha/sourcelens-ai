"""Streamlit user interface for SourceLens AI."""

import logging

import streamlit as st

from app.core.config import get_settings
from app.core.exceptions import SourceLensError
from app.core.logging import configure_logging
from app.services.research_service import ResearchService
from app.services.research_service import ResearchResult
from app.ui.components.sidebar import render_sidebar

logger = logging.getLogger(__name__)


def render_app() -> None:
    """Render the Streamlit application."""

    base_settings = get_settings()
    configure_logging(base_settings)

    st.set_page_config(
        page_title=base_settings.app_name,
        page_icon="SL",
        layout="wide",
    )

    options = render_sidebar(base_settings)
    settings = base_settings.model_copy(
        update={
            "ollama_model": options["ollama_model"],
            "search_max_results": options["search_max_results"],
        }
    )

    st.title("SourceLens AI")
    st.caption("Multi-agent research assistant - Phase 1")

    query = st.text_area(
        "Research question",
        value = st.session_state.get("research_query", ""),
        placeholder="Example: What are the benefits and risks of using local LLMs for enterprise knowledge assistants?",
        height=120,
    )

    run_clicked = st.button("Run research", type="primary")

    if run_clicked:
        service = ResearchService(settings)
        try:
            with st.status("Running research workflow...", expanded=True) as status:
                st.write("Planning research approach")
                st.write("Searching the web")
                st.write("Summarizing evidence")
                result = service.run(query)
                st.session_state["research_result"] = result
                st.session_state["research_query"] = query
                status.update(label="Research complete", state="complete")
        except SourceLensError as exc:
            logger.warning("User-facing research error: %s", exc)
            st.error(str(exc))
            return
        except Exception as exc:
            logger.exception("Unexpected application error")
            st.error(f"Unexpected error: {exc}")
            return

        if "research_result" in st.session_state:
            _render_result(st.session_state["research_result"])


def _render_result(result: ResearchResult) -> None:
    st.subheader("Answer")
    st.markdown(result.summary.answer)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.subheader("Research Plan")
        st.markdown("**Subquestions**")
        for item in result.plan.subquestions:
            st.markdown(f"- {item}")
        st.markdown("**Search queries**")
        for item in result.plan.search_queries:
            st.markdown(f"- {item}")

    with col2:
        st.subheader("Key Points")
        if result.summary.key_points:
            for point in result.summary.key_points:
                st.markdown(f"- {point}")
        else:
            st.info("No key points generated.")

    st.subheader("Sources")
    if result.search_results:
        for source in result.search_results:
            st.markdown(f"**[{source.rank}] [{source.title}]({source.url})**")
            if source.snippet:
                st.caption(source.snippet)
    else:
        st.info("No sources were retrieved.")

    st.subheader("Markdown Report")
    st.download_button(
        label="Download markdown report",
        data=result.report.content,
        file_name=result.report.filename,
        mime="text/markdown",
    )
    st.markdown(result.report.content)
