"""Extraction et réparation d'objets JSON depuis du texte brut (sortie LLM)."""

from __future__ import annotations

import json
import re


def _extract_json_candidates(raw: str) -> list[str]:
    """Retourne les candidats JSON trouvés dans le texte, du plus probable au moins."""
    candidates: list[str] = []

    # 1. Bloc markdown ```json ... ```
    for m in re.finditer(r"```json\s*\n(.*?)\n```", raw, re.DOTALL | re.IGNORECASE):
        candidates.append(m.group(1).strip())

    # 2. Bloc markdown ``` ... ```
    for m in re.finditer(r"```\s*\n(.*?)\n```", raw, re.DOTALL):
        candidates.append(m.group(1).strip())

    # 3. Premier objet { ... } équilibré
    depth = 0
    start = -1
    for i, ch in enumerate(raw):
        if ch == "{":
            if depth == 0:
                start = i
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0 and start >= 0:
                candidates.append(raw[start : i + 1])
                break

    return candidates


def parse_json_object(raw: str) -> dict:
    """Extrait un objet JSON depuis du texte brut. Lève ValueError si impossible."""
    for candidate in _extract_json_candidates(raw):
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue

    # Dernière tentative : le texte brut entier
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        raise ValueError("Aucun objet JSON valide trouvé dans le texte")


def repair_json_object(raw: str) -> dict | None:
    """Tente de réparer un JSON invalide (virgule finale, guillemets typographiques).
    Retourne None si non réparable."""
    try:
        return parse_json_object(raw)
    except ValueError:
        pass

    # Réparation : virgule finale avant } ou ]
    repaired = re.sub(r",(\s*[}\]])", r"\1", raw)
    try:
        return parse_json_object(repaired)
    except ValueError:
        return None
