from nicegui import ui


def render() -> None:
    with ui.footer(fixed=False).classes(
        "bg-[var(--surface-0)] border-t border-white/5 px-4 py-2"
    ):
        ui.label("LinguAI · learning with AI").classes(
            "text-[11px] text-[var(--text-3)]"
        )
