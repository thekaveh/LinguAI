from __future__ import annotations
from typing import Callable, Dict

from nicegui import ui, app

from viewmodels.app_shell_vm import AppShellVM
from views.theme.palette import apply_theme
from views.theme.typography import install_fonts
from views.shell import header as _header
from views.shell import sidebar as _sidebar
from views.shell import footer as _footer
from views.shell import toast_host as _toast_host
from views.home.home_view import render as _render_home
from views.polyglot_puzzle.polyglot_puzzle_view import render as _render_polyglot
from views.profile.profile_view import render as _render_profile
from views.assessment.assessment_view import render as _render_assessment
from views.chat.chat_view import render as _render_chat
from views.content_gen.content_gen_view import render as _render_content_gen
from views.rewrite_content.rewrite_content_view import render as _render_rewrite
from views.review_writing.review_writing_view import render as _render_review
from views.admin.admin_view import render as _render_admin


# Route -> page-renderer registry, populated via register_page_renderer().
PAGE_RENDERERS: Dict[str, Callable[[AppShellVM], None]] = {}

PAGE_RENDERERS["home"] = _render_home
PAGE_RENDERERS["polyglot_puzzle"] = _render_polyglot
PAGE_RENDERERS["profile"] = _render_profile
PAGE_RENDERERS["assessment"] = _render_assessment
PAGE_RENDERERS["chat"] = _render_chat
PAGE_RENDERERS["content_gen"] = _render_content_gen
PAGE_RENDERERS["rewrite_content"] = _render_rewrite
PAGE_RENDERERS["review_writing"] = _render_review
PAGE_RENDERERS["admin"] = _render_admin


def register_page_renderer(route: str, fn: Callable[[AppShellVM], None]) -> None:
    PAGE_RENDERERS[route] = fn


def mount(shell: AppShellVM) -> None:
    """Build chrome + a content slot that swaps when navigation or auth changes."""
    install_fonts()
    saved_mode = app.storage.user.get("theme_mode", "system")
    shell.settings.set_theme(saved_mode)
    apply_theme(saved_mode)

    _header.render(shell)
    _sidebar.render(shell)
    _footer.render()
    _toast_host.attach(shell.notifications)

    # Persist session to storage as it changes.
    def _persist_session(_=None) -> None:
        s = shell.session.model
        if s.token:
            app.storage.user["auth_token"] = s.token
            app.storage.user["username"] = s.username
        else:
            app.storage.user.pop("auth_token", None)
            app.storage.user.pop("username", None)
    shell.session.property_changed.subscribe(
        lambda name: _persist_session() if name == "model" else None
    )

    content_slot = ui.column().classes("w-full max-w-6xl mx-auto px-6 py-6")

    def _rerender(_=None) -> None:
        content_slot.clear()
        with content_slot:
            if not shell.session.model.is_authenticated:
                from viewmodels.auth.login_vm import build_login_vm
                from views.auth.login_view import render as render_login
                if not hasattr(shell, "_login_vm_pair"):
                    shell._login_vm_pair = build_login_vm(
                        shell._hub, shell._dispatcher, shell.session, shell.notifications,
                    )
                vm, cmd = shell._login_vm_pair
                render_login(vm, cmd)
                return
            renderer = PAGE_RENDERERS.get(shell.navigation.model.current)
            if renderer is None:
                # Defensive: every NavigationVM route has a registered renderer,
                # but guard against an unregistered route rather than crashing.
                ui.label(
                    f"(no renderer registered for '{shell.navigation.model.current}')"
                ).classes("text-[var(--text-3)] text-sm italic")
                return
            renderer(shell)

    shell.navigation.property_changed.subscribe(
        lambda name: _rerender() if name == "model" else None
    )
    shell.session.property_changed.subscribe(
        lambda name: _rerender() if name == "model" else None
    )
    _rerender()
