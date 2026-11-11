"""Tests du constructeur de prompts visuels."""

from storyworld.domain.models import CharacterDraft, PanelDraft, SceneDraft, Style
from storyworld.services.prompt_builder import build_image_prompt


def test_image_prompt_contient_elements_essentiels():
    character = CharacterDraft(
        name="Leila",
        role="héroïne",
        personnalite="curieuse",
        vetements="sweat à capuche et jean",
        couleurs="bleu marine et gris",
        attributs_distinctifs="lunettes de réparation",
    )
    panel = PanelDraft(
        numero=1,
        description_visuelle="Ruelle étroite, murs ocre, lumière orangée.",
        dialogue="Bonjour le monde.",
        personnages=["Leila"],
    )
    scene = SceneDraft(
        numero=1,
        description="Leila marche dans les ruelles de Casablanca.",
        panels=[panel],
    )
    style: Style = "manga"

    prompt = build_image_prompt(scene, character, style, panel_index=1)

    assert "Leila" in prompt
    assert "manga" in prompt.lower()
    assert "lunettes de réparation" in prompt
    assert "Ruelle étroite" in prompt
    # Interdiction de texte dans l'image (les bulles sont ajoutées après)
    assert "texte" in prompt.lower()
    assert "pas de texte" in prompt.lower() or "no text" in prompt.lower()


def test_image_prompt_deterministe():
    character = CharacterDraft(
        name="Leila", role="héroïne", personnalite="curieuse",
        vetements="jean", couleurs="bleu", attributs_distinctifs="lunettes",
    )
    panel = PanelDraft(
        numero=1, description_visuelle="Une ruelle.", dialogue="Bonjour.", personnages=["Leila"],
    )
    scene = SceneDraft(numero=1, description="Test.", panels=[panel])

    p1 = build_image_prompt(scene, character, "manga", panel_index=1)
    p2 = build_image_prompt(scene, character, "manga", panel_index=1)
    assert p1 == p2


def test_image_prompt_varie_selon_style():
    character = CharacterDraft(
        name="Leila", role="héroïne", personnalite="curieuse",
        vetements="jean", couleurs="bleu", attributs_distinctifs="lunettes",
    )
    panel = PanelDraft(
        numero=1, description_visuelle="Une ruelle.", dialogue="Bonjour.", personnages=["Leila"],
    )
    scene = SceneDraft(numero=1, description="Test.", panels=[panel])

    p_manga = build_image_prompt(scene, character, "manga", panel_index=1)
    p_comics = build_image_prompt(scene, character, "comics", panel_index=1)
    assert p_manga != p_comics
