from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.admin.admin_vm import AdminVM
from views.theme.components import card, pill_button, section_header, chip


def render(shell: AppShellVM) -> None:
    vm: AdminVM = shell._admin_vm  # type: ignore[attr-defined]

    # Auto-load user list on first render.
    if not vm.state.model.users:
        asyncio.create_task(_load(vm))

    # ---- Users table ----
    with card():
        with ui.row().classes("items-center justify-between w-full"):
            section_header("Users", subtitle="manage LinguAI accounts")
            with ui.row().classes("gap-2"):
                pill_button("Refresh", on_click=vm.load_users_command.execute)

        users_container = ui.column().classes("w-full gap-1 mt-3")

        def _render_users(name: str) -> None:
            if name != "model":
                return
            users_container.clear()
            with users_container:
                if not vm.state.model.users:
                    ui.label("No users loaded.").classes("text-sm text-[var(--text-3)]")
                    return
                # Header row
                with ui.row().classes("w-full gap-2 text-xs uppercase tracking-wider text-[var(--text-3)] py-1 border-b border-white/5"):
                    ui.label("USERNAME").classes("w-32")
                    ui.label("EMAIL").classes("flex-1")
                    ui.label("TYPE").classes("w-24")
                    ui.label("NAME").classes("w-48")
                    ui.label("").classes("w-12")  # actions
                # User rows
                for u in vm.state.model.users:
                    is_self = u.username == (vm._session.model.username or "")
                    with ui.row().classes("w-full gap-2 items-center py-1.5 border-b border-white/5 text-sm"):
                        ui.label(u.username).classes("w-32 font-mono")
                        ui.label(u.email or "").classes("flex-1 text-[var(--text-2)]")
                        chip(u.user_type or "user",
                             tone="brand" if u.user_type == "admin" else "neutral")
                        ui.label(f"{u.first_name or ''} {u.last_name or ''}").classes("w-48 text-[var(--text-2)]")
                        if is_self:
                            ui.label("(you)").classes("w-12 text-xs text-[var(--text-3)]")
                        else:
                            ui.button(icon="delete", on_click=_make_request_delete(vm, u.username)) \
                                .props("flat dense round color=negative").classes("w-12")

        _render_users("model")
        vm.state.property_changed.subscribe(_render_users)

    # ---- Backend health card ----
    with card().classes("mt-4"):
        section_header("Backend health")
        ui.label().bind_text_from(vm.state, "model", backward=lambda m: m.last_ping) \
            .classes("text-sm text-[var(--text-1)]")
        with ui.row().classes("justify-end mt-3"):
            pill_button("Ping backend", variant="primary", on_click=vm.ping_command.execute)

    # ---- Confirm-delete dialog ----
    dialog = ui.dialog()
    with dialog:
        with card().classes("w-96"):
            section_header("Confirm delete")
            ui.label().bind_text_from(
                vm.state, "model",
                backward=lambda m: f"Permanently delete user '{m.pending_delete_username}'?" if m.pending_delete_username else "",
            ).classes("text-sm")
            ui.label("This cannot be undone.").classes("text-xs text-[var(--danger)] mt-1")
            with ui.row().classes("justify-end gap-2 mt-4 w-full"):
                pill_button("Cancel", on_click=_cancel_and_close(vm, dialog))
                pill_button("Delete", variant="primary",
                            on_click=_execute_and_close(vm, dialog)).style("background:#EF4444")

    def _open_or_close_dialog(name: str) -> None:
        if name != "model":
            return
        if vm.state.model.pending_delete_username:
            dialog.open()
        else:
            dialog.close()
    vm.state.property_changed.subscribe(_open_or_close_dialog)


def _make_request_delete(vm: AdminVM, username: str):  # type: ignore[no-untyped-def]
    def _cb() -> None:
        vm.request_delete(username)
    return _cb


def _cancel_and_close(vm: AdminVM, dialog):  # type: ignore[no-untyped-def]
    def _cb() -> None:
        vm.cancel_delete_command.execute()
    return _cb


def _execute_and_close(vm: AdminVM, dialog):  # type: ignore[no-untyped-def]
    def _cb() -> None:
        vm.execute_delete_command.execute()
    return _cb


async def _load(vm: AdminVM) -> None:
    vm.load_users_command.execute()
