"""Export vers PDF et archive d'images."""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from storyworld.domain.models import StoryDraft


class Exporter:
    def export_pdf(
        self,
        story: StoryDraft,
        pages: list[Path],
        output: Path,
    ) -> Path:
        c = canvas.Canvas(str(output), pagesize=A4)
        c.setTitle(story.title)
        c.drawString(50, 800, story.title)
        c.drawString(50, 780, story.synopsis[:100])
        y = 740
        for scene in story.scenes:
            for panel in scene.panels:
                c.drawString(50, y, panel.dialogue[:80])
                y -= 40
                if y < 100:
                    c.showPage()
                    y = 800
        c.save()
        return output

    def export_png_zip(
        self,
        story: StoryDraft,
        images: dict[int, Path],
        output: Path,
    ) -> Path:
        import zipfile

        with zipfile.ZipFile(output, "w") as zf:
            for panel_index, image_path in images.items():
                zf.write(image_path, arcname=f"panel_{panel_index}.png")
        return output
