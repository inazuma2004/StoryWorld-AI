"""Tests de l'export PDF et ZIP."""

import zipfile

from pypdf import PdfReader

from storyworld.domain.models import (
    CharacterDraft,
    PanelDraft,
    SceneDraft,
    StoryDraft,
)
from storyworld.services.composer import Composer
from storyworld.services.exporter import Exporter


def _story() -> StoryDraft:
    return StoryDraft(
        title="Le robot du jardin",
        synopsis="Une étudiante répare un robot abandonné.",
        characters=[
            CharacterDraft(
                name="Leila",
                role="héroïne",
                personnalite="curieuse",
                vetements="jean",
                couleurs="bleu",
                attributs_distinctifs="lunettes",
            )
        ],
        scenes=[
            SceneDraft(
                numero=1,
                description="Leila découvre le robot.",
                panels=[
                    PanelDraft(
                        numero=1,
                        description_visuelle="Une ruelle.",
                        dialogue="Tu fonctionnes encore ?",
                        personnages=["Leila"],
                    ),
                    PanelDraft(
                        numero=2,
                        description_visuelle="Le robot s'allume.",
                        dialogue="Oui, merci Leila.",
                        personnages=["Leila"],
                    ),
                ],
            )
        ],
    )


def test_export_pdf_contient_texte_et_pages_images(tmp_path):
    story = _story()
    composer = Composer()
    pages = composer.compose_story(story, {}, tmp_path / "pages")

    pdf_path = Exporter().export_pdf(story, pages, tmp_path / "story.pdf")

    assert pdf_path.exists()
    reader = PdfReader(str(pdf_path))
    assert len(reader.pages) == 1 + len(pages)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert story.title in text
    assert "Tu fonctionnes encore ?" in text
    assert "Leila" in text


def test_export_png_zip_contient_les_cases(tmp_path):
    story = _story()
    from PIL import Image

    images = {}
    for index in range(1, 3):
        path = tmp_path / f"panel_{index}.png"
        Image.new("RGB", (128, 128), (index * 80, 0, 0)).save(path)
        images[index] = path

    zip_path = Exporter().export_png_zip(story, images, tmp_path / "images.zip")

    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == ["panel_1.png", "panel_2.png"]
