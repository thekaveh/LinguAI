from __future__ import annotations
import plotly.graph_objects as go  # type: ignore[import-untyped]
from nicegui import ui

from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM, EmbeddingsView


_DARK_LAYOUT: dict = {
    "template": "plotly_dark",
    "paper_bgcolor": "rgba(0,0,0,0)",
    "plot_bgcolor": "rgba(0,0,0,0)",
    "font": {"color": "#E6EAF2"},
}


def _similarity_color(sim: float) -> str:
    """Red→amber→emerald gradient. sim in [0, 1]. Local copy — keeps module independent."""
    s = max(0.0, min(1.0, sim))
    if s < 0.5:
        t = s / 0.5
        r1, g1, b1 = 0xEF, 0x44, 0x44
        r2, g2, b2 = 0xF5, 0x9E, 0x0B
    else:
        t = (s - 0.5) / 0.5
        r1, g1, b1 = 0xF5, 0x9E, 0x0B
        r2, g2, b2 = 0x10, 0xB9, 0x81
    return f"rgb({int(r1+(r2-r1)*t)}, {int(g1+(g2-g1)*t)}, {int(b1+(b2-b1)*t)})"


def _marker_colors(m: EmbeddingsView) -> list[str]:
    """Build a per-point color list: index 0 = 'ideal' (brand orange); rest = gradient."""
    if not m.similarities:
        return ["#F97316"] * len(m.labels)  # fallback: all brand orange
    cols: list[str] = ["#F97316"]  # ideal
    for s in m.similarities:
        cols.append(_similarity_color(s))
    # Pad if labels longer than expected (safety)
    while len(cols) < len(m.labels):
        cols.append("#94A3B8")
    return cols


def _figure_for(m: EmbeddingsView) -> go.Figure:
    colors = _marker_colors(m)
    if m.mode == "3d" and m.points_3d:
        xs = [p[0] for p in m.points_3d]
        ys = [p[1] for p in m.points_3d]
        zs = [p[2] for p in m.points_3d]
        return go.Figure(data=[go.Scatter3d(
            x=xs, y=ys, z=zs, mode="markers+text",
            text=list(m.labels), textposition="top center",
            marker={"size": 6, "color": colors},
        )], layout={**_DARK_LAYOUT, "margin": {"l": 0, "r": 0, "t": 20, "b": 0}, "height": 320})
    if m.points_2d:
        xs = [p[0] for p in m.points_2d]
        ys = [p[1] for p in m.points_2d]
        return go.Figure(data=[go.Scatter(
            x=xs, y=ys, mode="markers+text",
            text=list(m.labels), textposition="top center",
            marker={"size": 10, "color": colors},
        )], layout={**_DARK_LAYOUT, "margin": {"l": 0, "r": 0, "t": 20, "b": 0}, "height": 320})
    return go.Figure(layout={
        **_DARK_LAYOUT,
        "annotations": [{"text": "Submit attempts to see the projection",
                          "showarrow": False, "x": 0.5, "y": 0.5,
                          "xref": "paper", "yref": "paper"}],
        "height": 320,
        "xaxis": {"visible": False},
        "yaxis": {"visible": False},
    })


def render(vm: EmbeddingsViewVM) -> None:
    with ui.column().classes("w-full mt-4 gap-2"):
        toggle = ui.toggle({"2d": "2D", "3d": "3D"}, value=vm.model.mode) \
            .on_value_change(lambda e: vm.set_mode(e.value))
        chart = ui.plotly(_figure_for(vm.model)).classes("w-full")

        def _rebuild(name: str) -> None:
            if name == "model":
                chart.update_figure(_figure_for(vm.model))
                toggle.value = vm.model.mode
        vm.property_changed.subscribe(_rebuild)
