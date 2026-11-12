# StoryWorld AI

Plateforme de création de bandes dessinées par IA générative : à partir d'une
idée, l'application produit un scénario structuré, des illustrations par case,
des bulles de dialogue, puis exporte le résultat en PDF et en images.

Interface et contenus en français.

## Fonctionnalités

- Scénario structuré : titre, synopsis, personnages, scènes et cases (1 à 12).
- Validation narrative : titre, dialogues non vides (≤ 120 caractères),
  personnages référencés cohérents.
- Illustrations par case avec cache par hash du prompt (pas d'appel redondant).
- Providers interchangeables :
  - texte : `mock` (déterministe, hors ligne), `gemini`, `ollama` ;
  - images : `mock`, `hf` (Hugging Face), `pollinations`.
- Composition de planches A4 (4 cases par page) avec bulles de dialogue.
- Export PDF (page texte extractible + planches) et archive ZIP des cases.
- Persistance SQLite des projets et des médias sur disque.
- Interface React + Vite, API FastAPI.

## Architecture

```
src/storyworld/
  api/main.py            API FastAPI (génération, médias, exports)
  domain/                modèles Pydantic, validation narrative
  providers/             providers texte/image + registre
  services/              orchestration, prompts, cache, composition, export
  storage/               SQLite + SQLAlchemy
frontend/                React + Vite
tests/                   unitaires, intégration, API
```

## Installation

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

## Lancement

Backend (port 8000) :

```powershell
.\.venv\Scripts\python.exe -m uvicorn storyworld.api.main:app --port 8000
```

Frontend (port 5173) :

```powershell
npm --prefix frontend install
npm --prefix frontend run dev
```

Ouvrir <http://localhost:5173>.

## Configuration

Les variables sont lues depuis `.env` avec le préfixe `STORYWORLD_`
(voir `.env.example`). Par défaut, tout fonctionne hors ligne avec les
providers `mock`.

| Variable | Valeurs | Défaut |
|---|---|---|
| `STORYWORLD_TEXT_PROVIDER` | `mock`, `gemini`, `ollama` | `mock` |
| `STORYWORLD_IMAGE_PROVIDER` | `mock`, `hf`, `pollinations` | `mock` |
| `STORYWORLD_GEMINI_API_KEY` | clé Gemini | vide |
| `STORYWORLD_HF_TOKEN` | token Hugging Face | vide |
| `STORYWORLD_POLLINATIONS_TOKEN` | token optionnel Pollinations | vide |
| `STORYWORLD_OLLAMA_BASE_URL` | URL Ollama | `http://localhost:11434` |
| `STORYWORLD_DATA_DIR` | dossier de données | `data` |

Aucun secret ne doit être commité : seul `.env.example` est versionné.

## Tests et qualité

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -q
ruff check src tests
npm --prefix frontend run build
```

L'interface est vérifiée avec Playwright : chargement des images, téléchargement
PDF/ZIP, état d'erreur et affichage mobile.

## Limites connues

- Les providers réels nécessitent une clé API (Gemini, Hugging Face) ou une
  instance Ollama locale ; Pollinations peut appliquer des quotas anonymes.
- Le provider `mock` produit des aplats de couleur : il sert aux tests et aux
  démonstrations hors ligne, pas à un rendu artistique.
