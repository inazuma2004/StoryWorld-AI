from storyworld.providers.base import ImageProvider, TextProvider


def build_text_provider(settings) -> TextProvider:  # type: ignore[valid-type]
    from storyworld.providers.mock import build_text_provider as _btp

    return _btp(settings)


def build_image_provider(settings) -> ImageProvider:  # type: ignore[valid-type]
    from storyworld.providers.mock import build_image_provider as _bip

    return _bip(settings)
