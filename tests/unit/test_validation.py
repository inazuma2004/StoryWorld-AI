"""Tests de validation narrative."""

from storyworld.domain.models import (
    CharacterDraft,
    PanelDraft,
    SceneDraft,
    StoryDraft,
)
from storyworld.domain.validation import validate_story


def _build_story() -> StoryDraft:
    return StoryDraft(
        title="Titre",
        synopsis="Synopsis de test.",
        characters=[
            CharacterDraft(
                name="Leila",
                role="heroine",
                personnalite="curieuse",
                vetements="jean",
                couleurs="bleu",
                attributs_distinctifs="lunettes",
            )
        ],
        scenes=[
            SceneDraft(
                numero=1,
                description="Début de l'histoire.",
                panels=[
                    PanelDraft(
                        numero=1,
                        description_visuelle="Une ruelle.",
                        dialogue="Bonjour le monde.",
                        personnages=["Leila"],
                    )
                ],
            ),
            SceneDraft(
                numero=2,
                description="Fin de l'histoire.",
                panels=[
                    PanelDraft(
                        numero=2,
                        description_visuelle="Un coucher de soleil.",
                        dialogue="Merci.",
                        personnages=["Leila"],
                    )
                ],
            ),
        ],
    )


def test_validate_story_ok():
    issues = validate_story(_build_story())
    assert issues == []


def test_validate_dialogue_too_long():
    story = _build_story()
    story.scenes[0].panels[0].dialogue = "A" * 121
    issues = validate_story(story)
    assert any(i.code == "dialogue_too_long" for i in issues)


def test_validate_empty_dialogue():
    story = _build_story()
    story.scenes[0].panels[0].dialogue = ""
    issues = validate_story(story)
    assert any(i.code == "empty_dialogue" for i in issues)


def test_validate_unknown_character():
    story = _build_story()
    story.scenes[0].panels[0].personnages = ["Inconnu"]
    issues = validate_story(story)
    assert any(i.code == "unknown_character" for i in issues)


def test_validate_empty_title():
    story = _build_story()
    story.title = ""
    issues = validate_story(story)
    assert any(i.code == "empty_title" for i in issues)
