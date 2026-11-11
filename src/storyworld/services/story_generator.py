"""Orchestre la génération d'une histoire : texte → validation → images → stockage."""

from __future__ import annotations

from pathlib import Path

from storyworld.config import Settings
from storyworld.domain.models import (
    CharacterDraft,
    StoryBrief,
    StoryDraft,
)
from storyworld.providers.base import ImageProvider, TextProvider
from storyworld.services.image_generator import ImageGenerator
from storyworld.storage import Repository


class StoryGenerator:
    def __init__(
        self,
        text_provider: TextProvider,
        image_provider: ImageProvider,
        repository: Repository,
        settings: Settings,
    ):
        self.text_provider = text_provider
        self.image_provider = image_provider
        self.repository = repository
        self.settings = settings

    def generate(self, brief: StoryBrief) -> StoryDraft:
        prompt = self._build_prompt(brief)
        raw = self.text_provider.generate_json(prompt, StoryDraft)
        story = StoryDraft.model_validate(raw)
        project_id = self.repository.save_project(story)
        self._generate_images(story, project_id)
        return story

    def _build_prompt(self, brief: StoryBrief) -> str:
        return (
            f"Génère un storyboard pour une BD de {brief.panel_count} cases. "
            f"Idee : {brief.idea}. Genre : {brief.genre}. Style : {brief.style}. "
            f"Public : {brief.audience}. Langue : {brief.language}."
        )

    def _generate_images(self, story: StoryDraft, project_id: str) -> None:
        output_dir: Path = self.settings.data_dir / "media" / "panels"
        image_gen = ImageGenerator(self.image_provider, output_dir)
        reference_character: CharacterDraft | None = (
            story.characters[0] if story.characters else None
        )

        for scene in story.scenes:
            for panel in scene.panels:
                try:
                    if reference_character:
                        path = image_gen.generate_panel_image(
                            scene, reference_character, "manga", panel.numero
                        )
                        panel.image_path = str(path)
                        panel.status = "generated"
                    else:
                        panel.status = "error"
                except Exception:  # noqa: BLE001 — statut passé à "error" en cas d'échec générateur
                    panel.status = "error"
