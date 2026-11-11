"""Providers : abstraction texte et image pour les modèles génératifs."""

from typing import Protocol, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class TextProvider(Protocol):
    """Génère un objet JSON structuré à partir d'un prompt."""

    def generate_json(
        self, prompt: str, schema: type[T], *, timeout: float = 60.0
    ) -> dict: ...


class ImageProvider(Protocol):
    """Génère une image à partir d'un prompt textuel."""

    def generate(
        self,
        prompt: str,
        *,
        size: tuple[int, int] = (1024, 1024),
        seed: int | None = None,
    ) -> bytes: ...


class ProviderError(RuntimeError):
    """Erreur retournée par un fournisseur (quota, timeout, panne)."""
