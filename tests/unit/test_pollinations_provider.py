"""Tests du provider image Pollinations (simulés avec respx)."""

import httpx
import pytest
import respx

from storyworld.providers.base import ProviderError
from storyworld.providers.pollinations import PollinationsImageProvider


@respx.mock
def test_pollinations_retourne_des_octets_png():
    route = respx.get(url__startswith="https://image.pollinations.ai/prompt/").mock(
        return_value=httpx.Response(200, content=b"\x89PNG\r\n\x1a\nfake")
    )
    provider = PollinationsImageProvider()

    data = provider.generate("un robot dans une ruelle", size=(768, 768), seed=42)

    assert data == b"\x89PNG\r\n\x1a\nfake"
    assert route.called
    request = route.calls[0].request
    assert request.url.params["width"] == "768"
    assert request.url.params["height"] == "768"
    assert request.url.params["seed"] == "42"
    assert request.url.params["nologo"] == "true"
    assert "un%20robot" in str(request.url)


@respx.mock
def test_pollinations_erreur_http_leve_provider_error():
    respx.get(url__startswith="https://image.pollinations.ai/prompt/").mock(
        return_value=httpx.Response(500, text="boom")
    )
    provider = PollinationsImageProvider()

    with pytest.raises(ProviderError):
        provider.generate("un robot")


@respx.mock
def test_pollinations_timeout_leve_provider_error():
    respx.get(url__startswith="https://image.pollinations.ai/prompt/").mock(
        side_effect=httpx.TimeoutException("timeout")
    )
    provider = PollinationsImageProvider()

    with pytest.raises(ProviderError):
        provider.generate("un robot")


@respx.mock
def test_pollinations_envoie_le_token_si_fourni():
    route = respx.get(url__startswith="https://image.pollinations.ai/prompt/").mock(
        return_value=httpx.Response(200, content=b"img")
    )
    provider = PollinationsImageProvider(token="pk-test")

    provider.generate("un robot")

    assert route.calls[0].request.headers["authorization"] == "Bearer pk-test"
