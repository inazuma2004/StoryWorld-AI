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
| `STORYWORLD_OLLAMA_MODEL` | modèle Ollama | `llama3.2:1b` |
| `STORYWORLD_OLLAMA_TIMEOUT` | délai max par génération (s) | `180` |
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

## Laboratoire IA (VAE / DCGAN)

L'onglet « Laboratoire IA » de l'interface compare deux modèles entraînés
localement sur Fashion-MNIST (images 28×28, noir et blanc) :

- **VAE** : reconstructions (originales en haut, reconstruites en bas) et
  interpolation linéaire entre deux vecteurs latents ;
- **DCGAN** : échantillons produits par le générateur après entraînement.

Ces modèles sont **expérimentaux** : ils illustrent l'encodeur/décodeur et le
jeu générateur/discriminateur, mais ne génèrent pas les cases de la BD.

Entraînement complet en ligne de commande (CPU, quelques minutes) :

```powershell
.\.venv\Scripts\python.exe -m storyworld.lab.train --model vae --epochs 10 --output-dir data/lab
.\.venv\Scripts\python.exe -m storyworld.lab.train --model dcgan --epochs 10 --output-dir data/lab
```

Options utiles : `--epochs`, `--batch-size`, `--limit-batches` (smoke test),
`--latent-dim`, `--device auto|cpu|cuda`, `--data-dir`, `--output-dir`.

Les artefacts sont écrits dans `data/lab/` (`vae.pt`, `dcgan.pt`,
`vae_history.json`, `dcgan_history.json`, grilles PNG) puis servis par l'API
sur `/lab-media/`. Endpoints :

| Méthode | Route | Rôle |
|---|---|---|
| `GET` | `/api/v1/lab/status` | disponibilité des artefacts + historiques |
| `POST` | `/api/v1/lab/train/{vae\|dcgan}` | entraînement court (démo, borné) |

Le bouton « Entraîner (démo) » lance 1 epoch sur 10 lots : il vérifie le
pipeline, pas la qualité visuelle. Un entraînement complet sur GPU (Colab,
Kaggle) donne de meilleurs résultats ; `--device auto` sélectionne CUDA s'il
est disponible.

## Limites connues

- Les providers réels nécessitent une clé API (Gemini, Hugging Face) ou une
  instance Ollama locale ; Pollinations peut appliquer des quotas anonymes.
- Le provider `mock` produit des aplats de couleur : il sert aux tests et aux
  démonstrations hors ligne, pas à un rendu artistique.
