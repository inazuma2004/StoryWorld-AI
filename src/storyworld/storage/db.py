"""Configuration de la base de données SQLite."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from storyworld.storage.models import Base


def create_session_factory(db_path: Path) -> sessionmaker[Session]:
    """Crée une sessionmaker liée à une base SQLite et initialise les tables."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, expire_on_commit=False)
