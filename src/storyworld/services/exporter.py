"""Export vers PDF et archive d'images."""

from __future__ import annotations

import textwrap
import zipfile
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from storyworld.domain.models import StoryDraft


class Exporter:
    """Produit un PDF lisible (texte + planches) et une archive des cases."""

    def export_pdf(
        self,
        story: StoryDraft,
        pages: list[Path],
        output: Path,
    ) -> Path:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        pdf = canvas.Canvas(str(output), pagesize=A4)
        pdf.setTitle(story.title)
        pdf.setAuthor("StoryWorld AI")

        self._draw_text_page(pdf, story)
        pdf.showPage()

        page_width, page_height = A4
        for page_path in pages:
            pdf.drawImage(
                str(page_path),
                0,
                0,
                width=page_width,
                height=page_height,
                preserveAspectRatio=True,
                anchor="c",
            )
            pdf.showPage()

        pdf.save()
        return output

    def _draw_text_page(self, pdf: canvas.Canvas, story: StoryDraft) -> None:
        _width, height = A4
        margin = 50
        y = height - 70

        pdf.setFont("Helvetica-Bold", 20)
        pdf.drawString(margin, y, story.title)
        y -= 30

        pdf.setFont("Helvetica", 11)
        for line in textwrap.wrap(story.synopsis, width=95):
            pdf.drawString(margin, y, line)
            y -= 16
        y -= 10

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(margin, y, "Personnages")
        y -= 20
        pdf.setFont("Helvetica", 11)
        for character in story.characters:
            line = f"- {character.name} ({character.role}) : {character.personnalite}"
            for wrapped in textwrap.wrap(line, width=95):
                pdf.drawString(margin, y, wrapped)
                y -= 15
        y -= 10

        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(margin, y, "Dialogue")
        y -= 20
        pdf.setFont("Helvetica", 11)

        panel_number = 0
        for scene in story.scenes:
            for panel in scene.panels:
                panel_number += 1
                line = f"Case {panel_number} : {panel.dialogue}"
                for wrapped in textwrap.wrap(line, width=95):
                    if y < 60:
                        pdf.showPage()
                        y = height - 60
                        pdf.setFont("Helvetica", 11)
                    pdf.drawString(margin, y, wrapped)
                    y -= 15
                y -= 4

    def export_png_zip(
        self,
        story: StoryDraft,
        images: dict[int, Path],
        output: Path,
    ) -> Path:
        output = Path(output)
        output.parent.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(output, "w") as archive:
            for panel_index, image_path in images.items():
                archive.write(image_path, arcname=f"panel_{panel_index}.png")
        return output
