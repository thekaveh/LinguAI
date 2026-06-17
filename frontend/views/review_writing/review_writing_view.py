from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.review_writing.review_writing_vm import ReviewWritingVM
from models.domain.llm import llm_label as _llm_label
from models.schemas.skill_level import SKILL_LEVELS
from views.theme.components import card, pill_button, section_header, bind_button_enabled


def render(shell: AppShellVM) -> None:
    vm: ReviewWritingVM = shell._review_writing_vm  # type: ignore[attr-defined]

    if not vm.state.model.llms:
        asyncio.create_task(_load(vm))

    with card():
        section_header("Review writing", subtitle="Get feedback on your writing")

        content_area = (
            ui.textarea("Your writing")
            .props("outlined dense autogrow")
            .classes("w-full")
        )
        content_area.on_value_change(lambda e: vm.set_input_content(e.value or ""))

        ui.label().bind_text_from(
            vm.state, "model",
            backward=lambda m: (
                f"\U0001f4dd Detected: {m.detected_language}" if m.detected_language else ""
            ),
        ).classes("text-xs text-[var(--text-3)] mt-1")

        with ui.row().classes("gap-3 w-full mt-3"):
            # NOTE: do NOT pass `value=` to ui.select() when options=[] — Quasar
            # silently aborts rendering of subsequent siblings if the initial
            # value isn't in the options list. _refresh() below sets the value
            # once options have loaded.
            lang_sel = (
                ui.select([], label="Language")
                .props("outlined dense")
                .classes("flex-1")
            )

            curr_sel = (
                ui.select(
                    SKILL_LEVELS,
                    label="Current level",
                    value=vm.state.model.curr_skill_level,
                )
                .props("outlined dense")
                .classes("flex-1")
            )

            next_sel = (
                ui.select(
                    SKILL_LEVELS,
                    label="Target level",
                    value=vm.state.model.next_skill_level,
                )
                .props("outlined dense")
                .classes("flex-1")
            )

            llm_sel = (
                ui.select([], label="Model")
                .props("outlined dense")
                .classes("flex-1")
            )

        def _refresh(name: str) -> None:
            if name != "model":
                return
            # Populate language dropdown from loaded languages
            lang_names = [
                getattr(L, "language_name", str(L))
                for L in vm.state.model.languages
            ]
            if lang_names:
                lang_sel.options = lang_names
                lang_sel.update()
                if vm.state.model.language not in lang_names:
                    lang_sel.value = lang_names[0]
                else:
                    lang_sel.value = vm.state.model.language
            # LLM dropdown
            llm_sel.options = [_llm_label(m) for m in vm.state.model.llms]
            llm_sel.update()
            if vm.state.model.llm_id:
                llm_sel.value = next(
                    (
                        _llm_label(m)
                        for m in vm.state.model.llms
                        if int(getattr(m, "id", 0)) == vm.state.model.llm_id
                    ),
                    None,
                )
            # Keep level selects in sync
            curr_sel.value = vm.state.model.curr_skill_level
            next_sel.value = vm.state.model.next_skill_level

        _refresh("model")
        vm.state.property_changed.subscribe(_refresh)

        lang_sel.on_value_change(lambda e: vm.set_language(e.value or "English"))
        curr_sel.on_value_change(lambda e: vm.set_curr_skill_level(e.value or "B1"))
        next_sel.on_value_change(lambda e: vm.set_next_skill_level(e.value or "B2"))
        llm_sel.on_value_change(_on_llm(vm))

        with ui.row().classes("gap-3 w-full mt-3"):
            strength_input = (
                ui.input("Strength (optional)")
                .props("outlined dense")
                .classes("flex-1")
            )
            strength_input.on_value_change(lambda e: vm.set_strength(e.value or ""))

            weakness_input = (
                ui.input("Weakness (optional)")
                .props("outlined dense")
                .classes("flex-1")
            )
            weakness_input.on_value_change(lambda e: vm.set_weakness(e.value or ""))

        with ui.row().classes("items-center gap-3 mt-3"):
            ui.label("Temperature").classes("text-xs text-[var(--text-3)]")
            slider = (
                ui.slider(min=0.0, max=1.0, step=0.05)
                .props("color=primary dense")
                .classes("w-40")
            )
            slider.bind_value_from(
                vm.state, "model", backward=lambda m: m.temperature
            )
            slider.on_value_change(lambda e: vm.set_temperature(float(e.value)))
            ui.space()
            review_btn = pill_button(
                "Get feedback", variant="primary", on_click=vm.review_command.execute
            )
            bind_button_enabled(review_btn, vm.review_command)

    result_card = card()
    result_card.classes("mt-4").bind_visibility_from(
        vm.state, "model", backward=lambda m: bool(m.result)
    )
    with result_card:
        section_header("Feedback")
        (
            ui.label()
            .bind_text_from(
                vm.state, "model", backward=lambda m: m.result or ""
            )
            .classes("text-sm whitespace-pre-wrap")
        )

    # History section
    with ui.expansion("History", icon="history").classes("mt-4 w-full"):
        history_container = ui.column().classes("w-full gap-1")

        def _render_history(name: str) -> None:
            if name != "model":
                return
            history_container.clear()
            items = vm.state.model.history
            with history_container:
                if not items:
                    ui.label("No saved generations yet.").classes(
                        "text-sm text-[var(--text-3)]"
                    )
                    return
                for item in items:
                    with ui.row().classes(
                        "w-full items-start gap-2 py-2 border-b border-white/5"
                    ):
                        with ui.column().classes("flex-1 gap-0"):
                            meta = []
                            if item.language:
                                meta.append(item.language)
                            if item.level:
                                meta.append(item.level)
                            if item.created_date:
                                meta.append(str(item.created_date)[:10])
                            ui.label(" · ".join(meta) or "untitled").classes(
                                "text-xs text-[var(--text-3)]"
                            )
                            gen_text = item.gen_content or ""
                            preview = gen_text[:200]
                            ui.label(
                                preview + ("…" if len(gen_text) > 200 else "")
                            ).classes("text-sm text-[var(--text-2)] whitespace-pre-wrap")
                        ui.button(
                            icon="delete",
                            on_click=_make_delete_history(vm, item.id),
                        ).props("flat dense round color=negative")

        _render_history("model")
        vm.state.property_changed.subscribe(_render_history)


def _on_llm(vm: ReviewWritingVM):  # type: ignore[return]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        target = next(
            (m for m in vm.state.model.llms if _llm_label(m) == e.value),
            None,
        )
        if target is not None:
            vm.set_llm_id(int(getattr(target, "id", 0)))

    return _cb


def _make_delete_history(vm: ReviewWritingVM, content_id: int):  # type: ignore[return]
    def _cb() -> None:
        vm.request_delete(content_id)
    return _cb


async def _load(vm: ReviewWritingVM) -> None:
    vm.load_command.execute()
