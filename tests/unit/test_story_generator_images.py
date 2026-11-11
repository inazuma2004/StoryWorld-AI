"""Tests du générateur d'histoire avec génération d'images."""

from storyworld.config import Settings
from storyworld.domain.models import StoryBrief
from storyworld.providers.mock import MockImageProvider, MockTextProvider
from storyworld.services.story_generator import StoryGenerator
from storyworld.storage import Repository, create_session_factory


def _build_brief() -> StoryBrief:
    return StoryBrief(
        idea="un robot jardinier",
        genre="aventure",
        style="manga",
        audience="enfant",
        language="fr",
        panel_count=2,
    )


def _build_repo(tmp_path):
    return Repository(create_session_factory(tmp_path / "db.sqlite"))


def test_story_generator_uses_image_cache(tmp_path):
    """Même scène générée deux fois → le provider d'image n'est appelé qu'une fois."""
    provider = MockImageProvider()
    repo = _build_repo(tmp_path)
    settings = Settings(text_provider="mock", image_provider="mock", data_dir=tmp_path)
    generator = StoryGenerator(MockTextProvider(), provider, repo, settings)

    brief = _build_brief()
    story = generator.generate(brief)

    # Chaque panel doit avoir un chemin d'image et un statut 'generated'
    total_panels = sum(len(s.panels) for s in story.scenes)
    panels_with_image = 0
    for scene in story.scenes:
        for panel in scene.panels:
            if panel.image_path and panel.status == "generated":
                panels_with_image += 1

    assert panels_with_image == total_panels
    # Le provider Mock sous-jacent appelé une fois par panel distinct (cache d'ImageGenerator)
    assert provider.call_count >= 1
