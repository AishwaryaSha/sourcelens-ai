"""Search agent for Phase 1 web research."""

import logging

from app.agents.planner_agent import ResearchPlan
from app.core.config import Settings
from app.core.exceptions import SearchError
from app.providers.search.base import BaseSearchProvider, SearchResult

logger = logging.getLogger(__name__)


class SearchAgent:
    """Execute web searches from a research plan."""

    def __init__(self, provider: BaseSearchProvider, settings: Settings) -> None:
        self._provider = provider
        self._settings = settings

    def search(self, plan: ResearchPlan) -> list[SearchResult]:
        """Search for plan queries and deduplicate results by URL."""

        deduped: dict[str, SearchResult] = {}
        errors: list[str] = []

        for query in plan.search_queries:
            if len(deduped) >= self._settings.search_max_results:
                break

            try:
                results = self._provider.search(
                    query=query,
                    max_results=self._settings.search_max_results,
                )
            except SearchError as exc:
                logger.warning("Search failed for query '%s': %s", query, exc)
                errors.append(str(exc))
                continue

            for result in results:
                if len(deduped) >= self._settings.search_max_results:
                    break
                if result.url not in deduped:
                    deduped[result.url] = SearchResult(
                        title=result.title,
                        url=result.url,
                        snippet=result.snippet,
                        rank=len(deduped) + 1,
                    )

        if errors and not deduped:
            raise SearchError("; ".join(errors))

        return list(deduped.values())[: self._settings.search_max_results]
