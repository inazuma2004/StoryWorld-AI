"""Provider image Pollinations.ai (génération sans clé API)."""

from __future__ import annotations

from urllib.parse import quote

import httpx

from storyworld.providers.base import ProviderError


class PollinationsImageProvider:
    """Génère une image via l'API HTTP publique de Pollinations."""

    def __init__(
        self,
        base_url: str = "https://image.pollinations.ai",
        model: str = "flux",
        token: str | None = None,
        client: httpx.Client | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.token = token
        self._client = client or httpx.Client(timeout=120.0)

    def generate(
        self,
        prompt: str,
        *,
        size: tuple[int, int] = (1024, 1024),
        seed: int | None = None,
    ) -> bytes:
        width, height = size
        params: dict[str, str | int] = {
            "width": width,
            "height": height,
            "model": self.model,
            "nologo": "true",
        }
        if seed is not None:
            params["seed"] = seed

        headers = {"Authorization": f"Bearer {self.token}"} if self.token else {}
        url = f"{self.base_url}/prompt/{quote(prompt, safe='')}"
        try:
            response = self._client.get(
                url, params=params, headers=headers, timeout=120.0
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError(f"Timeout Pollinations : {exc}") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Erreur réseau Pollinations : {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"Erreur HTTP Pollinations {exc.response.status_code}"
            ) from exc

        if not response.content:
            raise ProviderError("Réponse Pollinations vide")
        return response.content
