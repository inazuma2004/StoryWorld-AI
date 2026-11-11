"""Repository : lecture/écriture des projets et des assets."""

from pathlib import Path

from sqlalchemy import create_engine

from storyworld.domain.models import StoryDraft
from storyworld.storage.models import AssetORM, Base, ProjectORM


class Repository:
    def __init__(self, session_factory):
        self._session_factory = session_factory

    def save_project(self, story: StoryDraft) -> str:
        with self._session_factory() as session:
            project = ProjectORM(
                title=story.title,
                status="draft",
                story_json=story.model_dump_json(),
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return project.id

    def get_project(self, project_id: str) -> StoryDraft | None:
        with self._session_factory() as session:
            project = session.get(ProjectORM, project_id)
            if project is None:
                return None
            return StoryDraft.model_validate_json(project.story_json)

    def list_projects(self):
        with self._session_factory() as session:
            projects = session.query(ProjectORM).all()
            return [
                {"id": p.id, "title": p.title, "status": p.status}
                for p in projects
            ]

    def add_asset(
        self,
        project_id: str,
        kind: str,
        path: str,
        prompt_hash: str | None = None,
    ) -> str:
        with self._session_factory() as session:
            asset = AssetORM(
                project_id=project_id,
                kind=kind,
                path=path,
                prompt_hash=prompt_hash,
            )
            session.add(asset)
            session.commit()
            session.refresh(asset)
            return asset.id

    def get_asset_by_hash(
        self, project_id: str, prompt_hash: str
    ) -> AssetORM | None:
        with self._session_factory() as session:
            return (
                session.query(AssetORM)
                .filter_by(project_id=project_id, prompt_hash=prompt_hash)
                .first()
            )

    def create_tables(self, db_path: Path) -> None:
        engine = create_engine(f"sqlite:///{db_path}")
        Base.metadata.create_all(engine)
