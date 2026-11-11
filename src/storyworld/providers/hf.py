"""Provider image Hugging Face Inference API."""

from __future__ import annotations

import httpx

from storyworld.providers.base import ProviderError


class HuggingFaceImageProvider:
    """Génère une image via l'API Inference de Hugging Face."""

    def __init__(
        self,
        token: str,
        model: str = "stabilityai/stable-diffusion-xl-base-1.0",
        base_url: str = "https://api-inference.huggingface.co",
        client: httpx.Client | None = None,
    ):
        self.token = token
        self.model = model
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.Client(timeout=120.0)

    def generate(
        self,
        prompt: str,
        *,
        size: tuple[int, int] = (1024, 1024),
        seed: int | None = None,
    ) -> bytes:
        del size, seed  # non supportés par l'Inference API simple (à étendre plus tard)
        url = f"{self.base_url}/models/{self.model}"
        try:
            response = self._client.post(
                url,
                headers={"Authorization": f"Bearer {self.token}"},
                json={"inputs": prompt},
                timeout=120.0,
            )
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ProviderError(f"Timeout Hugging Face : {exc}") from exc
        except httpx.RequestError as exc:
            raise ProviderError(f"Erreur réseau Hugging Face : {exc}") from exc
        except httpx.HTTPStatusError as exc:
            raise ProviderError(
                f"Erreur HTTP Hugging Face {exc.response.status_code}"
            ) from exc

        return response.content
