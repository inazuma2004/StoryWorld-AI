from storyworld.domain.models import CharacterDraft, PanelDraft, SceneDraft, StoryDraft
from storyworld.storage import Repository, create_session_factory


def build_valid_story() -> StoryDraft:
    return StoryDraft(
        title="Test BD",
        synopsis="Une courte histoire de test.",
        characters=[
            CharacterDraft(
                name="Leila",
                role="heroine",
                personnalite="curieuse",
                vetements="jean",
                couleurs="bleu",
                attributs_distinctifs="lunettes",
            )
        ],
        scenes=[
            SceneDraft(
                numero=1,
                description="Une scène de test.",
                panels=[
                    PanelDraft(
                        numero=1,
                        description_visuelle="Un personnage dans une ruelle.",
                        dialogue="Bonjour le monde.",
                        personnages=["Leila"],
                    )
                ],
            )
        ],
    )


def test_project_roundtrip(tmp_path):
    repo = Repository(create_session_factory(tmp_path / "test.db"))
    story = build_valid_story()
    project_id = repo.save_project(story)
    loaded = repo.get_project(project_id)
    assert loaded is not None
    assert loaded.title == story.title
    assert len(loaded.scenes) == len(story.scenes)
    assert loaded.scenes[0].panels[0].dialogue == story.scenes[0].panels[0].dialogue
