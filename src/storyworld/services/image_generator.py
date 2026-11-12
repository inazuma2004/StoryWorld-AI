"""Générateur d'images avec cache par hash du prompt."""

from __future__ import annotations

import hashlib
import io
from pathlib import Path

from PIL import Image

from storyworld.domain.models import CharacterDraft, SceneDraft, Style
from storyworld.providers.base import ImageProvider, ProviderError
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
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                normalized = image.convert("RGB")
                normalized.save(output_path, format="PNG")
        except Exception as exc:
            raise ProviderError(
                "Le provider d'images a renvoyé un contenu illisible"
            ) from exc
        return output_path
