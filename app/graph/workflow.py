"""LangGraph workflow assembly for Phase 1."""

import logging
from typing import Any

from langgraph.graph import END, StateGraph

from app.agents.planner_agent import PlannerAgent
from app.agents.search_agent import SearchAgent
from app.agents.summarization_agent import SummarizationAgent
from app.graph.nodes.planner import create_planner_node
from app.graph.nodes.search import create_search_node
from app.graph.nodes.summarization import create_summarization_node
from app.graph.state import ResearchState

logger = logging.getLogger(__name__)


def build_research_workflow(
    planner_agent: PlannerAgent,
    search_agent: SearchAgent,
    summarization_agent: SummarizationAgent,
) -> Any:
    """Build the Phase 1 research workflow."""

    graph = StateGraph(ResearchState)
    graph.add_node("planner", create_planner_node(planner_agent))
    graph.add_node("search", create_search_node(search_agent))
    graph.add_node("summarization", create_summarization_node(summarization_agent))

    graph.set_entry_point("planner")
    graph.add_edge("planner", "search")
    graph.add_edge("search", "summarization")
    graph.add_edge("summarization", END)

    return graph.compile()


def run_research_workflow(
    query: str,
    planner_agent: PlannerAgent,
    search_agent: SearchAgent,
    summarization_agent: SummarizationAgent,
) -> ResearchState:
    """Run the Phase 1 workflow for a query."""

    logger.info("Starting research workflow")
    app = build_research_workflow(
        planner_agent=planner_agent,
        search_agent=search_agent,
        summarization_agent=summarization_agent,
    )
    result = app.invoke({"query": query, "warnings": [], "errors": []})
    logger.info("Research workflow completed")
    return result
