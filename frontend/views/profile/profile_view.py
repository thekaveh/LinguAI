from __future__ import annotations
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.profile.profile_vm import ProfileVM
from views.theme.components import card, pill_button, section_header, bind_button_enabled
from views.profile.interest_chip import render as render_chip


def render(shell: AppShellVM) -> None:
    vm: ProfileVM = shell._profile_vm  # type: ignore[attr-defined]
    cp = vm.change_password_vm
    cp_cmd = vm.change_password_command

    with card():
        section_header("Profile")

        # --- Identity row: preferred name + email ---
        with ui.row().classes("gap-3 w-full"):
            preferred = (
                ui.input("Preferred name", value=vm.state.model.preferred_name)
                .props("outlined dense")
                .classes("flex-1")
            )
            email = (
                ui.input("Email", value=vm.state.model.email)
                .props("outlined dense")
                .classes("flex-1")
            )

        # --- Name row: first / middle / last ---
        with ui.row().classes("gap-3 w-full mt-3"):
            first = (
                ui.input("First name", value=vm.state.model.first_name)
                .props("outlined dense")
                .classes("flex-1")
            )
            middle = (
                ui.input("Middle name", value=vm.state.model.middle_name)
                .props("outlined dense")
                .classes("flex-1")
            )
            last = (
                ui.input("Last name", value=vm.state.model.last_name)
                .props("outlined dense")
                .classes("flex-1")
            )

        # --- Languages row ---
        with ui.row().classes("gap-3 w-full mt-3"):
            base_lang = (
                ui.select(
                    list(vm.state.model.available_languages),
                    label="Native language",
                    value=vm.state.model.base_language or None,
                )
                .props("outlined dense")
                .classes("flex-1")
            )
            learning = (
                ui.select(
                    list(vm.state.model.available_languages),
                    label="Learning languages",
                    multiple=True,
                    value=list(vm.state.model.learning_languages) or None,
                )
                .props("outlined dense")
                .classes("flex-1")
            )

        # --- Demographics row ---
        with ui.row().classes("gap-3 w-full mt-3"):
            gender = (
                ui.select(
                    ["Male", "Female", "Nonbinary", "Prefer not to say"],
                    label="Gender",
                    value=vm.state.model.gender or None,
                )
                .props("outlined dense")
                .classes("flex-1")
            )
            phone = (
                ui.input("Mobile phone", value=vm.state.model.mobile_phone)
                .props("outlined dense")
                .classes("flex-1")
            )
            contact = (
                ui.select(
                    ["email", "phone", "none"],
                    label="Contact preference",
                    value=vm.state.model.contact_preference or None,
                )
                .props("outlined dense")
                .classes("flex-1")
            )

        # --- Wire setters ---
        preferred.on_value_change(lambda e: vm.set_preferred_name(e.value or ""))
        email.on_value_change(lambda e: vm.set_email(e.value or ""))
        first.on_value_change(lambda e: vm.set_first_name(e.value or ""))
        middle.on_value_change(lambda e: vm.set_middle_name(e.value or ""))
        last.on_value_change(lambda e: vm.set_last_name(e.value or ""))
        base_lang.on_value_change(lambda e: vm.set_base_language(e.value or ""))
        learning.on_value_change(
            lambda e: vm.set_learning_languages(tuple(e.value or ()))
        )
        gender.on_value_change(lambda e: vm.set_gender(e.value or ""))
        phone.on_value_change(lambda e: vm.set_mobile_phone(e.value or ""))
        contact.on_value_change(lambda e: vm.set_contact_preference(e.value or ""))

        # --- Sync inputs after async load ---
        def _refresh_inputs(name: str) -> None:
            if name != "model":
                return
            m = vm.state.model
            preferred.value = m.preferred_name
            email.value = m.email
            first.value = m.first_name
            middle.value = m.middle_name
            last.value = m.last_name
            base_lang.options = list(m.available_languages)
            base_lang.update()
            base_lang.value = m.base_language or None
            learning.options = list(m.available_languages)
            learning.update()
            learning.value = list(m.learning_languages) or None
            gender.value = m.gender or None
            phone.value = m.mobile_phone
            contact.value = m.contact_preference or None

        vm.state.property_changed.subscribe(_refresh_inputs)

        # --- Interests ---
        ui.label("Interests").classes(
            "text-xs uppercase tracking-wider text-[var(--text-3)] mt-4"
        )
        chips_row = ui.row().classes("flex-wrap w-full mt-2")

        def _render_chips() -> None:
            chips_row.clear()
            with chips_row:
                for ivm in vm.interests:
                    render_chip(ivm)

        _render_chips()
        vm.state.property_changed.subscribe(
            lambda name: _render_chips() if name == "model" else None
        )

        # --- Save ---
        with ui.row().classes("justify-end mt-4 w-full"):
            save = pill_button("Save", variant="primary", on_click=vm.save_command.execute)
            bind_button_enabled(save, vm.save_command)
            ui.label().bind_text_from(
                vm.state, "model", backward=lambda m: m.error
            ).classes("text-xs text-[var(--danger)] ml-3 self-center")

    # --- Change password card ---
    with card().classes("mt-4"):
        section_header("Change password")
        cur = (
            ui.input("Current password", password=True, password_toggle_button=True)
            .props("outlined dense")
            .classes("w-full")
        )
        new_pw = (
            ui.input("New password", password=True, password_toggle_button=True)
            .props("outlined dense")
            .classes("w-full mt-2")
        )
        confirm_pw = (
            ui.input("Confirm new password", password=True, password_toggle_button=True)
            .props("outlined dense")
            .classes("w-full mt-2")
        )
        cur.on_value_change(lambda e: cp.set_current(e.value or ""))
        new_pw.on_value_change(lambda e: cp.set_new(e.value or ""))
        confirm_pw.on_value_change(lambda e: cp.set_confirm(e.value or ""))
        ui.label().bind_text_from(
            cp, "model", backward=lambda m: m.error
        ).classes("text-xs text-[var(--danger)] mt-2")
        with ui.row().classes("justify-end mt-3 w-full"):
            change_btn = pill_button(
                "Change password", variant="primary", on_click=cp_cmd.execute
            )
            bind_button_enabled(change_btn, cp_cmd)

    # --- Assessment history ---
    with card().classes("mt-4"):
        section_header("Assessment history")
        history = vm.history
        languages_sel = (
            ui.select([], label="Filter by language").props("outlined dense").classes("w-60")
        )

        def _refresh_filter(name: str) -> None:
            if name != "model":
                return
            langs = sorted({e.language for e in history.model.entries})
            languages_sel.options = langs
            languages_sel.update()
            languages_sel.value = history.model.selected_language or (
                langs[0] if langs else None
            )

        history.property_changed.subscribe(_refresh_filter)
        _refresh_filter("model")
        languages_sel.on_value_change(
            lambda e: history.set_language_filter(e.value or "")
        )

        list_col = ui.column().classes("gap-1 mt-2 w-full")

        def _render_list(name: str) -> None:
            if name != "model":
                return
            list_col.clear()
            with list_col:
                for entry in history.model.filtered_entries:
                    with ui.row().classes(
                        "items-center justify-between w-full py-1 border-b border-white/5"
                    ):
                        ui.label(f"{entry.date_iso} · {entry.language}").classes("text-sm")
                        ui.label(entry.skill_level).classes("text-xs text-[var(--brand)]")

        history.property_changed.subscribe(_render_list)
        _render_list("model")
