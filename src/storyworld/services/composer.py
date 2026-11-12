"""Compositeur de pages de BD : assemble les cases, bulles et titres."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from storyworld.domain.models import PanelDraft, StoryDraft

_FONT_CANDIDATES = {
    False: [
        r"C:\Windows\Fonts\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ],
    True: [
        r"C:\Windows\Fonts\arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ],
}


class Composer:
    """Compose des pages A4 (150 DPI) avec 4 cases maximum par page."""

    PAGE_SIZE = (1240, 1754)  # A4 à 150 DPI
    MARGIN = 60
    GAP = 24
    COLUMNS = 2
    PANELS_PER_PAGE = 4

    def __init__(self) -> None:
        self._font_cache: dict[tuple[int, bool], ImageFont.FreeTypeFont] = {}

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------

    def compose_story(
        self,
        story: StoryDraft,
        panel_images: dict[int, Path],
        output_dir: Path,
    ) -> list[Path]:
        """Compose toutes les pages de l'histoire et retourne leurs chemins.

        ``panel_images`` est indexé par la position globale de la case
        (1 = première case de la première scène).
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        panels = [
            (index, panel)
            for index, panel in enumerate(self._flatten_panels(story), start=1)
        ]
        pages: list[Path] = []
        for page_index in range(math.ceil(len(panels) / self.PANELS_PER_PAGE)):
            chunk = panels[
                page_index * self.PANELS_PER_PAGE : (page_index + 1) * self.PANELS_PER_PAGE
            ]
            output_path = output_dir / f"page_{page_index + 1}.png"
            self._render_page(story, chunk, page_index, panel_images, output_path)
            pages.append(output_path)
        return pages

    def render_page(
        self,
        story: StoryDraft,
        panel_images: dict[int, Path],
        page_index: int,
        output_path: Path,
    ) -> Path:
        """Rend une page précise (compatibilité avec l'ancienne API)."""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        panels = [
            (index, panel)
            for index, panel in enumerate(self._flatten_panels(story), start=1)
        ]
        chunk = panels[
            page_index * self.PANELS_PER_PAGE : (page_index + 1) * self.PANELS_PER_PAGE
        ]
        self._render_page(story, chunk, page_index, panel_images, output_path)
        return output_path

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def _render_page(
        self,
        story: StoryDraft,
        panels: list[tuple[int, PanelDraft]],
        page_index: int,
        panel_images: dict[int, Path],
        output_path: Path,
    ) -> None:
        width, height = self.PAGE_SIZE
        page = Image.new("RGB", self.PAGE_SIZE, "white")
        draw = ImageDraw.Draw(page)

        top = self.MARGIN
        if page_index == 0:
            top = self._draw_header(draw, story, top, width)

        rows = max(1, math.ceil(len(panels) / self.COLUMNS))
        cell_width = (width - 2 * self.MARGIN - (self.COLUMNS - 1) * self.GAP) // self.COLUMNS
        available_height = height - top - self.MARGIN - (rows - 1) * self.GAP
        cell_height = available_height // rows

        for position, (global_index, panel) in enumerate(panels):
            column = position % self.COLUMNS
            row = position // self.COLUMNS
            x = self.MARGIN + column * (cell_width + self.GAP)
            y = top + row * (cell_height + self.GAP)
            self._draw_panel(
                page,
                draw,
                panel,
                panel_images.get(global_index),
                x,
                y,
                cell_width,
                cell_height,
            )

        draw.text(
            (width // 2, height - 32),
            str(page_index + 1),
            fill=(120, 120, 120),
            font=self._font(18),
            anchor="mm",
        )
        page.save(output_path, format="PNG")

    def _draw_header(
        self, draw: ImageDraw.ImageDraw, story: StoryDraft, top: int, width: int
    ) -> int:
        draw.text(
            (self.MARGIN, top),
            story.title,
            fill=(17, 24, 39),
            font=self._font(46, bold=True),
        )
        top += 70

        synopsis_font = self._font(22)
        for line in self._wrap(story.synopsis, synopsis_font, width - 2 * self.MARGIN)[:3]:
            draw.text((self.MARGIN, top), line, fill=(75, 85, 99), font=synopsis_font)
            top += 30

        top += 16
        draw.line(
            (self.MARGIN, top, width - self.MARGIN, top), fill=(209, 213, 219), width=2
        )
        return top + 26

    def _draw_panel(
        self,
        page: Image.Image,
        draw: ImageDraw.ImageDraw,
        panel: PanelDraft,
        image_path: Path | None,
        x: int,
        y: int,
        width: int,
        height: int,
    ) -> None:
        if image_path and Path(image_path).exists():
            with Image.open(image_path) as source:
                image = ImageOps.fit(
                    source.convert("RGB"),
                    (width, height),
                    method=Image.Resampling.LANCZOS,
                )
            page.paste(image, (x, y))
        else:
            draw.rectangle((x, y, x + width, y + height), fill=(229, 231, 235))
            draw.text(
                (x + width // 2, y + height // 2),
                "Image indisponible",
                fill=(107, 114, 128),
                font=self._font(22),
                anchor="mm",
            )

        draw.rectangle((x, y, x + width, y + height), outline=(17, 24, 39), width=4)

        if panel.dialogue and panel.dialogue.strip():
            self._draw_bubble(draw, panel.dialogue.strip(), x, y, width)

    def _draw_bubble(
        self,
        draw: ImageDraw.ImageDraw,
        dialogue: str,
        panel_x: int,
        panel_y: int,
        panel_width: int,
    ) -> None:
        font = self._font(20)
        padding = 16
        line_height = 28
        max_text_width = panel_width - 2 * padding - 24

        lines = self._wrap(dialogue, font, max_text_width)[:5]
        if not lines:
            return

        text_width = max(self._text_width(line, font) for line in lines)
        bubble_width = min(panel_width - 24, text_width + 2 * padding)
        bubble_height = len(lines) * line_height + 2 * padding

        bubble_x = panel_x + (panel_width - bubble_width) // 2
        bubble_y = panel_y + 16
        draw.rounded_rectangle(
            (
                bubble_x,
                bubble_y,
                bubble_x + bubble_width,
                bubble_y + bubble_height,
            ),
            radius=18,
            fill=(255, 255, 255),
            outline=(17, 24, 39),
            width=3,
        )
        for index, line in enumerate(lines):
            draw.text(
                (bubble_x + padding, bubble_y + padding + index * line_height),
                line,
                fill=(17, 24, 39),
                font=font,
            )

    # ------------------------------------------------------------------
    # Utilitaires texte
    # ------------------------------------------------------------------

    def _font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        key = (size, bold)
        if key not in self._font_cache:
            font = None
            for candidate in _FONT_CANDIDATES[bold]:
                if Path(candidate).exists():
                    font = ImageFont.truetype(candidate, size=size)
                    break
            if font is None:
                font = ImageFont.load_default(size=size)
            self._font_cache[key] = font
        return self._font_cache[key]

    def _text_width(self, text: str, font: ImageFont.FreeTypeFont) -> int:
        return int(ImageDraw.Draw(Image.new("RGB", (1, 1))).textlength(text, font=font))

    def _wrap(
        self, text: str, font: ImageFont.FreeTypeFont, max_width: int
    ) -> list[str]:
        """Découpe un texte en lignes qui tiennent dans ``max_width``."""
        words = text.split()
        if not words:
            return []

        lines: list[str] = []
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if self._text_width(candidate, font) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
            # Mot plus large que la ligne : découpe caractère par caractère
            if self._text_width(word, font) > max_width:
                chunk = ""
                for char in word:
                    if self._text_width(chunk + char, font) <= max_width:
                        chunk += char
                    else:
                        lines.append(chunk)
                        chunk = char
                current = chunk
            else:
                current = word
        if current:
            lines.append(current)
        return lines

    @staticmethod
    def _flatten_panels(story: StoryDraft) -> list[PanelDraft]:
        return [panel for scene in story.scenes for panel in scene.panels]
