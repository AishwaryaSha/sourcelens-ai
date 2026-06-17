"""Summarization node."""

from app.agents.summarization_agent import SummarizationAgent
from app.graph.state import ResearchState


def create_summarization_node(agent: SummarizationAgent):
    """Create a LangGraph-compatible summarization node."""

    def summarization_node(state: ResearchState) -> ResearchState:
        summary = agent.summarize(
            query=state["query"],
            plan=state["plan"],
            search_results=state.get("search_results", []),
        )
        return {"summary": summary}

    return summarization_node
