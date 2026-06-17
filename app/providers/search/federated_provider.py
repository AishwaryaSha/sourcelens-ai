"""Small federated search provider for Phase 1."""

import logging

from app.core.exceptions import SearchError
from app.providers.search.base import BaseSearchProvider, SearchResult

logger = logging.getLogger(__name__)


class FederatedSearchProvider(BaseSearchProvider):
    """Query multiple free providers and return deduplicated results."""

    def __init__(self, providers: list[BaseSearchProvider]) -> None:
        self._providers = providers

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search providers in order and gracefully skip provider failures."""

        if not self._providers:
            raise SearchError("No search providers are configured.")

        results: list[SearchResult] = []
        errors: list[str] = []
        per_provider_limit = max(1, min(max_results, (max_results // len(self._providers)) + 1))

        for provider in self._providers:
            try:
                provider_results = provider.search(
                    query=query,
                    max_results=per_provider_limit,
                )
            except SearchError as exc:
                logger.warning("%s failed: %s", provider.__class__.__name__, exc)
                errors.append(str(exc))
                continue

            results.extend(provider_results)

        deduped = _dedupe_results(results)
        if not deduped and errors:
            raise SearchError("; ".join(errors))
        return deduped[:max_results]


def _dedupe_results(results: list[SearchResult]) -> list[SearchResult]:
    deduped: dict[str, SearchResult] = {}
    for result in results:
        if result.url not in deduped:
            deduped[result.url] = SearchResult(
                title=result.title,
                url=result.url,
                snippet=result.snippet,
                rank=len(deduped) + 1,
            )
    return list(deduped.values())
