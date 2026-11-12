"""Application FastAPI : exposition des services StoryWorld."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from storyworld.config import Settings
from storyworld.domain.models import StoryBrief, StoryDraft
from storyworld.domain.validation import validate_story
from storyworld.providers.registry import build_image_provider, build_text_provider
from storyworld.services.composer import Composer
from storyworld.services.exporter import Exporter
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
# Fichiers médias (images générées) servis au frontend
# ---------------------------------------------------------------------------

from pathlib import Path

_media_dir = Settings().data_dir / "media"
_media_dir.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=str(_media_dir)), name="media")

# ---------------------------------------------------------------------------
# Dépendances
# ---------------------------------------------------------------------------

_settings: Settings | None = None


def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
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
    text_provider = build_text_provider(settings)
    image_provider = build_image_provider(settings)
    generator = StoryGenerator(
        text_provider,
        image_provider,
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
        issues = validate_story(story, settings)
        if issues:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Problèmes détectés dans le scénario généré",
                    "issues": [
                        {
                            "code": i.code,
                            "message": i.message,
                            "panel_index": i.panel_index,
                        }
                        for i in issues
                    ],
                },
            )
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    result = story.model_dump()
    media_root = (settings.data_dir / "media").resolve()
    for scene in result["scenes"]:
        for panel in scene["panels"]:
            if not panel.get("image_path"):
                continue
            image_path = Path(panel["image_path"]).resolve()
            try:
                relative = image_path.relative_to(media_root)
            except ValueError:
                relative = Path(image_path.name)
            panel["image_url"] = f"/media/{relative.as_posix()}"
    return result


# ---------------------------------------------------------------------------
# Export PDF / images
# ---------------------------------------------------------------------------


def _flatten_panels(story: StoryDraft):
    return [panel for scene in story.scenes for panel in scene.panels]


def _panel_images(story: StoryDraft) -> dict[int, Path]:
    images: dict[int, Path] = {}
    for index, panel in enumerate(_flatten_panels(story), start=1):
        if panel.image_path:
            path = Path(panel.image_path)
            if path.exists():
                images[index] = path
    return images


def _safe_filename(title: str) -> str:
    cleaned = "".join(
        char if char.isalnum() or char in ("-", "_") else "-" for char in title
    ).strip("-")
    return cleaned or "storyworld"


def _get_story_or_404(repo: Repository, project_id: str) -> StoryDraft:
    story = repo.get_project(project_id)
    if story is None:
        raise HTTPException(status_code=404, detail="Projet introuvable")
    return story


@app.get("/api/v1/projects/{project_id}/export/pdf")
def export_project_pdf(
    project_id: str,
    repo: Annotated[Repository, Depends(get_repository)],
):
    story = _get_story_or_404(repo, project_id)
    settings = get_settings()
    export_dir = settings.data_dir / "exports" / project_id

    pages = Composer().compose_story(story, _panel_images(story), export_dir)
    pdf_path = Exporter().export_pdf(story, pages, export_dir / "story.pdf")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"{_safe_filename(story.title)}.pdf",
    )


@app.get("/api/v1/projects/{project_id}/export/images")
def export_project_images(
    project_id: str,
    repo: Annotated[Repository, Depends(get_repository)],
):
    story = _get_story_or_404(repo, project_id)
    settings = get_settings()
    export_dir = settings.data_dir / "exports" / project_id

    zip_path = Exporter().export_png_zip(
        story, _panel_images(story), export_dir / "images.zip"
    )
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename=f"{_safe_filename(story.title)}-images.zip",
    )
