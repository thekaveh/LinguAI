"""Shared color helpers for the polyglot puzzle views.

Extracted from ``polyglot_puzzle_view.py`` and ``embeddings_plot.py``,
which previously each carried their own copy of ``_similarity_color``.
"""
from __future__ import annotations


def similarity_color(sim: float) -> str:
    """Red→amber→emerald gradient for similarity in [0, 1]."""
    s = max(0.0, min(1.0, sim))
    if s < 0.5:
        t = s / 0.5
        r1, g1, b1 = 0xEF, 0x44, 0x44
        r2, g2, b2 = 0xF5, 0x9E, 0x0B
    else:
        t = (s - 0.5) / 0.5
        r1, g1, b1 = 0xF5, 0x9E, 0x0B
        r2, g2, b2 = 0x10, 0xB9, 0x81
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"rgb({r}, {g}, {b})"
