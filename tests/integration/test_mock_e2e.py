"""Parcours Mock de bout en bout : idée → storyboard → images → PDF."""

from pathlib import Path

from pypdf import PdfReader

from storyworld.config import Settings
from storyworld.domain.models import StoryBrief
from storyworld.providers.mock import MockImageProvider, MockTextProvider
from storyworld.services.composer import Composer
from storyworld.services.exporter import Exporter
from storyworld.services.story_generator import StoryGenerator
from storyworld.storage import Repository, create_session_factory


def test_idea_to_pdf_with_mocks(tmp_path: Path):
    settings = Settings(
        text_provider="mock",
        image_provider="mock",
        data_dir=tmp_path,
    )
    repo = Repository(create_session_factory(tmp_path / "db.sqlite"))
    generator = StoryGenerator(
        MockTextProvider(), MockImageProvider(), repo, settings
    )
    story = generator.generate(
        StoryBrief(
            idea="un robot jardinier",
            genre="aventure",
            style="manga",
            audience="enfant",
            language="fr",
            panel_count=4,
        )
    )
    assert len(story.scenes) >= 1
    total_panels = sum(len(s.panels) for s in story.scenes)
    assert total_panels == 4

    composer = Composer()
    pages: list[Path] = []
    for i in range(1):
        page_path = tmp_path / f"page_{i}.png"
        pages.append(composer.render_page(story, {}, i, page_path))

    exporter = Exporter()
    pdf_path = tmp_path / "story.pdf"
    exporter.export_pdf(story, pages, pdf_path)

    reader = PdfReader(str(pdf_path))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert story.title in text
