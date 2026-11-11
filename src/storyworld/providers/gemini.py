"""Provider texte Gemini (Google Generative AI)."""

from __future__ import annotations

from typing import Any, TypeVar

from google import genai
from pydantic import BaseModel

from storyworld.providers.base import ProviderError
from storyworld.services.json_repair import parse_json_object, repair_json_object

T = TypeVar("T", bound=BaseModel)


class GeminiTextProvider:
    """Génère un objet JSON structuré via l'API Gemini."""

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-2.5-flash",
        client: Any = None,
    ):
        self.api_key = api_key
        self.model = model
        self._client = client or genai.Client(api_key=api_key)

    def generate_json(
        self, prompt: str, schema: type[T], *, timeout: float = 60.0
    ) -> dict:
        del schema  # le schéma est transmis dans le prompt (construit par prompt_builder)
        try:
            response = self._client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
            text = response.text or ""
        except Exception as exc:
            raise ProviderError(f"Erreur Gemini : {exc}") from exc

        # 1. parsing direct
        try:
            return parse_json_object(text)
        except ValueError:
            pass

        # 2. réparation (markdown, virgule finale, etc.)
        repaired = repair_json_object(text)
        if repaired is not None:
            return repaired

        raise ProviderError(
            f"Réponse Gemini invalide (non JSON) : {text[:200]}..."
        )
