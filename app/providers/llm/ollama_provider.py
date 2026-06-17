"""Ollama local LLM provider."""

import logging

import httpx

from app.core.config import Settings
from app.core.exceptions import ProviderError
from app.providers.llm.base import BaseLLMProvider, LLMResponse

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """Local-first Ollama provider using the HTTP API."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._base_url = settings.ollama_base_url.rstrip("/")

    def is_available(self) -> bool:
        """Return whether Ollama is reachable and has at least one model."""

        try:
            response = httpx.get(
                f"{self._base_url}/api/tags",
                timeout=120,
            )
            if response.status_code != 200:
                return False
            return bool(self.available_models())
        except httpx.HTTPError as exc:
            logger.warning("Ollama availability check failed: %s", exc)
            return False

    def available_models(self) -> list[str]:
        """Return model names installed in the local Ollama server."""

        try:
            response = httpx.get(
                f"{self._base_url}/api/tags",
                timeout=120,
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            logger.warning("Ollama model list failed: %s", exc)
            return []

        data = response.json()
        raw_models = data.get("models", [])
        if not isinstance(raw_models, list):
            return []

        models: list[str] = []
        for item in raw_models:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if name:
                models.append(name)
        return models

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float = 0.2,
    ) -> LLMResponse:
        """Generate text using Ollama's /api/chat endpoint."""

        model = self._resolve_model()

        logger.warning(
            "SETTINGS DEBUG: model=%s timeout=%s",
            self._settings.ollama_model,
            self._settings.ollama_timeout_seconds,
        )

        messages: list[dict[str, str]] = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }

        try:
            response = httpx.post(
                f"{self._base_url}/api/chat",
                json=payload,
                timeout=self._settings.ollama_timeout_seconds,
            )
            if response.status_code == 404:
                error_message = _ollama_error_message(response)
                raise ProviderError(
                    f"Ollama model or endpoint was not found: {error_message}. "
                    f"Installed models: {', '.join(self.available_models()) or 'none'}."
                )
            response.raise_for_status()
        except ProviderError:
            raise
        except httpx.HTTPError as exc:
            raise ProviderError(f"Ollama generation failed: {exc}") from exc

        data = response.json()
        message = data.get("message", {})
        if not isinstance(message, dict):
            raise ProviderError("Ollama returned an unexpected chat response.")

        text = str(message.get("content", "")).strip()
        if not text:
            raise ProviderError("Ollama returned an empty response.")

        return LLMResponse(
            text=text,
            model=model,
            provider="ollama",
        )

    def _resolve_model(self) -> str:
        configured_model = self._settings.ollama_model.strip()
        models = self.available_models()
        if not models:
            raise ProviderError("Ollama is reachable but no local models are installed.")

        if configured_model in models:
            return configured_model

        for model in models:
            if model.split(":", maxsplit=1)[0] == configured_model:
                logger.info(
                    "Using installed Ollama model '%s' for configured model '%s'",
                    model,
                    configured_model,
                )
                return model

        fallback_model = models[0]
        logger.warning(
            "Configured Ollama model '%s' is not installed; using '%s'.",
            configured_model,
            fallback_model,
        )
        return fallback_model


def _ollama_error_message(response: httpx.Response) -> str:
    try:
        data = response.json()
    except ValueError:
        return response.text.strip() or "404 Not Found"
    return str(data.get("error", "")).strip() or "404 Not Found"
