"""Tests du provider Ollama (simulés avec respx, aucun appel réseau réel)."""

import httpx
import pytest
import respx

from storyworld.domain.models import StoryDraft
from storyworld.providers.base import ProviderError
from storyworld.providers.ollama import OllamaTextProvider


@respx.mock
def test_ollama_generate_json_returns_dict():
    route = respx.post("http://localhost:11434/api/generate").mock(
        return_value=httpx.Response(
            200,
            json={
                "model": "llama3.2:1b",
                "response": '{"title": "T", "synopsis": "S", "characters": [], "scenes": []}',
                "done": True,
            },
        )
    )
    provider = OllamaTextProvider(base_url="http://localhost:11434")
    result = provider.generate_json("prompt", StoryDraft)
    assert result == {"title": "T", "synopsis": "S", "characters": [], "scenes": []}
    assert route.called


@respx.mock
def test_ollama_timeout_raises_provider_error():
    route = respx.post("http://localhost:11434/api/generate").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    provider = OllamaTextProvider(base_url="http://localhost:11434")
    with pytest.raises(ProviderError):
        provider.generate_json("prompt", StoryDraft)
    assert route.called
