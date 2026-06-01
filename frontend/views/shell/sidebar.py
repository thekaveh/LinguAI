from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM


_LEARN = [
    ("home", "home", "Home"),
    ("chat", "chat_bubble", "Chat"),
    ("content_gen", "auto_stories", "Content"),
    ("rewrite_content", "edit", "Rewrite"),
    ("review_writing", "rate_review", "Review"),
    ("polyglot_puzzle", "extension", "Polyglot"),
]
_YOU = [
    ("profile", "person", "Profile"),
    ("assessment", "insights", "Assessment"),
]
_SYSTEM = [("admin", "tune", "Admin")]


def render(shell: AppShellVM) -> None:
    with ui.left_drawer(
        value=shell.navigation.model.drawer_open, fixed=False,
    ).classes(
        "bg-[var(--surface-0)] border-r border-white/5 p-3 gap-1"
    ) as drawer:
        # Two-way bind: when NavigationVM.drawer_open changes, update drawer visibility.
        def _sync(_=None) -> None:
            drawer.set_value(shell.navigation.model.drawer_open)
        shell.navigation.property_changed.subscribe(lambda name: _sync() if name == "model" else None)

        body = ui.column().classes("w-full gap-0")

        def _rebuild() -> None:
            body.clear()
            with body:
                _section("LEARN", _LEARN, shell)
                _section("YOU", _YOU, shell)
                if shell.session.model.is_admin:
                    _section("SYSTEM", _SYSTEM, shell)

        _rebuild()
        shell.session.property_changed.subscribe(lambda name: _rebuild() if name == "model" else None)


def _section(label: str, items, shell: AppShellVM) -> None:
    ui.label(label).classes(
        "text-[10px] tracking-widest text-[var(--text-3)] "
        "mt-3 mb-1 px-2 font-semibold"
    )
    for route, icon, text in items:
        row = ui.row().classes(
            "items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer text-sm hover:bg-white/5"
        ).on("click", _goto(shell, route))
        with row:
            ui.icon(icon).classes("text-base")
            ui.label(text)

        # Bind active highlighting — captures route and row per iteration to avoid closure bugs.
        def _refresh(name: str, r=row, rt=route) -> None:
            if name != "model":
                return
            is_active = shell.navigation.model.current == rt
            # Use Classes.__call__ API (remove= / add=) to avoid replacing the Classes
            # instance with a plain list (which would break future callable access).
            to_remove = "bg-white/5 text-[var(--brand)] text-[var(--text-2)]"
            if is_active:
                r.classes(add="bg-white/5 text-[var(--brand)]", remove=to_remove)
            else:
                r.classes(add="text-[var(--text-2)]", remove=to_remove)

        shell.navigation.property_changed.subscribe(_refresh)
        _refresh("model")


def _goto(shell: AppShellVM, route: str):
    def _cb() -> None:
        shell.navigation.go(route)  # type: ignore[arg-type]
    return _cb
