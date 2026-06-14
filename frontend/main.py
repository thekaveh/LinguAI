from __future__ import annotations
import asyncio
import logging

from nicegui import ui, app

from core.config import AppConfig
from core.logger import setup_logging
from core.di import build_process_scoped, build_shell
from views.app_shell import mount


_CFG = AppConfig()
setup_logging(_CFG.frontend_logger_name, _CFG.frontend_log_level, _CFG.frontend_log_file)

# Warn if storage_secret is left at its dev default. NiceGUI uses this to sign
# `app.storage.user`; an attacker who knows the secret can forge auth_token.
if _CFG.frontend_storage_secret == "linguai-frontend-dev-secret":
    logging.getLogger(_CFG.frontend_logger_name).warning(
        "FRONTEND_STORAGE_SECRET is using the built-in dev default; "
        "set it to a private value in production."
    )

# Process-scoped objects. NiceGUI's main thread runs uvicorn, which creates the loop later;
# at module-import time there is no running loop. Create one for the dispatcher to bind to;
# uvicorn picks it up (or replaces it) once ui.run() starts.
try:
    _LOOP = asyncio.get_running_loop()
except RuntimeError:
    _LOOP = asyncio.new_event_loop()
    asyncio.set_event_loop(_LOOP)

_HUB, _DISPATCHER, _HTTP, _AUTH = build_process_scoped(_CFG, _LOOP)


@ui.page("/")
def index_page() -> None:
    shell = build_shell(_HUB, _DISPATCHER, _HTTP, _AUTH)

    # Rehydrate session from cookie if present.
    saved_token = app.storage.user.get("auth_token")
    saved_user = app.storage.user.get("username")
    if saved_token:
        shell.session.rehydrate(saved_token, saved_user)

    mount(shell)


@ui.page("/register")
def register_page() -> None:
    from viewmodels.auth.register_vm import build_register_vm
    from viewmodels.shell.notification_center_vm import build_notification_center
    from views.auth.register_view import render as render_register
    from views.theme.palette import apply_theme
    from views.theme.typography import install_fonts

    install_fonts()
    saved_mode = app.storage.user.get("theme_mode", "system")
    apply_theme(saved_mode)

    notifications = build_notification_center(_HUB, _DISPATCHER)
    vm, nx, bk, sub = build_register_vm(
        _HUB, _DISPATCHER, _HTTP, notifications,
        on_complete=lambda: ui.navigate.to("/"),
    )
    render_register(vm, nx, bk, sub)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host="0.0.0.0",
        port=_CFG.frontend_port,
        title="LinguAI",
        dark=True,
        storage_secret=_CFG.frontend_storage_secret,
        show=False,
        reload=False,
    )
