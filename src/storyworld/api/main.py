"""Application FastAPI : exposition des services StoryWorld."""

from __future__ import annotations

import json
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from storyworld.config import Settings
from storyworld.domain.models import StoryBrief, StoryDraft
from storyworld.domain.validation import validate_story
from storyworld.lab.models import VAE, DCGANDiscriminator, DCGANGenerator
from storyworld.lab.train import (
    make_fashion_mnist_loader,
    resolve_device,
    save_dcgan_samples,
    save_vae_samples,
    train_dcgan,
    train_vae,
)
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

_lab_dir = Settings().data_dir / "lab"
_lab_dir.mkdir(parents=True, exist_ok=True)
app.mount("/lab-media", StaticFiles(directory=str(_lab_dir)), name="lab-media")

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


# ---------------------------------------------------------------------------
# Laboratoire VAE / DCGAN
# ---------------------------------------------------------------------------


class LabTrainIn(BaseModel):
    epochs: int = 1
    limit_batches: int = 10
    batch_size: int = 32
    latent_dim: int = 16


def _lab_samples(settings: Settings) -> dict:
    lab_dir = settings.data_dir / "lab"
    vae_samples = {
        "reconstructions": "/lab-media/vae_reconstructions.png",
        "interpolation": "/lab-media/vae_interpolation.png",
    }
    vae_available = all((lab_dir / Path(url).name).exists() for url in vae_samples.values())

    dcgan_samples = {"samples": "/lab-media/dcgan_samples.png"}
    dcgan_available = (lab_dir / "dcgan_samples.png").exists()

    return {
        "vae": {
            "available": vae_available,
            "samples": vae_samples if vae_available else {},
            "history": _read_json(lab_dir / "vae_history.json"),
        },
        "dcgan": {
            "available": dcgan_available,
            "samples": dcgan_samples if dcgan_available else {},
            "history": _read_json(lab_dir / "dcgan_history.json"),
        },
    }


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


@app.get("/api/v1/lab/status")
def lab_status():
    return _lab_samples(get_settings())


@app.post("/api/v1/lab/train/{model}")
def lab_train(model: Literal["vae", "dcgan"], payload: LabTrainIn | None = None):
    payload = payload or LabTrainIn()
    settings = get_settings()
    lab_dir = settings.data_dir / "lab"
    lab_dir.mkdir(parents=True, exist_ok=True)

    epochs = max(1, min(payload.epochs, 3))
    limit_batches = max(1, min(payload.limit_batches, 200))
    batch_size = max(4, min(payload.batch_size, 256))
    latent_dim = max(2, min(payload.latent_dim, 128))

    loader = make_fashion_mnist_loader(
        settings.data_dir / "fashion_mnist", batch_size=batch_size
    )
    device = resolve_device("auto")

    if model == "vae":
        vae = VAE(latent_dim=latent_dim)
        history = train_vae(
            vae,
            loader,
            epochs=epochs,
            device=device,
            limit_batches=limit_batches,
            checkpoint_path=lab_dir / "vae.pt",
        )
        samples = save_vae_samples(vae, loader, lab_dir, device)
        history_path = lab_dir / "vae_history.json"
        sample_urls = {
            "reconstructions": "/lab-media/vae_reconstructions.png",
            "interpolation": "/lab-media/vae_interpolation.png",
        }
    else:
        generator = DCGANGenerator(latent_dim=latent_dim)
        discriminator = DCGANDiscriminator()
        history = train_dcgan(
            generator,
            discriminator,
            loader,
            epochs=epochs,
            device=device,
            limit_batches=limit_batches,
            checkpoint_path=lab_dir / "dcgan.pt",
        )
        samples = {"samples": save_dcgan_samples(generator, lab_dir, device)}
        history_path = lab_dir / "dcgan_history.json"
        sample_urls = {"samples": "/lab-media/dcgan_samples.png"}

    import json

    history_path.write_text(json.dumps(history, indent=2), encoding="utf-8")
    return {
        "model": model,
        "device": device,
        "history": history,
        "samples": sample_urls,
        "files": {name: str(path) for name, path in samples.items()},
    }
