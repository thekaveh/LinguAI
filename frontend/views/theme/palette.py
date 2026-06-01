from dataclasses import dataclass
from typing import Literal

from nicegui import ui  # noqa: F401  (imported eagerly for apply_theme; views/theme/ is allowed to import nicegui)

BRAND_ORANGE = "#F97316"

ThemeMode = Literal["system", "light", "dark"]


@dataclass(frozen=True)
class ColorPalette:
    brand: str
    surface_0: str   # page background
    surface_1: str   # default card
    surface_2: str   # elevated surface
    border: str
    text_1: str      # primary
    text_2: str      # secondary
    text_3: str      # tertiary / disabled
    success: str
    warning: str
    danger: str
    info: str


LIGHT = ColorPalette(
    brand=BRAND_ORANGE,
    surface_0="#FFFFFF",
    surface_1="#F8FAFC",
    surface_2="#F1F5F9",
    border="#E2E8F0",
    text_1="#0F172A",
    text_2="#475569",
    text_3="#94A3B8",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    info="#22D3EE",
)

DARK = ColorPalette(
    brand=BRAND_ORANGE,
    surface_0="#0A0E1A",
    surface_1="#0F1421",
    surface_2="#141A2A",
    border="#1F2937",
    text_1="#E6EAF2",
    text_2="#9CA6BC",
    text_3="#5B6478",
    success="#10B981",
    warning="#FBBF24",
    danger="#F87171",
    info="#22D3EE",
)


def palette_for(mode: ThemeMode) -> ColorPalette:
    if mode == "light":
        return LIGHT
    return DARK  # "dark" or "system" (until OS detection added)


def apply_theme(mode: ThemeMode) -> None:
    """Apply the palette to the current NiceGUI page by setting CSS variables + dark-mode toggle."""
    p = palette_for(mode)
    ui.colors(primary=p.brand, secondary=p.info, accent=p.brand, dark=p.surface_0)
    ui.dark_mode(mode != "light")
    ui.add_head_html(
        f"<style>:root{{"
        f"--brand:{p.brand};"
        f"--surface-0:{p.surface_0};--surface-1:{p.surface_1};--surface-2:{p.surface_2};"
        f"--border:{p.border};"
        f"--text-1:{p.text_1};--text-2:{p.text_2};--text-3:{p.text_3};"
        f"--success:{p.success};--warning:{p.warning};--danger:{p.danger};--info:{p.info};"
        f"}}</style>"
    )
