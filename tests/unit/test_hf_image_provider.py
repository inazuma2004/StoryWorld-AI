"""Tests du provider image Hugging Face (simulés avec respx, aucun appel réseau réel)."""

import httpx
import pytest
import respx

from storyworld.providers.base import ProviderError
from storyworld.providers.hf import HuggingFaceImageProvider


@respx.mock
def test_hf_generate_returns_image_bytes():
    route = respx.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ).mock(return_value=httpx.Response(200, content=b"\x89PNG\r\n\x1a\nfake"))
    provider = HuggingFaceImageProvider(token="hf-test-token")
    data = provider.generate("un robot dans une ruelle")
    assert data == b"\x89PNG\r\n\x1a\nfake"
    assert route.called
    assert route.calls[0].request.headers["authorization"] == "Bearer hf-test-token"


@respx.mock
def test_hf_timeout_raises_provider_error():
    route = respx.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ).mock(side_effect=httpx.TimeoutException("timeout"))
    provider = HuggingFaceImageProvider(token="hf-test-token")
    with pytest.raises(ProviderError):
        provider.generate("un robot dans une ruelle")
    assert route.called


@respx.mock
def test_hf_http_error_raises_provider_error():
    route = respx.post(
        "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    ).mock(return_value=httpx.Response(503, text="model loading"))
    provider = HuggingFaceImageProvider(token="hf-test-token")
    with pytest.raises(ProviderError):
        provider.generate("un robot dans une ruelle")
    assert route.called
