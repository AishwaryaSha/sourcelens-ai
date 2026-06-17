"""Research orchestration service."""

import logging
from dataclasses import dataclass

from app.agents.planner_agent import PlannerAgent, ResearchPlan
from app.agents.search_agent import SearchAgent
from app.agents.summarization_agent import ResearchSummary, SummarizationAgent
from app.core.config import Settings
from app.core.exceptions import SourceLensError, WorkflowError
from app.graph.workflow import run_research_workflow
from app.providers.llm.ollama_provider import OllamaProvider
from app.providers.search.base import SearchResult
from app.providers.search.federated_provider import FederatedSearchProvider
from app.providers.search.openalex_provider import OpenAlexSearchProvider
from app.providers.search.wikipedia_provider import WikipediaSearchProvider
from app.reports.markdown import MarkdownReport, generate_markdown_report
from app.utils.text import normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchResult:
    """Complete Phase 1 research result."""

    query: str
    plan: ResearchPlan
    search_results: list[SearchResult]
    summary: ResearchSummary
    report: MarkdownReport


class ResearchService:
    """Application service used by the Streamlit UI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def run(self, query: str) -> ResearchResult:
        """Run the full Phase 1 research workflow and generate a report."""

        cleaned_query = normalize_whitespace(query)
        if not cleaned_query:
            raise WorkflowError("Please enter a research question.")

        ollama_provider = OllamaProvider(self._settings)
        planner_agent = PlannerAgent(llm_provider=ollama_provider)
        search_agent = SearchAgent(
            provider=FederatedSearchProvider(
                providers=[
                    WikipediaSearchProvider(self._settings),
                    OpenAlexSearchProvider(self._settings),
                ]
            ),
            settings=self._settings,
        )
        summarization_agent = SummarizationAgent(llm_provider=ollama_provider)

        try:
            state = run_research_workflow(
                query=cleaned_query,
                planner_agent=planner_agent,
                search_agent=search_agent,
                summarization_agent=summarization_agent,
            )
        except SourceLensError:
            raise
        except Exception as exc:
            logger.exception("Research workflow failed")
            raise WorkflowError(f"Research workflow failed: {exc}") from exc

        plan = state["plan"]
        search_results = state.get("search_results", [])
        summary = state["summary"]
        report = generate_markdown_report(
            query=cleaned_query,
            plan=plan,
            search_results=search_results,
            summary=summary,
        )

        return ResearchResult(
            query=cleaned_query,
            plan=plan,
            search_results=search_results,
            summary=summary,
            report=report,
        )
