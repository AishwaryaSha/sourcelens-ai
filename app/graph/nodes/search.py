"""Search node."""

from app.agents.search_agent import SearchAgent
from app.graph.state import ResearchState


def create_search_node(agent: SearchAgent):
    """Create a LangGraph-compatible search node."""

    def search_node(state: ResearchState) -> ResearchState:
        results = agent.search(state["plan"])
        return {"search_results": results}

    return search_node
