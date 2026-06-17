from app.agents.planner_agent import ResearchPlan
from app.agents.summarization_agent import ResearchSummary
from app.graph.workflow import run_research_workflow
from app.providers.search.base import SearchResult


class FakePlannerAgent:
    def plan(self, query: str) -> ResearchPlan:
        return ResearchPlan(
            objective=query,
            subquestions=["Question one"],
            search_queries=["query one"],
        )


class FakeSearchAgent:
    def search(self, plan: ResearchPlan) -> list[SearchResult]:
        return [
            SearchResult(
                title="Result",
                url="https://example.com",
                snippet="Snippet",
                rank=1,
            )
        ]


class FakeSummarizationAgent:
    def summarize(
        self,
        query: str,
        plan: ResearchPlan,
        search_results: list[SearchResult],
    ) -> ResearchSummary:
        return ResearchSummary(
            answer=f"Answer for {query}",
            key_points=["Key point"],
            limitations=["Limitation"],
            used_llm=False,
        )


def test_workflow_runs_phase_1_nodes() -> None:
    state = run_research_workflow(
        query="sample query",
        planner_agent=FakePlannerAgent(),
        search_agent=FakeSearchAgent(),
        summarization_agent=FakeSummarizationAgent(),
    )

    assert state["plan"].objective == "sample query"
    assert len(state["search_results"]) == 1
    assert state["summary"].answer == "Answer for sample query"
