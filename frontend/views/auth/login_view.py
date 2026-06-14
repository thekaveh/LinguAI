from __future__ import annotations

from nicegui import ui

from viewmodels.auth.login_vm import LoginVM
from vmx import RelayCommand
from views.theme.components import card, pill_button, section_header, bind_button_enabled


def render(vm: LoginVM, cmd: RelayCommand) -> None:
    with ui.column().classes("max-w-sm mx-auto mt-16 gap-4 w-full"):
        with card():
            section_header("Sign in to LinguAI")

            user_input = ui.input("Username").props("outlined dense").classes("w-full")
            pass_input = ui.input("Password", password=True, password_toggle_button=True) \
                .props("outlined dense").classes("w-full mt-2")

            user_input.on_value_change(lambda e: vm.set_username(e.value or ""))
            pass_input.on_value_change(lambda e: vm.set_password(e.value or ""))

            ui.label().classes("text-xs text-[var(--danger)] mt-2") \
                .bind_text_from(vm, "model", backward=lambda m: m.error)

            btn = pill_button(
                "Sign in", variant="primary", on_click=cmd.execute,
            )
            btn.classes("w-full mt-3")
            bind_button_enabled(btn, cmd)

        with ui.row().classes("justify-center w-full text-xs text-[var(--text-2)] gap-1"):
            ui.label("New here?")
            ui.link("Create an account", "/register").classes("text-[var(--brand)]")
