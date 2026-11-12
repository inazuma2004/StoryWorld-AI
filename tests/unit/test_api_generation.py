"""Tests de la route de génération."""


def test_generate_story(client):
    payload = {
        "idea": "un robot jardinier",
        "genre": "aventure",
        "style": "manga",
        "audience": "enfant",
        "language": "fr",
        "panel_count": 4,
    }
    response = client.post("/api/v1/generate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "scenes" in data

    # Chaque panel expose une image réellement servie par l'API
    total_panels = sum(len(s["panels"]) for s in data["scenes"])
    for scene in data["scenes"]:
        for panel in scene["panels"]:
            url = panel.get("image_url", "")
            assert url.startswith("/media/panels/"), url
            image = client.get(url)
            assert image.status_code == 200, url
            assert image.headers["content-type"] == "image/png"
            assert image.content.startswith(b"\x89PNG")
    assert total_panels >= 1
