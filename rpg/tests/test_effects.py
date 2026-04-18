from rpg_battle.content.effects import EFFECTS
from rpg_battle.render.effect_factory import make_effect


def test_new_effect_catalog_entries_exist() -> None:
    for effect_id in ["sine_wave", "gradient_descent", "chaos_zigzag", "pixel_storm"]:
        assert effect_id in EFFECTS


def test_declared_effect_can_build_runtime_instance() -> None:
    effect = make_effect("chaos_zigzag", (10.0, 20.0), (100.0, 80.0))
    assert effect.spec.effect_id == "chaos_zigzag"
    assert effect.alive()
