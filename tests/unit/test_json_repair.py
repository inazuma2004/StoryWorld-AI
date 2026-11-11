from storyworld.services.json_repair import parse_json_object, repair_json_object


def test_parse_json_pur():
    assert parse_json_object('{"cle": "valeur"}') == {"cle": "valeur"}


def test_parse_json_bloc_markdown():
    assert parse_json_object('```json\n{"cle": "valeur"}\n```') == {"cle": "valeur"}


def test_parse_json_texte_avant_apres():
    assert parse_json_object('Intro {\"cle\": \"valeur\"} suite') == {"cle": "valeur"}


def test_repair_virgule_finale():
    assert repair_json_object('{"a": 1,}') == {"a": 1}


def test_json_tronne_non_reparable():
    assert repair_json_object('{"a":') is None
