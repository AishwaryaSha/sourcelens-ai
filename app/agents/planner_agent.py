"""Planner agent for Phase 1 research planning."""

import logging
from dataclasses import dataclass, field

from app.providers.llm.base import BaseLLMProvider
from app.utils.text import clean_lines, normalize_whitespace

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class ResearchPlan:
    """Simple research plan produced from a user query."""

    objective: str
    subquestions: list[str] = field(default_factory=list)
    search_queries: list[str] = field(default_factory=list)


class PlannerAgent:
    """Create a focused web research plan."""

    def __init__(self, llm_provider: BaseLLMProvider | None = None) -> None:
        self._llm_provider = llm_provider

    def plan(self, query: str) -> ResearchPlan:
        """Create a plan using Ollama when available, otherwise fallback."""

        cleaned_query = normalize_whitespace(query)
        if not cleaned_query:
            raise ValueError("Query cannot be empty.")

        # if self._llm_provider and self._llm_provider.is_available():
        #     try:
        #         return self._plan_with_llm(cleaned_query)
        #     except Exception as exc:
        #         logger.warning("Planner LLM failed; using fallback plan: %s", exc)

        return self._fallback_plan(cleaned_query)

    def _plan_with_llm(self, query: str) -> ResearchPlan:
        prompt = f"""
Create a concise research plan for this query:

{query}

Return exactly two sections:
Subquestions:
- ...

Search queries:
- ...

Use 2-4 subquestions and 2-4 search queries. Keep each item short.
"""
        response = self._llm_provider.generate(
            prompt=prompt.strip(),
            system_prompt="You are a practical research planner.",
            temperature=0.1,
        )
        subquestions = self._extract_section(response.text, "Subquestions")
        search_queries = self._extract_section(response.text, "Search queries")

        if not subquestions or not search_queries:
            logger.info("Planner LLM output was incomplete; using fallback plan.")
            return self._fallback_plan(query)

        return ResearchPlan(
            objective=query,
            subquestions=subquestions[:4],
            search_queries=search_queries[:4],
        )

    def _fallback_plan(self, query: str) -> ResearchPlan:
        return ResearchPlan(
            objective=query,
            subquestions=[
                f"What are the key facts about {query}?",
                f"What recent or reliable sources discuss {query}?",
                f"What conclusions are supported by available sources about {query}?",
            ],
            search_queries=[
                query,
                f"{query} overview",
                f"{query} analysis",
            ],
        )

    @staticmethod
    def _extract_section(text: str, heading: str) -> list[str]:
        lines = text.splitlines()
        in_section = False
        captured: list[str] = []
        for line in lines:
            normalized = line.strip().lower().rstrip(":")
            if normalized == heading.lower():
                in_section = True
                continue
            if in_section and normalized in {"subquestions", "search queries"}:
                break
            if in_section:
                captured.append(line)
        return clean_lines(captured)
