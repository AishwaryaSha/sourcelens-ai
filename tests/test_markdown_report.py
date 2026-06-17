from app.agents.planner_agent import ResearchPlan
from app.agents.summarization_agent import ResearchSummary
from app.providers.search.base import SearchResult
from app.reports.markdown import generate_markdown_report


def test_markdown_report_contains_core_sections() -> None:
    report = generate_markdown_report(
        query="test query",
        plan=ResearchPlan(
            objective="test query",
            subquestions=["What is test query?"],
            search_queries=["test query"],
        ),
        search_results=[
            SearchResult(
                title="Example",
                url="https://example.com",
                snippet="Example snippet",
                rank=1,
            )
        ],
        summary=ResearchSummary(
            answer="A short answer.",
            key_points=["Point one"],
            limitations=["Limited evidence"],
            used_llm=False,
        ),
    )

    assert "# SourceLens AI Research Report" in report.content
    assert "## Research Plan" in report.content
    assert "## Sources" in report.content
    assert "https://example.com" in report.content
    assert report.filename.endswith(".md")
