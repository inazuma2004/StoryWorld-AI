"""Configuration pytest : client de test avec base SQLite temporaire isolée."""

from __future__ import annotations

from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from storyworld.api.main import app, get_repository
from storyworld.storage import Repository, create_session_factory


@pytest.fixture
def client(tmp_path: Path):
    """Fournit un TestClient avec une base SQLite temporaire vide par test."""
    db_path = tmp_path / "api_test.db"
    session_factory = create_session_factory(db_path)
    repo = Repository(session_factory)

    def _get_repo():
        return repo

    app.dependency_overrides[get_repository] = _get_repo
    yield TestClient(app)
    app.dependency_overrides.clear()
