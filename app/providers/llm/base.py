"""Base interfaces for LLM providers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class LLMResponse:
    """Normalized response from an LLM provider."""

    text: str
    model: str
    provider: str


class BaseLLMProvider(ABC):
    """Common interface for local and remote LLM providers."""

    @abstractmethod
    def is_available(self) -> bool:
        """Return whether the provider is reachable."""

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generate text from a prompt."""
