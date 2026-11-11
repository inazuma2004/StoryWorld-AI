"""Générateur d'images avec cache par hash du prompt."""

from __future__ import annotations

import hashlib
from pathlib import Path

from storyworld.domain.models import CharacterDraft, SceneDraft, Style
from storyworld.providers.base import ImageProvider
from storyworld.services.prompt_builder import build_image_prompt


class ImageGenerator:
    """Génère et met en cache les illustrations de cases.

    Le cache est clé par le hash SHA-256 du prompt (tronqué à 16 caractères).
    Si une image existe déjà pour un prompt donné, elle est retournée sans
    nouvel appel au fournisseur.
    """

    def __init__(self, image_provider: ImageProvider, output_dir: Path):
        self.image_provider = image_provider
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_panel_image(
        self,
        scene: SceneDraft,
        character: CharacterDraft,
        style: Style,
        panel_index: int,
    ) -> Path:
        prompt = build_image_prompt(scene, character, style, panel_index)
        image_hash = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
        output_path = self.output_dir / f"{image_hash}.png"

        if output_path.exists():
            return output_path

        image_bytes = self.image_provider.generate(prompt)
        output_path.write_bytes(image_bytes)
        return output_path
