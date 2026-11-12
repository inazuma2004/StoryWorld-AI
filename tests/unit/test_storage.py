"""Tests de l'initialisation de la base SQLite."""

from storyworld.storage import create_session_factory


def test_create_session_factory_cree_le_dossier_parent(tmp_path):
    db_path = tmp_path / "nested" / "data" / "storyworld.sqlite"

    create_session_factory(db_path)

    assert db_path.exists()
