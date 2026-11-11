from storyworld.domain.models import StoryDraft
from storyworld.providers.mock import MockImageProvider, MockTextProvider


def test_mock_text_is_valid_and_deterministic():
    provider = MockTextProvider()
    first = provider.generate_json("brief", StoryDraft)
    second = provider.generate_json("brief", StoryDraft)
    assert first == second
    StoryDraft.model_validate(first)


def test_mock_image_returns_png():
    data = MockImageProvider().generate("case 1")
    assert data[:8] == b"\x89PNG\r\n\x1a\n"

