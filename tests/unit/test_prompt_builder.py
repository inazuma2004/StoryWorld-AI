from storyworld.domain.models import StoryBrief
from storyworld.services.prompt_builder import build_story_prompt


def test_prompt_contient_contraintes_essentielles():
    brief = StoryBrief(
        idea="un robot jardinier",
        genre="aventure",
        style="manga",
        audience="enfant",
        language="fr",
        panel_count=4,
    )
    schema = {"type": "object"}
    prompt = build_story_prompt(brief, schema)

    assert brief.idea in prompt
    assert brief.genre in prompt
    assert brief.style in prompt
    assert brief.audience in prompt
    assert brief.language in prompt
    assert str(brief.panel_count) in prompt
    assert "JSON" in prompt.upper()
    assert "120" in prompt  # limite dialogue
    assert "texte" in prompt.lower()  # interdiction texte dans les images
