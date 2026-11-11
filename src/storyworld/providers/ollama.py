"""Provider texte Ollama (LLM local)."""

from __future__ import annotations

import httpx

from storyworld.providers.base import ProviderError
from storyworld.services.json_repair import parse_json_object, repair_json_object


class OllamaTextProvider:
    """Génère un objet JSON structuré via une instance Ollama locale."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "llama3.2:1b"):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(timeout=60.0)

    def generate_json(
        self, prompt: str, schema: type, *, timeout: float = 60.0
    ) -> dict:
        del schema  # le schéma est transmis dans le prompt (construit par prompt_builder)
        try:
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                },
                timeout=timeout,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError(f"Timeout Ollama : {exc}") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Erreur réseau Ollama : {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"Erreur HTTP Ollama {exc.response.status_code}"
            ) from exc

        data = response.json()
        text = data.get("response", "") or ""

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
            f"Réponse Ollama invalide (non JSON) : {text[:200]}..."
        )
