"""Construction de prompts déterministes pour le LLM."""

from __future__ import annotations

import json

from storyworld.domain.models import (
    CharacterDraft,
    SceneDraft,
    StoryBrief,
    Style,
)


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


def build_image_prompt(
    scene: SceneDraft,
    character: CharacterDraft,
    style: Style,
    panel_index: int,
) -> str:
    """Génère le prompt pour l'illustration d'une case (modèle de diffusion).

    Le prompt inclut la description de la scène, la description visuelle de la
    case, la fiche du personnage pour cohérence visuelle, le style artistique,
    et un negative prompt interdisant le texte dans l'image (les bulles sont
    composées séparément).
    """
    style_guides = {
        "manga": "style manga japonais, lignes nettes, tramage, expressive",
        "cartoon": "style cartoon, couleurs vives, formes simplifiées, expressif",
        "aquarelle": "style aquarelle, coups de pinceau visibles, couleurs douces, fluide",
        "comics": "style comics américain, encrage épais, halftone, dynamique",
    }
    style_guide = style_guides.get(style, f"style {style}")

    panel = scene.panels[panel_index - 1] if panel_index <= len(scene.panels) else scene.panels[-1]

    return f"""Illustration de bande dessinée, case {panel_index}.

SCENE : {scene.description}
CASE {panel_index} : {panel.description_visuelle}

PERSONNAGE PRINCIPAL :
- Nom : {character.name}
- Vêtements : {character.vetements}
- Couleurs : {character.couleurs}
- Attributs distinctifs : {character.attributs_distinctifs}

STYLE : {style_guide}

Règles :
- Respecte exactement la description de la scène ci-dessus.
- Le personnage doit correspondre à la fiche ci-dessus (même tenue, mêmes couleurs, mêmes attributs d'une case à l'autre).
- Pas de texte, pas de bulles, pas de lettres, pas de mots dans l'image : le texte est ajouté séparément en bulles.
- Composition adaptée à une case de bande dessinée.
- Qualité haute, détails nets, éclairage cohérent.

Negative prompt : texte, écriture, lettres, mots, bulles de dialogue, sous-titres, watermark, signature, flou, déformation.
""".strip()
