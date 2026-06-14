from nicegui import ui, app

from viewmodels.app_shell_vm import AppShellVM


def render(shell: AppShellVM) -> None:
    # TODO: bind header bg to current SettingsVM.theme_mode for light-mode polish
    with ui.header(elevated=False).props('reveal-offset=0').style(
        'background: rgba(10,14,26,0.72); backdrop-filter: blur(12px); '
        'border-bottom: 1px solid rgba(255,255,255,0.06);'
    ).classes("items-center px-4 py-2 gap-3"):
        ui.icon("menu").on("click", shell.navigation.toggle_drawer).classes(
            "text-[var(--text-2)] cursor-pointer"
        )
        ui.element("div").classes("w-6 h-6 rounded-md").style(
            "background:linear-gradient(135deg,#F97316,#FB923C,#FBBF24);"
            "box-shadow:0 0 12px rgba(249,115,22,0.4)"
        )
        ui.label("LinguAI").classes("text-sm font-semibold tracking-tight")
        ui.label("/").classes("text-[var(--text-3)] mx-1")
        ui.label().bind_text_from(
            shell.navigation, "model",
            backward=lambda m: m.current.replace("_", " ").title(),
        ).classes("text-sm text-[var(--text-1)]")
        ui.space()

        # Backend status dot — bound to shell.session.model.backend_status
        with ui.row().classes("items-center gap-1.5 text-xs text-[var(--text-2)]"):
            status_dot = ui.element("span").classes("w-1.5 h-1.5 rounded-full bg-slate-500")
            status_dot.style("box-shadow: 0 0 6px currentColor")  # subtle glow

            def _refresh_status(name: str) -> None:
                if name != "model":
                    return
                bs = shell.session.model.backend_status
                color = {
                    "online": "bg-emerald-400",
                    "offline": "bg-red-400",
                    "unknown": "bg-slate-500",
                }[bs]
                # Remove any existing bg-* class then add the new one.
                # Use Classes.__call__ API: remove= then add= keeps _classes as a Classes object.
                existing_bg = " ".join(c for c in status_dot.classes if c.startswith("bg-"))
                status_dot.classes(add=color, remove=existing_bg if existing_bg else None)

            shell.session.property_changed.subscribe(_refresh_status)
            _refresh_status("model")
            ui.label("Backend")

        ui.icon("dark_mode").on("click", _toggle_theme(shell)).classes(
            "text-[var(--text-2)] cursor-pointer"
        )

        # User avatar + sign-out menu
        with ui.row().classes("items-center gap-2 pl-2 border-l border-white/5"):
            ui.label().bind_text_from(
                shell.session, "model",
                backward=lambda m: (m.username or "?")[:2].upper(),
            ).classes(
                "w-7 h-7 rounded-full bg-violet-500 text-white text-xs font-semibold "
                "flex items-center justify-center cursor-pointer"
            )

            async def _logout() -> None:
                shell.notifications.push_info("Signed out — see you soon!")
                await shell.session.log_out()
                app.storage.user.pop("auth_token", None)
                app.storage.user.pop("username", None)

            with ui.menu().props("auto-close"):
                ui.menu_item("Sign out", on_click=_logout)


def _toggle_theme(shell: AppShellVM):
    from views.theme.palette import apply_theme

    def _cb() -> None:
        nxt = {"system": "light", "light": "dark", "dark": "system"}[
            shell.settings.model.theme_mode
        ]
        shell.settings.set_theme(nxt)
        apply_theme(nxt)
        app.storage.user["theme_mode"] = nxt

    return _cb
