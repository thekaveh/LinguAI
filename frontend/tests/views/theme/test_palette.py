from views.theme.palette import BRAND_ORANGE, LIGHT, DARK, palette_for


def test_brand_orange_is_constant_across_modes():
    assert LIGHT.brand == BRAND_ORANGE
    assert DARK.brand == BRAND_ORANGE


def test_palette_for_returns_matching_palette():
    assert palette_for("light") is LIGHT
    assert palette_for("dark") is DARK


def test_palette_for_unknown_defaults_to_dark():
    assert palette_for("system") is DARK  # system→dark until OS detection lands
