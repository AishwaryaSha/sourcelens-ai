from app.core.config import Settings


def test_settings_defaults_are_valid() -> None:
    settings = Settings()

    assert settings.app_name == "SourceLens AI"
    assert settings.search_max_results >= 1
    assert settings.ollama_base_url.startswith("http")
