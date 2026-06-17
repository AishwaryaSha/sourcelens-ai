import httpx

from app.core.config import Settings
from app.providers.llm.ollama_provider import OllamaProvider


def test_ollama_resolves_configured_model_to_installed_tag(monkeypatch) -> None:
    settings = Settings(ollama_model="llama3.1")
    provider = OllamaProvider(settings)

    monkeypatch.setattr(
        provider,
        "available_models",
        lambda: ["llama3.1:latest", "mistral:latest"],
    )

    assert provider._resolve_model() == "llama3.1:latest"


def test_ollama_chat_response_is_parsed(monkeypatch) -> None:
    settings = Settings(ollama_model="llama3.1")
    provider = OllamaProvider(settings)

    monkeypatch.setattr(
        provider,
        "available_models",
        lambda: ["llama3.1:latest"],
    )

    def fake_post(url, json, timeout):
        assert url.endswith("/api/chat")
        assert json["model"] == "llama3.1:latest"
        assert json["messages"][0]["role"] == "system"
        assert json["messages"][1]["role"] == "user"

        request = httpx.Request(
            "POST",
            "http://localhost:11434/api/chat",
        )

        return httpx.Response(
            status_code=200,
            request=request,
            json={"message": {"content": "Generated answer"}},
        )

    monkeypatch.setattr(httpx, "post", fake_post)

    response = provider.generate(
        prompt="Summarize AI agents.",
        system_prompt="You are concise.",
    )

    assert response.text == "Generated answer"
    assert response.model == "llama3.1:latest"