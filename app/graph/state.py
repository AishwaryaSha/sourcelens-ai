"""State definitions for the Phase 1 LangGraph workflow."""

from typing import TypedDict

from app.agents.planner_agent import ResearchPlan
from app.agents.summarization_agent import ResearchSummary
from app.providers.search.base import SearchResult


class ResearchState(TypedDict, total=False):
    """Shared state passed between LangGraph nodes."""

    query: str
    plan: ResearchPlan
    search_results: list[SearchResult]
    summary: ResearchSummary
    warnings: list[str]
    errors: list[str]
