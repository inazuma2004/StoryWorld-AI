"""Tests du compositeur de pages de BD."""

from PIL import Image

from storyworld.domain.models import (
    CharacterDraft,
    PanelDraft,
    SceneDraft,
    StoryDraft,
)
from storyworld.services.composer import Composer


def _story(panel_count: int, dialogue: str = "Bonjour le monde.") -> StoryDraft:
    panels = [
        PanelDraft(
            numero=i + 1,
            description_visuelle=f"Case {i + 1}.",
            dialogue=dialogue,
            personnages=["Leila"],
        )
        for i in range(panel_count)
    ]
    return StoryDraft(
        title="Titre test",
        synopsis="Synopsis de test.",
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
        scenes=[SceneDraft(numero=1, description="Scène.", panels=panels)],
    )


def _solid(path, color=(255, 0, 0), size=(512, 512)):
    Image.new("RGB", size, color).save(path)
    return path


def test_compose_story_quatre_cases_une_page(tmp_path):
    story = _story(4)
    images = {i: _solid(tmp_path / f"p{i}.png") for i in range(1, 5)}

    pages = Composer().compose_story(story, images, tmp_path / "pages")

    assert len(pages) == 1
    assert pages[0].exists()
    with Image.open(pages[0]) as page:
        assert page.size == Composer.PAGE_SIZE


def test_compose_story_cinq_cases_deux_pages(tmp_path):
    story = _story(5)
    images = {i: _solid(tmp_path / f"p{i}.png") for i in range(1, 6)}

    pages = Composer().compose_story(story, images, tmp_path / "pages")

    assert len(pages) == 2
    assert all(path.exists() for path in pages)


def test_compose_story_sans_image_ne_plante_pas(tmp_path):
    story = _story(2)

    pages = Composer().compose_story(story, {}, tmp_path / "pages")

    assert len(pages) == 1
    assert pages[0].exists()


def test_compose_story_bulle_ajoute_du_blanc(tmp_path):
    """La bulle de dialogue est blanche : elle ajoute des pixels blancs sur l'image rouge."""
    images = {1: _solid(tmp_path / "p1.png")}
    composer = Composer()

    with_dialogue = composer.compose_story(
        _story(1, dialogue="Bonjour le monde."), images, tmp_path / "avec"
    )[0]
    without_dialogue = composer.compose_story(
        _story(1, dialogue=""), images, tmp_path / "sans"
    )[0]

    with Image.open(with_dialogue) as page:
        white_with = sum(1 for px in page.convert("RGB").getdata() if px == (255, 255, 255))
    with Image.open(without_dialogue) as page:
        white_without = sum(1 for px in page.convert("RGB").getdata() if px == (255, 255, 255))

    assert white_with > white_without


def test_wrap_dialogue_respecte_la_largeur():
    composer = Composer()
    font = composer._font(20)
    lines = composer._wrap("Un dialogue assez long pour devoir être découpé en plusieurs lignes.", font, 200)

    assert len(lines) > 1
    assert all(
        composer._text_width(line, font) <= 200 for line in lines
    )
