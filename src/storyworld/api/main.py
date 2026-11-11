"""Application FastAPI : exposition des services StoryWorld."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from storyworld.config import Settings
from storyworld.domain.models import StoryBrief, StoryDraft
from storyworld.providers.mock import MockImageProvider, MockTextProvider
from storyworld.services.story_generator import StoryGenerator
from storyworld.storage import Repository, create_session_factory

app = FastAPI(title="StoryWorld AI API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Dépendances
# ---------------------------------------------------------------------------

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings(text_provider="mock", image_provider="mock")
    return _settings


def get_repository(settings: Annotated[Settings, Depends(get_settings)]) -> Repository:
    db_path = settings.data_dir / "api.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    session_factory = create_session_factory(db_path)
    return Repository(session_factory)


# ---------------------------------------------------------------------------
# Schémas d'entrée/sortie API
# ---------------------------------------------------------------------------


class ProjectIn(BaseModel):
    title: str
    story: dict


class ProjectOut(BaseModel):
    id: str
    title: str
    status: str


class GenerationIn(BaseModel):
    idea: str
    genre: str
    style: str
    audience: str
    language: str = "fr"
    panel_count: int = 4


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/api/v1/projects", response_model=list[ProjectOut])
def list_projects(repo: Annotated[Repository, Depends(get_repository)]):
    return [{"id": p["id"], "title": p["title"], "status": p["status"]} for p in repo.list_projects()]


@app.post("/api/v1/projects", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectIn, repo: Annotated[Repository, Depends(get_repository)]):
    try:
        story = StoryDraft.model_validate(payload.story)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Histoire invalide : {exc}") from exc
    project_id = repo.save_project(story)
    return {"id": project_id, "title": payload.title, "status": "draft"}


@app.post("/api/v1/generate", response_model=dict)
def generate_story(payload: GenerationIn, repo: Annotated[Repository, Depends(get_repository)]):
    settings = get_settings()
    generator = StoryGenerator(
        MockTextProvider(),
        MockImageProvider(),
        repo,
        settings,
    )
    brief = StoryBrief(
        idea=payload.idea,
        genre=payload.genre,  # type: ignore[arg-type]
        style=payload.style,  # type: ignore[arg-type]
        audience=payload.audience,  # type: ignore[arg-type]
        language=payload.language,  # type: ignore[arg-type]
        panel_count=payload.panel_count,
    )
    try:
        story = generator.generate(brief)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    return story.model_dump()
