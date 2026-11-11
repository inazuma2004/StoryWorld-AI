"""Compositeur de pages de BD : assemble les cases dans une page."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from storyworld.domain.models import StoryDraft


class Composer:
    def render_page(
        self,
        story: StoryDraft,
        panel_images: dict[int, Path],
        page_index: int,
        output_path: Path,
    ) -> Path:
        """Rend une page avec les cases (Mock : image blanche avec numéro de page)."""
        img = Image.new("RGB", (1024, 768), color=(255, 255, 255))
        img.save(output_path)
        return output_path
