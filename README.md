# StoryWorld AI

Plateforme intelligente de création de bandes dessinées et d'histoires
illustrées par IA générative.

## Installation

```powershell
python -m venv --system-site-packages .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
cp .env.example .env
```

## Lancement

```powershell
streamlit run src/storyworld/ui/app.py
```

## Tests

```powershell
pytest
ruff check src tests
```
