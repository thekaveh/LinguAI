from __future__ import annotations

from nicegui import ui

from viewmodels.auth.register_vm import RegisterVM
from vmx import RelayCommand
from views.theme.components import card, pill_button, section_header, bind_button_enabled


# Hard-coded language list for the wizard; replaced by a LanguageService call when ProfileVM lands in phase 4.
_LANGUAGES = [
    "English", "Spanish", "French", "German", "Italian",
    "Japanese", "Mandarin", "Portuguese", "Arabic", "Russian",
]


def render(
    vm: RegisterVM,
    next_cmd: RelayCommand,
    back_cmd: RelayCommand,
    submit_cmd: RelayCommand,
) -> None:
    with ui.column().classes("max-w-md mx-auto mt-12 gap-3 w-full"):
        with card():
            section_header("Create your LinguAI account")
            ui.label().bind_text_from(
                vm, "model", backward=lambda m: f"Step {m.current_step + 1} of 3",
            ).classes("text-xs text-[var(--text-3)] uppercase tracking-wider")

            step_container = ui.column().classes("w-full mt-3 gap-2")

            def _render_step() -> None:
                step_container.clear()
                with step_container:
                    idx = vm.model.current_step
                    if idx == 0:
                        _account_inputs(vm)
                    elif idx == 1:
                        _profile_inputs(vm)
                    else:
                        _languages_inputs(vm)

            vm.property_changed.subscribe(
                lambda name: _render_step() if name == "model" else None
            )
            _render_step()

            ui.label().bind_text_from(vm, "model", backward=lambda m: m.error) \
                .classes("text-xs text-[var(--danger)] mt-2")

            with ui.row().classes("gap-2 justify-end mt-3 w-full"):
                back_btn = pill_button("Back", on_click=back_cmd.execute)
                bind_button_enabled(back_btn, back_cmd)

                next_btn = pill_button("Next", variant="primary", on_click=next_cmd.execute)
                next_btn.bind_visibility_from(
                    vm, "model", backward=lambda m: m.current_step < 2
                )
                bind_button_enabled(next_btn, next_cmd)

                submit_btn = pill_button(
                    "Create account", variant="primary", on_click=submit_cmd.execute
                )
                submit_btn.bind_visibility_from(
                    vm, "model", backward=lambda m: m.current_step == 2
                )
                bind_button_enabled(submit_btn, submit_cmd)


def _account_inputs(vm: RegisterVM) -> None:
    a = vm.account
    ui.input("Username", value=a.model.username).props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: a.set_username(e.value or ""))
    ui.input("Email", value=a.model.email).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: a.set_email(e.value or ""))
    # Read plaintext from the trusted accessors (NOT the model — the model only
    # carries validity flags, the plaintext lives in private VM attrs for security).
    ui.input(
        "Password", password=True, password_toggle_button=True, value=a.password(),
    ).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: a.set_password(e.value or ""))
    ui.input("Confirm password", password=True, value=a.confirm()) \
        .props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: a.set_confirm(e.value or ""))


def _profile_inputs(vm: RegisterVM) -> None:
    p = vm.profile
    ui.input("Preferred name (optional)", value=p.model.preferred_name) \
        .props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: p.set_preferred_name(e.value or ""))
    ui.input("First name", value=p.model.first_name).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: p.set_first_name(e.value or ""))
    ui.input("Last name (optional)", value=p.model.last_name) \
        .props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: p.set_last_name(e.value or ""))


def _languages_inputs(vm: RegisterVM) -> None:
    L = vm.languages
    ui.select(_LANGUAGES, label="Native language", value=L.model.native or None) \
        .props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: L.set_native(e.value or ""))
    ui.select(
        _LANGUAGES, label="Languages to learn", multiple=True,
        value=list(L.model.learning) or None,
    ).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: L.set_learning(tuple(e.value or ())))
