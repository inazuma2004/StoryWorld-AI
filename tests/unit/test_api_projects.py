"""Tests des routes API projets."""

def test_list_projects_empty(client):
    response = client.get("/api/v1/projects")
    assert response.status_code == 200
    assert response.json() == []


def test_create_project(client):
    payload = {
        "title": "Ma première BD",
        "story": {
            "title": "Ma première BD",
            "synopsis": "Un test.",
            "characters": [
                {
                    "name": "Leila",
                    "role": "heroine",
                    "personnalite": "curieuse",
                    "vetements": "jean",
                    "couleurs": "bleu",
                    "attributs_distinctifs": "lunettes",
                }
            ],
            "scenes": [
                {
                    "numero": 1,
                    "description": "Scène de test.",
                    "panels": [
                        {
                            "numero": 1,
                            "description_visuelle": "Un personnage.",
                            "dialogue": "Bonjour.",
                            "personnages": [],
                        }
                    ],
                }
            ],
        },
    }
    response = client.post("/api/v1/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Ma première BD"
    assert "id" in data
