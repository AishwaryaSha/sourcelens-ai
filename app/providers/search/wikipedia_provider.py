"""Wikipedia search provider using the official MediaWiki API."""

import logging
import time
from urllib.parse import quote

import httpx

from app.core.config import Settings
from app.core.exceptions import SearchError
from app.providers.search.base import BaseSearchProvider, SearchResult
from app.providers.search.html import strip_html_tags

logger = logging.getLogger(__name__)


class WikipediaSearchProvider(BaseSearchProvider):
    """Search Wikipedia through the official MediaWiki API."""

    API_URL = "https://en.wikipedia.org/w/api.php"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search Wikipedia and return normalized results."""

        params = {
            "action": "query",
            "list": "search",
            "srsearch": query,
            "srlimit": max_results,
            "format": "json",
            "formatversion": "2",
            "utf8": "1",
        }

        try:
            with httpx.Client(
                timeout=self._settings.search_timeout_seconds,
                headers={
                    "User-Agent": self._settings.search_user_agent,
                    "Api-User-Agent": self._settings.search_user_agent,
                },
                follow_redirects=True,
            ) as client:
                response = client.get(self.API_URL, params=params)
                if response.status_code == 429:
                    retry_after = _retry_after_seconds(response)
                    logger.warning(
                        "Wikipedia rate limited request; retrying after %s seconds",
                        retry_after,
                    )
                    time.sleep(retry_after)
                    response = client.get(self.API_URL, params=params)
                if response.status_code == 403:
                    raise SearchError(
                        "Wikipedia search was forbidden. Check the configured "
                        "SOURCELENS_SEARCH_USER_AGENT value."
                    )
                response.raise_for_status()
        except SearchError:
            raise
        except httpx.HTTPError as exc:
            raise SearchError(f"Wikipedia search request failed: {exc}") from exc

        return self._parse_results(response.json(), max_results=max_results)

    @staticmethod
    def _parse_results(data: dict[str, object], max_results: int) -> list[SearchResult]:
        query = data.get("query", {})
        if not isinstance(query, dict):
            return []

        raw_results = query.get("search", [])
        if not isinstance(raw_results, list):
            return []

        results: list[SearchResult] = []
        for item in raw_results:
            if len(results) >= max_results:
                break
            if not isinstance(item, dict):
                continue
            title = str(item.get("title", "")).strip()
            snippet = strip_html_tags(str(item.get("snippet", "")).strip())
            if not title:
                continue
            results.append(
                SearchResult(
                    title=f"Wikipedia: {title}",
                    url=f"https://en.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}",
                    snippet=snippet,
                    rank=len(results) + 1,
                )
            )
        return results


def _retry_after_seconds(response: httpx.Response) -> float:
    value = response.headers.get("Retry-After", "2")
    try:
        return min(max(float(value), 1), 5)
    except ValueError:
        return 2
