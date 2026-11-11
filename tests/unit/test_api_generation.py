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
