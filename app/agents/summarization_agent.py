"""Summarization agent for grounded Phase 1 reports."""

import logging
from dataclasses import dataclass

from app.agents.planner_agent import ResearchPlan
from app.providers.llm.base import BaseLLMProvider
from app.providers.search.base import SearchResult
from app.utils.text import truncate_text

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchSummary:
    """Summary output from the summarization agent."""

    answer: str
    key_points: list[str]
    limitations: list[str]
    used_llm: bool


class SummarizationAgent:
    """Summarize search evidence using Ollama with a deterministic fallback."""

    def __init__(self, llm_provider: BaseLLMProvider | None = None) -> None:
        self._llm_provider = llm_provider

    def summarize(
        self,
        query: str,
        plan: ResearchPlan,
        search_results: list[SearchResult],
    ) -> ResearchSummary:
        """Generate a grounded summary from search results."""

        if self._llm_provider and self._llm_provider.is_available() and search_results:
            try:
                return self._summarize_with_llm(query, plan, search_results)
            except Exception as exc:
                logger.warning("Summarization LLM failed; using fallback: %s", exc)

        return self._fallback_summary(query, search_results)

    def _summarize_with_llm(
        self,
        query: str,
        plan: ResearchPlan,
        search_results: list[SearchResult],
    ) -> ResearchSummary:
        evidence = "\n\n".join(
            f"[{index}] {result.title}\nURL: {result.url}\nSnippet: {result.snippet}"
            for index, result in enumerate(search_results, start=1)
        )
        subquestions = "\n".join(f"- {item}" for item in plan.subquestions)

        prompt = f"""
User query:
{query}

Research subquestions:
{subquestions}

Search evidence:
{evidence}

Write a concise research summary grounded only in the search evidence.
Return exactly this format:

Answer:
...

Key points:
- ...

Limitations:
- ...
"""
        response = self._llm_provider.generate(
            prompt=prompt.strip(),
            system_prompt=(
                "You are a careful research assistant. Do not invent facts. "
                "If evidence is thin, say so clearly."
            ),
            temperature=0.2,
        )
        answer = self._extract_block(response.text, "Answer")
        key_points = self._extract_bullets(response.text, "Key points")
        limitations = self._extract_bullets(response.text, "Limitations")

        return ResearchSummary(
            answer=answer or truncate_text(response.text, 1200),
            key_points=key_points or self._fallback_key_points(search_results),
            limitations=limitations
            or ["This Phase 1 report is based on search snippets, not full-source verification."],
            used_llm=True,
        )

    def _fallback_summary(
        self,
        query: str,
        search_results: list[SearchResult],
    ) -> ResearchSummary:
        if not search_results:
            return ResearchSummary(
                answer=(
                    f"No web search results were available for '{query}'. "
                    "Try a more specific query or check network access."
                ),
                key_points=[],
                limitations=["No sources were retrieved."],
                used_llm=False,
            )

        key_points = self._fallback_key_points(search_results)
        answer = (
            f"Initial research for '{query}' found {len(search_results)} web sources. "
            "The strongest available signals from the retrieved snippets are summarized below."
        )
        return ResearchSummary(
            answer=answer,
            key_points=key_points,
            limitations=[
                "Ollama was unavailable or failed, so this summary uses retrieved snippets directly.",
                "Phase 1 does not verify claims against full source text.",
            ],
            used_llm=False,
        )

    @staticmethod
    def _fallback_key_points(search_results: list[SearchResult]) -> list[str]:
        return [
            f"{result.title}: {truncate_text(result.snippet, 220)}"
            for result in search_results
            if result.snippet
        ][:5]

    @staticmethod
    def _extract_block(text: str, heading: str) -> str:
        lines = text.splitlines()
        in_section = False
        captured: list[str] = []
        known_headings = {"answer", "key points", "limitations"}
        for line in lines:
            normalized = line.strip().lower().rstrip(":")
            if normalized == heading.lower():
                in_section = True
                continue
            if in_section and normalized in known_headings:
                break
            if in_section:
                captured.append(line.strip())
        return "\n".join(line for line in captured if line).strip()

    @staticmethod
    def _extract_bullets(text: str, heading: str) -> list[str]:
        block = SummarizationAgent._extract_block(text, heading)
        bullets: list[str] = []
        for line in block.splitlines():
            cleaned = line.strip().lstrip("-*0123456789. ").strip()
            if cleaned:
                bullets.append(cleaned)
        return bullets
