"""Tests du provider Gemini (client injectable, aucun appel réseau)."""

from unittest.mock import MagicMock

import pytest

from storyworld.domain.models import StoryDraft
from storyworld.providers.base import ProviderError
from storyworld.providers.gemini import GeminiTextProvider


def test_gemini_generate_json_returns_dict():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = (
        '{"title": "T", "synopsis": "S", "characters": [], "scenes": []}'
    )
    provider = GeminiTextProvider(api_key="test-key", client=mock_client)
    result = provider.generate_json("prompt", StoryDraft)
    assert result == {"title": "T", "synopsis": "S", "characters": [], "scenes": []}


def test_gemini_markdown_json_is_repaired():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = (
        '```json\n{"title": "T", "synopsis": "S", "characters": [], "scenes": []}\n```'
    )
    provider = GeminiTextProvider(api_key="test-key", client=mock_client)
    result = provider.generate_json("prompt", StoryDraft)
    assert result["title"] == "T"


def test_gemini_invalid_json_raises_provider_error():
    mock_client = MagicMock()
    mock_client.models.generate_content.return_value.text = "ce n'est pas du JSON"
    provider = GeminiTextProvider(api_key="test-key", client=mock_client)
    with pytest.raises(ProviderError):
        provider.generate_json("prompt", StoryDraft)


def test_gemini_api_error_raises_provider_error():
    mock_client = MagicMock()
    mock_client.models.generate_content.side_effect = Exception("quota exceeded")
    provider = GeminiTextProvider(api_key="test-key", client=mock_client)
    with pytest.raises(ProviderError):
        provider.generate_json("prompt", StoryDraft)
