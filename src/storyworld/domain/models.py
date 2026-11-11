"""Modèles de domaine : structures de données du projet StoryWorld AI."""

from typing import Literal

from pydantic import BaseModel, Field

Genre = Literal["aventure", "fantastique", "science-fiction", "comedie", "educatif"]
Style = Literal["manga", "cartoon", "aquarelle", "comics"]
Audience = Literal["enfant", "adolescent", "adulte"]
Language = Literal["fr", "en", "ar"]
PanelStatus = Literal["pending", "generated", "error"]


class StoryBrief(BaseModel):
    idea: str = Field(min_length=1)
    genre: Genre
    style: Style
    audience: Audience
    language: Language
    panel_count: int = Field(ge=1, le=12)


class CharacterDraft(BaseModel):
    name: str = Field(min_length=1)
    role: str = Field(min_length=1)
    personnalite: str = Field(min_length=1)
    vetements: str = Field(min_length=1)
    couleurs: str = Field(min_length=1)
    attributs_distinctifs: str = Field(min_length=1)


class PanelDraft(BaseModel):
    numero: int = Field(ge=1)
    description_visuelle: str = Field(min_length=1)
    dialogue: str = Field(min_length=1, max_length=120)
    personnages: list[str] = Field(default_factory=list)


class SceneDraft(BaseModel):
    numero: int = Field(ge=1)
    description: str = Field(min_length=1)
    panels: list[PanelDraft] = Field(min_length=1)


class StoryDraft(BaseModel):
    title: str = Field(min_length=1)
    synopsis: str = Field(min_length=1)
    characters: list[CharacterDraft] = Field(min_length=1)
    scenes: list[SceneDraft] = Field(min_length=1)
