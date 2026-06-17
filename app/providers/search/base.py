"""Base interfaces for web search providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class SearchResult:
    """Normalized web search result."""

    title: str
    url: str
    snippet: str
    rank: int


class BaseSearchProvider(ABC):
    """Common interface for search providers."""

    @abstractmethod
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search the web for a query."""
