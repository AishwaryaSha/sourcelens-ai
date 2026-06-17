from app.core.exceptions import SearchError
from app.providers.search.base import BaseSearchProvider, SearchResult
from app.providers.search.federated_provider import FederatedSearchProvider
from app.providers.search.openalex_provider import OpenAlexSearchProvider
from app.providers.search.openalex_provider import normalize_openalex_query
from app.providers.search.wikipedia_provider import WikipediaSearchProvider


def test_wikipedia_parser_returns_mediawiki_results() -> None:
    results = WikipediaSearchProvider._parse_results(
        data={
            "query": {
                "search": [
                    {
                        "title": "Electric vehicle",
                        "snippet": "An <span>electric vehicle</span> uses electric motors.",
                    }
                ]
            }
        },
        max_results=3,
    )

    assert len(results) == 1
    assert results[0].title == "Wikipedia: Electric vehicle"
    assert results[0].url == "https://en.wikipedia.org/wiki/Electric_vehicle"
    assert "<span>" not in results[0].snippet


def test_openalex_parser_returns_academic_results() -> None:
    results = OpenAlexSearchProvider._parse_results(
        data={
            "results": [
                {
                    "display_name": "Attention Is All You Need",
                    "doi": "https://doi.org/10.48550/arXiv.1706.03762",
                    "publication_year": 2017,
                    "authorships": [
                        {"author": {"display_name": "Ashish Vaswani"}},
                        {"author": {"display_name": "Noam Shazeer"}},
                    ],
                    "abstract_inverted_index": {
                        "Transformers": [0],
                        "use": [1],
                        "attention": [2],
                    },
                }
            ]
        },
        max_results=2,
    )

    assert len(results) == 1
    assert results[0].title == "OpenAlex: Attention Is All You Need"
    assert results[0].url.startswith("https://doi.org/")
    assert "Published 2017" in results[0].snippet
    assert "Ashish Vaswani" in results[0].snippet


def test_openalex_normalizes_question_mark_queries() -> None:
    assert normalize_openalex_query("What are AI agents?") == "ai agents"


def test_openalex_normalizes_multi_word_queries() -> None:
    assert normalize_openalex_query("Electric vehicles in India") == "electric vehicles in india"


def test_openalex_normalizes_empty_queries() -> None:
    assert normalize_openalex_query("???   !!!") == ""


class FailingProvider(BaseSearchProvider):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        raise SearchError("provider failed")


class StaticProvider(BaseSearchProvider):
    def search(self, query: str, max_results: int) -> list[SearchResult]:
        return [
            SearchResult(
                title="Static source",
                url="https://example.com/source",
                snippet=f"Result for {query}",
                rank=1,
            )
        ][:max_results]


def test_federated_provider_skips_failed_provider() -> None:
    provider = FederatedSearchProvider(
        providers=[FailingProvider(), StaticProvider()],
    )

    results = provider.search(query="ai agents", max_results=3)

    assert len(results) == 1
    assert results[0].title == "Static source"
