"""Règles de validation narrative sur un scénario généré."""

from __future__ import annotations

from storyworld.config import Settings
from storyworld.domain.models import StoryDraft


class ValidationIssue:
    """Problème détecté lors de la validation narrative."""

    def __init__(self, code: str, message: str, panel_index: int | None = None):
        self.code = code
        self.message = message
        self.panel_index = panel_index

    def __eq__(self, other):
        if not isinstance(other, ValidationIssue):
            return NotImplemented
        return (
            self.code == other.code
            and self.message == other.message
            and self.panel_index == other.panel_index
        )

    def __repr__(self):
        return f"ValidationIssue(code={self.code!r}, message={self.message!r}, panel_index={self.panel_index!r})"


def validate_story(story: StoryDraft, settings: Settings | None = None) -> list[ValidationIssue]:
    """Vérifie la cohérence narrative d'un StoryDraft.

    Règles :
    - titre non vide
    - dialogues non vides et <= max_dialogue_chars
    - personnages référencés dans les cases existent dans la liste des personnages
    """
    settings = settings or Settings()
    issues: list[ValidationIssue] = []

    if not story.title or not story.title.strip():
        issues.append(ValidationIssue("empty_title", "Le titre ne doit pas être vide."))

    character_names = {c.name for c in story.characters}

    for scene in story.scenes:
        for panel in scene.panels:
            dialogue = (panel.dialogue or "").strip()
            if not dialogue:
                issues.append(
                    ValidationIssue(
                        "empty_dialogue",
                        f"Case {panel.numero} : le dialogue est vide.",
                        panel.numero,
                    )
                )
            elif len(dialogue) > settings.max_dialogue_chars:
                issues.append(
                    ValidationIssue(
                        "dialogue_too_long",
                        f"Case {panel.numero} : le dialogue dépasse {settings.max_dialogue_chars} caractères.",
                        panel.numero,
                    )
                )

            for name in panel.personnages:
                if name not in character_names:
                    issues.append(
                        ValidationIssue(
                            "unknown_character",
                            f"Case {panel.numero} : personnage inconnu '{name}'.",
                            panel.numero,
                        )
                    )

    return issues
