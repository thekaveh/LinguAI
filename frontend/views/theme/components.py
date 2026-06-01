from typing import Any, Callable, Optional
from nicegui import ui


def card() -> Any:
    """Return a card container — use inside a `with` block."""
    return ui.card().classes(
        "w-full rounded-xl border border-white/5 bg-[var(--surface-1)]"
    ).tight()


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    with ui.row().classes("items-baseline gap-3 mb-3"):
        ui.label(title).classes("text-lg font-semibold tracking-tight")
        if subtitle:
            ui.label(subtitle).classes("text-xs text-[var(--text-3)] uppercase tracking-wider")


def pill_button(
    label: str,
    *,
    on_click: Optional[Callable[..., Any]] = None,
    variant: str = "default",
    icon: Optional[str] = None,
) -> Any:
    """`variant`: 'default' | 'primary'."""
    cls = "rounded-lg text-sm font-medium px-3 py-1.5"
    if variant == "primary":
        cls += " bg-[var(--brand)] text-[var(--surface-0)]"
    else:
        cls += " bg-white/5 text-[var(--text-1)] hover:bg-white/10"
    btn = ui.button(label, on_click=on_click)
    btn.props("flat" if variant != "primary" else "unelevated")
    btn.classes(cls)
    if icon:
        btn.props(f"icon={icon}")
    return btn


def chip(text: str, *, tone: str = "neutral") -> Any:
    tones = {
        "neutral": "bg-white/5 text-[var(--text-2)]",
        "brand":   "bg-[var(--brand)]/10 text-[var(--brand)]",
        "success": "bg-emerald-500/10 text-emerald-300",
        "info":    "bg-cyan-500/10 text-cyan-300",
        "warning": "bg-amber-500/10 text-amber-300",
        "danger":  "bg-red-500/10 text-red-300",
    }
    return ui.label(text).classes(
        f"inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs {tones[tone]}"
    )


def bind_button_enabled(btn: Any, cmd: Any) -> None:
    """Subscribe a NiceGUI button's `enabled` to a VMx RelayCommand's can_execute_changed."""
    def _refresh(_: Any = None) -> None:
        btn.set_enabled(cmd.can_execute())
    cmd.can_execute_changed.subscribe(_refresh)
    _refresh()
