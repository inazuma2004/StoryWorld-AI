"""Construction de prompts déterministes pour le LLM."""

from __future__ import annotations

import json

from storyworld.domain.models import StoryBrief


def build_story_prompt(brief: StoryBrief, schema: dict) -> str:
    """Génère le prompt envoyé au LLM pour produire un storyboard structuré."""
    schema_json = json.dumps(schema, indent=2, ensure_ascii=False)
    return f"""Tu es un scénariste de bande dessinée. Génère un storyboard en français.

IDEE : {brief.idea}
GENRE : {brief.genre}
STYLE VISUEL : {brief.style}
PUBLIC CIBLE : {brief.audience}
LANGUE : {brief.language}
NOMBRE DE CASES : {brief.panel_count}

Règles :
- Réponds UNIQUEMENT avec un JSON valide, sans texte avant ni après.
- Respecte le schéma JSON suivant : {schema_json}
- Chaque dialogue doit faire au maximum 120 caractères.
- Les images ne doivent JAMAIS contenir de texte : le texte sera ajouté en bulles séparément.
- Inclus : titre, synopsis, personnages (nom, rôle, personnalité, vêtements, couleurs, attributs), scènes avec cases (description visuelle, dialogue, personnages).
- Langue de sortie : {brief.language}.
""".strip()
