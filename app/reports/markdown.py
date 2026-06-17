"""Markdown report generation."""

from dataclasses import dataclass
from datetime import datetime, timezone

from app.agents.planner_agent import ResearchPlan
from app.agents.summarization_agent import ResearchSummary
from app.providers.search.base import SearchResult


@dataclass(frozen=True)
class MarkdownReport:
    """Generated markdown report."""

    content: str
    filename: str


def generate_markdown_report(
    query: str,
    plan: ResearchPlan,
    search_results: list[SearchResult],
    summary: ResearchSummary,
) -> MarkdownReport:
    """Create a markdown report from workflow outputs."""

    generated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    filename = _report_filename(query)

    lines = [
        "# SourceLens AI Research Report",
        "",
        f"**Generated:** {generated_at}",
        f"**Query:** {query}",
        f"**Summary mode:** {'Ollama-assisted' if summary.used_llm else 'Fallback extractive'}",
        "",
        "## Research Plan",
        "",
        f"**Objective:** {plan.objective}",
        "",
        "### Subquestions",
        "",
        *[f"- {item}" for item in plan.subquestions],
        "",
        "### Search Queries",
        "",
        *[f"- {item}" for item in plan.search_queries],
        "",
        "## Answer",
        "",
        summary.answer,
        "",
        "## Key Points",
        "",
        *([f"- {item}" for item in summary.key_points] or ["- No key points generated."]),
        "",
        "## Sources",
        "",
        *(_format_sources(search_results) or ["- No sources retrieved."]),
        "",
        "## Limitations",
        "",
        *([f"- {item}" for item in summary.limitations] or ["- Phase 1 does not perform claim verification."]),
        "",
    ]

    return MarkdownReport(content="\n".join(lines), filename=filename)


def _format_sources(search_results: list[SearchResult]) -> list[str]:
    return [
        f"- [{result.rank}] [{result.title}]({result.url})"
        + (f" - {result.snippet}" if result.snippet else "")
        for result in search_results
    ]


def _report_filename(query: str) -> str:
    slug = "".join(
        char.lower() if char.isalnum() else "-"
        for char in query.strip()
    ).strip("-")
    compact_slug = "-".join(part for part in slug.split("-") if part)
    return f"sourcelens-report-{compact_slug[:48] or 'research'}.md"
