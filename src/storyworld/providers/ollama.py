"""Provider texte Ollama (LLM local, sortie JSON structurée)."""

from __future__ import annotations

import re

import httpx

from storyworld.providers.base import ProviderError
from storyworld.services.json_repair import parse_json_object, repair_json_object

_SCHEMA_SECTION = re.compile(
    r"^- Respecte le schéma JSON suivant :.*?(?=^- )", re.MULTILINE | re.DOTALL
)


class OllamaTextProvider:
    """Génère un objet JSON structuré via une instance Ollama locale.

    Ollama reçoit le schéma Pydantic dans ``format`` (sortie structurée) ; le
    schéma est retiré du prompt pour éviter que les petits modèles le recopient.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "llama3.2:1b",
        timeout: float = 180.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def generate_json(
        self, prompt: str, schema: type, *, timeout: float | None = None
    ) -> dict:
        json_schema = (
            schema.model_json_schema() if hasattr(schema, "model_json_schema") else None
        )
        cleaned_prompt = _SCHEMA_SECTION.sub("", prompt)

        payload: dict = {
            "model": self.model,
            "prompt": cleaned_prompt,
            "stream": False,
            "options": {"temperature": 0.4, "num_predict": 1600},
        }
        if json_schema:
            payload["format"] = json_schema
        else:
            payload["format"] = "json"

        try:
            response = self._client.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=timeout or self.timeout,
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

        try:
            return parse_json_object(text)
        except ValueError:
            pass

        repaired = repair_json_object(text)
        if repaired is not None:
            return repaired

        raise ProviderError(
            f"Réponse Ollama invalide (non JSON) : {text[:200]}..."
        )
