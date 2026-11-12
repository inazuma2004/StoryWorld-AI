"""Tests du provider Ollama (simulés avec respx, aucun appel réseau réel)."""

import json

import httpx
import pytest
import respx

from storyworld.domain.models import StoryDraft
from storyworld.providers.base import ProviderError
from storyworld.providers.ollama import OllamaTextProvider


def _response(**kwargs) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "llama3.2:1b",
            "response": '{"title": "T", "synopsis": "S", "characters": [], "scenes": []}',
            "done": True,
        },
        **kwargs,
    )


@respx.mock
def test_ollama_generate_json_returns_dict():
    route = respx.post("http://localhost:11434/api/generate").mock(
        return_value=_response()
    )
    provider = OllamaTextProvider(base_url="http://localhost:11434")

    result = provider.generate_json("prompt", StoryDraft)

    assert result == {"title": "T", "synopsis": "S", "characters": [], "scenes": []}
    assert route.called


@respx.mock
def test_ollama_envoie_le_schema_structure_et_nettoie_le_prompt():
    route = respx.post("http://localhost:11434/api/generate").mock(
        return_value=_response()
    )
    provider = OllamaTextProvider(base_url="http://localhost:11434")
    prompt = (
        "Tu es un scénariste.\n\nRègles :\n"
        "- Réponds UNIQUEMENT avec un JSON valide.\n"
        '- Respecte le schéma JSON suivant : {"title": {"type": "string"}}\n'
        "- Chaque dialogue doit faire au maximum 120 caractères.\n"
    )

    provider.generate_json(prompt, StoryDraft)

    payload = json.loads(route.calls[0].request.content)
    assert payload["format"]["type"] == "object"
    assert "properties" in payload["format"]
    assert "schéma JSON suivant" not in payload["prompt"]
    assert "Chaque dialogue" in payload["prompt"]
    assert payload["stream"] is False


@respx.mock
def test_ollama_timeout_raises_provider_error():
    route = respx.post("http://localhost:11434/api/generate").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    provider = OllamaTextProvider(base_url="http://localhost:11434")

    with pytest.raises(ProviderError):
        provider.generate_json("prompt", StoryDraft)

    assert route.called
