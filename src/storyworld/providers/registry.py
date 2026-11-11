"""Registre des providers texte et image."""

from __future__ import annotations

from storyworld.providers.base import ImageProvider, ProviderError, TextProvider


def build_text_provider(settings) -> TextProvider:  # type: ignore[valid-type]
    if settings.text_provider == "mock":
        from storyworld.providers.mock import MockTextProvider

        return MockTextProvider()

    if settings.text_provider == "gemini":
        if not settings.gemini_api_key:
            raise ProviderError(
                "GEMINI_API_KEY est requis pour utiliser text_provider=gemini"
            )
        from storyworld.providers.gemini import GeminiTextProvider

        return GeminiTextProvider(
            api_key=settings.gemini_api_key.get_secret_value()
        )

    if settings.text_provider == "ollama":
        from storyworld.providers.ollama import OllamaTextProvider

        return OllamaTextProvider(
            base_url=settings.ollama_base_url,
            model="llama3.2:1b",
        )

    raise ProviderError(
        f"Provider texte non implémenté : {settings.text_provider}"
    )


def build_image_provider(settings) -> ImageProvider:  # type: ignore[valid-type]
    if settings.image_provider == "mock":
        from storyworld.providers.mock import MockImageProvider

        return MockImageProvider()

    if settings.image_provider in ("hf", "pollinations"):
        raise ProviderError(
            f"Provider image {settings.image_provider} non encore implémenté"
        )

    raise ProviderError(
        f"Provider image non implémenté : {settings.image_provider}"
    )
