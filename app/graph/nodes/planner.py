"""Planner node."""

from app.agents.planner_agent import PlannerAgent
from app.graph.state import ResearchState


def create_planner_node(agent: PlannerAgent):
    """Create a LangGraph-compatible planner node."""

    def planner_node(state: ResearchState) -> ResearchState:
        plan = agent.plan(state["query"])
        return {"plan": plan}

    return planner_node
