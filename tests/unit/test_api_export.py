"""Tests des routes d'export PDF et images."""

import io
import zipfile

from pypdf import PdfReader


def _generate(client) -> dict:
    response = client.post(
        "/api/v1/generate",
        json={
            "idea": "un robot jardinier",
            "genre": "aventure",
            "style": "manga",
            "audience": "enfant",
            "language": "fr",
            "panel_count": 4,
        },
    )
    assert response.status_code == 200
    return response.json()


def test_generate_retourne_project_id(client):
    data = _generate(client)
    assert data["project_id"]


def test_export_pdf(client):
    data = _generate(client)

    response = client.get(f"/api/v1/projects/{data['project_id']}/export/pdf")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    reader = PdfReader(io.BytesIO(response.content))
    text = "".join(page.extract_text() or "" for page in reader.pages)
    assert data["title"] in text
    assert data["scenes"][0]["panels"][0]["dialogue"] in text


def test_export_images_zip(client):
    data = _generate(client)

    response = client.get(f"/api/v1/projects/{data['project_id']}/export/images")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"
    with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
        names = sorted(archive.namelist())
        total_panels = sum(len(scene["panels"]) for scene in data["scenes"])
        assert len(names) == total_panels
        assert all(name.startswith("panel_") and name.endswith(".png") for name in names)


def test_export_projet_inconnu_404(client):
    response = client.get("/api/v1/projects/inconnu/export/pdf")
    assert response.status_code == 404
