"""Tests du générateur d'images avec cache par hash."""

import hashlib

from storyworld.domain.models import CharacterDraft, PanelDraft, SceneDraft
from storyworld.providers.mock import MockImageProvider
from storyworld.services.image_generator import ImageGenerator


def _build_scene_and_character():
    character = CharacterDraft(
        name="Leila",
        role="héroïne",
        personnalite="curieuse",
        vetements="jean",
        couleurs="bleu",
        attributs_distinctifs="lunettes",
    )
    panel = PanelDraft(
        numero=1,
        description_visuelle="Une ruelle étroite, murs ocre.",
        dialogue="Bonjour.",
        personnages=["Leila"],
    )
    scene = SceneDraft(numero=1, description="Test scène.", panels=[panel])
    return scene, character


def test_image_generator_cache_evite_appel_redondant(tmp_path):
    provider = MockImageProvider()
    generator = ImageGenerator(provider, output_dir=tmp_path / "media")
    scene, character = _build_scene_and_character()

    path1 = generator.generate_panel_image(scene, character, "manga", 1)
    assert path1.exists()
    assert provider.call_count == 1

    # Même prompt → cache, pas de nouvel appel
    path2 = generator.generate_panel_image(scene, character, "manga", 1)
    assert path1 == path2
    assert provider.call_count == 1


def test_image_generator_prompts_differents_appelent_deux_fois(tmp_path):
    provider = MockImageProvider()
    generator = ImageGenerator(provider, output_dir=tmp_path / "media")
    scene, character = _build_scene_and_character()

    path_manga = generator.generate_panel_image(scene, character, "manga", 1)
    path_comics = generator.generate_panel_image(scene, character, "comics", 1)

    assert path_manga.exists()
    assert path_comics.exists()
    assert path_manga != path_comics
    assert provider.call_count == 2


def test_image_generator_nom_fichier_hash_prompt(tmp_path):
    provider = MockImageProvider()
    generator = ImageGenerator(provider, output_dir=tmp_path / "media")
    scene, character = _build_scene_and_character()

    path = generator.generate_panel_image(scene, character, "manga", 1)
    # Le nom de fichier doit être le hash du prompt
    from storyworld.services.prompt_builder import build_image_prompt

    prompt = build_image_prompt(scene, character, "manga", 1)
    expected_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]
    assert path.name == f"{expected_hash}.png"


class _JpegProvider:
    """Provider qui renvoie du JPEG, comme Pollinations."""

    def __init__(self):
        self.call_count = 0

    def generate(self, prompt, *, size=(1024, 1024), seed=None):
        import io

        from PIL import Image

        self.call_count += 1
        buffer = io.BytesIO()
        Image.new("RGB", (64, 64), (10, 20, 30)).save(buffer, format="JPEG")
        return buffer.getvalue()


def test_image_generator_normalise_le_format_en_png(tmp_path):
    generator = ImageGenerator(_JpegProvider(), output_dir=tmp_path / "media")
    scene, character = _build_scene_and_character()

    path = generator.generate_panel_image(scene, character, "manga", 1)

    from PIL import Image

    with Image.open(path) as image:
        assert image.format == "PNG"
        assert image.size == (64, 64)
