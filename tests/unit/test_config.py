import pytest
from pydantic import ValidationError

from storyworld.config import get_settings


def test_defaults_use_mock_providers(monkeypatch):
    monkeypatch.delenv("STORYWORLD_TEXT_PROVIDER", raising=False)
    monkeypatch.delenv("STORYWORLD_IMAGE_PROVIDER", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("HF_TOKEN", raising=False)
    settings = get_settings()
    assert settings.text_provider == "mock"
    assert settings.image_provider == "mock"


def test_gemini_requires_api_key(monkeypatch):
    monkeypatch.setenv("STORYWORLD_TEXT_PROVIDER", "gemini")
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with pytest.raises(ValidationError):
        get_settings()


def test_hf_requires_token(monkeypatch):
    monkeypatch.setenv("STORYWORLD_IMAGE_PROVIDER", "hf")
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(ValidationError):
        get_settings()

