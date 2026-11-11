"""Implémentations Mock déterministes (tests, démo hors-ligne)."""

from __future__ import annotations

from typing import Any

import structlog

from storyworld.providers.base import ImageProvider, ProviderError, TextProvider

logger = structlog.get_logger(__name__)


class MockTextProvider:
    """Retourne un storyboard français déterministe de 4 cases."""

    def generate_json(
        self, prompt: str, schema: type[Any], *, timeout: float = 60.0
    ) -> dict:
        del prompt, timeout  # non utilisé par le Mock
        return {
            "title": "Le robot du jardin",
            "synopsis": "Une étudiante découvre un robot abandonné dans un jardin de Casablanca et décide de le réparer.",
            "characters": [
                {
                    "name": "Leila",
                    "role": "héroïne",
                    "personnalite": "curieuse et déterminée",
                    "vetements": "sweat à capuche et jean",
                    "couleurs": "bleu marine et gris",
                    "attributs_distinctifs": "lunettes de réparation",
                },
                {
                    "name": "Robot",
                    "role": "compagnon",
                    "personnalite": "calme et serviable",
                    "vetements": "corps métallique argenté",
                    "couleurs": "argent et bleu",
                    "attributs_distinctifs": "yeux bleus lumineux",
                }
            ],
            "scenes": [
                {
                    "numero": 1,
                    "description": "Leila marche dans les ruelles de Casablanca au coucher du soleil.",
                    "panels": [
                        {
                            "numero": 1,
                            "description_visuelle": "Ruelle étroite, murs ocre, lumière orangée, Leila de dos.",
                            "dialogue": "Il parait que quelque chose traine ici.",
                            "personnages": ["Leila"],
                        }
                    ],
                },
                {
                    "numero": 2,
                    "description": "Leila découvre le robot caché sous une bâche.",
                    "panels": [
                        {
                            "numero": 2,
                            "description_visuelle": "Robot argenté sous une bâche déchirée, yeux bleus allumés.",
                            "dialogue": "Tu fonctionnes encore ?",
                            "personnages": ["Leila", "Robot"],
                        }
                    ],
                },
                {
                    "numero": 3,
                    "description": "Leila répare le robot avec ses outils.",
                    "panels": [
                        {
                            "numero": 3,
                            "description_visuelle": "Leila avec un tournevis, étincelles près du robot.",
                            "dialogue": "Presque réparé, tiens bon.",
                            "personnages": ["Leila", "Robot"],
                        }
                    ],
                },
                {
                    "numero": 4,
                    "description": "Le robot repart, réparé, sous le regard émerveillé de Leila.",
                    "panels": [
                        {
                            "numero": 4,
                            "description_visuelle": "Robot qui marche, Leila qui sourit, soleil couchant.",
                            "dialogue": "Merci, Leila.",
                            "personnages": ["Leila", "Robot"],
                        }
                    ],
                },
            ],
        }


class MockImageProvider:
    """Génère un PNG 512x512 aplat de couleur avec le numéro de case."""

    def __init__(self):
        self.call_count = 0

    def generate(
        self,
        prompt: str,
        *,
        size: tuple[int, int] = (1024, 1024),
        seed: int | None = None,
    ) -> bytes:
        self.call_count += 1
        del prompt, seed
        import io

        from PIL import Image

        img = Image.new("RGB", size, color=(200, 200, 200))
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        return buffer.getvalue()


def build_text_provider(settings) -> TextProvider:  # type: ignore[valid-type]
    if settings.text_provider == "mock":
        return MockTextProvider()
    raise ProviderError(f"Provider texte non encore implémenté : {settings.text_provider}")


def build_image_provider(settings) -> ImageProvider:  # type: ignore[valid-type]
    if settings.image_provider == "mock":
        return MockImageProvider()
    raise ProviderError(f"Provider image non encore implémenté : {settings.image_provider}")
