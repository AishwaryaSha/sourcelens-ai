"""OpenAlex search provider for lightweight academic sources."""

import logging
import re

import httpx

from app.core.config import Settings
from app.core.exceptions import SearchError
from app.providers.search.base import BaseSearchProvider, SearchResult

logger = logging.getLogger(__name__)


class OpenAlexSearchProvider(BaseSearchProvider):
    """Search scholarly works through the free OpenAlex API."""

    API_URL = "https://api.openalex.org/works"

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def search(self, query: str, max_results: int) -> list[SearchResult]:
        """Search OpenAlex works and return normalized academic results."""

        normalized_query = normalize_openalex_query(query)
        if not normalized_query:
            logger.info("Skipping OpenAlex search because the normalized query is empty.")
            return []

        try:
            with httpx.Client(
                timeout=min(self._settings.search_timeout_seconds, 8),
                headers={"User-Agent": self._settings.search_user_agent},
                follow_redirects=True,
            ) as client:
                response = client.get(
                    self.API_URL,
                    params={
                        "search": normalized_query,
                        "per-page": max_results,
                    },
                )
                if response.status_code == 429:
                    logger.warning("OpenAlex rate limited the search request.")
                    return []
                response.raise_for_status()
        except httpx.TimeoutException as exc:
            logger.warning("OpenAlex search timed out for query '%s'", normalized_query)
            return []
        except httpx.HTTPError as exc:
            raise SearchError(f"OpenAlex search request failed: {exc}") from exc

        return self._parse_results(response.json(), max_results=max_results)

    @staticmethod
    def _parse_results(data: dict[str, object], max_results: int) -> list[SearchResult]:
        raw_results = data.get("results", [])
        if not isinstance(raw_results, list):
            return []

        results: list[SearchResult] = []
        for item in raw_results:
            if len(results) >= max_results:
                break
            if not isinstance(item, dict):
                continue

            title = str(item.get("display_name", "")).strip()
            if not title:
                continue

            url = _best_openalex_url(item)
            snippet = _openalex_snippet(item)
            results.append(
                SearchResult(
                    title=f"OpenAlex: {title}",
                    url=url,
                    snippet=snippet,
                    rank=len(results) + 1,
                )
            )
        return results


def _best_openalex_url(item: dict[str, object]) -> str:
    doi = str(item.get("doi", "") or "").strip()
    if doi:
        return doi

    primary_location = item.get("primary_location", {})
    if isinstance(primary_location, dict):
        landing_page_url = str(primary_location.get("landing_page_url", "") or "").strip()
        if landing_page_url:
            return landing_page_url

    return str(item.get("id", "") or "").strip()


def normalize_openalex_query(query: str) -> str:
    """Normalize user/planner queries for OpenAlex search."""

    cleaned = query.strip().lower()
    cleaned = re.sub(r"[^\w\s-]", " ", cleaned)
    cleaned = re.sub(r"\b(what|who|when|where|why|how|are|is|the|a|an)\b", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def _openalex_snippet(item: dict[str, object]) -> str:
    year = item.get("publication_year")
    authorships = item.get("authorships", [])
    authors = _authors_from_authorships(authorships)
    abstract = _abstract_from_inverted_index(item.get("abstract_inverted_index"))

    parts: list[str] = []
    if year:
        parts.append(f"Published {year}.")
    if authors:
        parts.append(f"Authors: {authors}.")
    if abstract:
        parts.append(abstract)

    return " ".join(parts).strip()


def _authors_from_authorships(authorships: object) -> str:
    if not isinstance(authorships, list):
        return ""

    names: list[str] = []
    for authorship in authorships[:3]:
        if not isinstance(authorship, dict):
            continue
        author = authorship.get("author", {})
        if not isinstance(author, dict):
            continue
        name = str(author.get("display_name", "") or "").strip()
        if name:
            names.append(name)

    suffix = " et al" if len(authorships) > 3 else ""
    return ", ".join(names) + suffix if names else ""


def _abstract_from_inverted_index(value: object) -> str:
    if not isinstance(value, dict):
        return ""

    positioned_words: list[tuple[int, str]] = []
    for word, positions in value.items():
        if not isinstance(word, str) or not isinstance(positions, list):
            continue
        for position in positions:
            if isinstance(position, int):
                positioned_words.append((position, word))

    words = [word for _, word in sorted(positioned_words)]
    abstract = " ".join(words)
    if len(abstract) > 500:
        return f"{abstract[:497].rstrip()}..."
    return abstract
