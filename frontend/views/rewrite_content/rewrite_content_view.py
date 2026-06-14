from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.rewrite_content.rewrite_content_vm import RewriteContentVM, STYLE_OPTIONS
from models.domain.llm import llm_label as _llm_label
from views.theme.components import card, pill_button, section_header, bind_button_enabled

SKILL_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


def render(shell: AppShellVM) -> None:
    vm: RewriteContentVM = shell._rewrite_content_vm  # type: ignore[attr-defined]

    if not vm.state.model.llms:
        asyncio.create_task(_load(vm))

    with card():
        section_header("Rewrite content", subtitle="Transform a passage to a different style")

        source = (
            ui.textarea("Source text")
            .props("outlined dense autogrow")
            .classes("w-full")
        )
        source.on_value_change(lambda e: vm.set_source_text(e.value or ""))

        with ui.row().classes("gap-3 w-full mt-3"):
            style_sel = (
                ui.select(STYLE_OPTIONS, label="Target style", value=vm.state.model.target_style)
                .props("outlined dense")
                .classes("flex-1")
            )
            style_sel.on_value_change(lambda e: vm.set_target_style(e.value or "formal"))

            # Language is now a select populated from LanguageService (Item #11)
            lang_sel = (
                ui.select([], label="Target language")
                .props("outlined dense")
                .classes("flex-1")
            )

            level_sel = (
                ui.select(SKILL_LEVELS, label="Target level", value=vm.state.model.skill_level)
                .props("outlined dense")
                .classes("flex-1")
            )
            level_sel.on_value_change(lambda e: vm.set_skill_level(e.value or "B1"))

            llm_sel = (
                ui.select([], label="Model")
                .props("outlined dense")
                .classes("flex-1")
            )

        def _refresh(name: str) -> None:
            if name != "model":
                return
            # Language dropdown
            if vm.state.model.languages:
                lang_sel.options = list(vm.state.model.languages)
                lang_sel.update()
                if vm.state.model.language in vm.state.model.languages:
                    lang_sel.value = vm.state.model.language
                else:
                    lang_sel.value = vm.state.model.languages[0]
            # Level select
            level_sel.value = vm.state.model.skill_level
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

        _refresh("model")
        vm.state.property_changed.subscribe(_refresh)

        lang_sel.on_value_change(lambda e: vm.set_language(e.value or "English"))
        llm_sel.on_value_change(_on_llm(vm))

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
            rewrite_btn = pill_button(
                "Rewrite", variant="primary", on_click=vm.rewrite_command.execute
            )
            bind_button_enabled(rewrite_btn, vm.rewrite_command)

    result_card = card()
    result_card.classes("mt-4").bind_visibility_from(
        vm.state, "model", backward=lambda m: bool(m.result)
    )
    with result_card:
        section_header("Result")
        (
            ui.label()
            .bind_text_from(
                vm.state, "model", backward=lambda m: m.result or ""
            )
            .classes("text-sm whitespace-pre-wrap")
        )
        with ui.row().classes("justify-end mt-3"):
            speak = pill_button("🔊 Speak", on_click=vm.speak_command.execute)
            bind_button_enabled(speak, vm.speak_command)

    # TTS audio player — shown only when a data URL is available; autoplay on each update.
    audio_el = ui.audio("").props("autoplay")
    audio_el.bind_source_from(
        vm.state, "model", backward=lambda m: m.last_audio_data_url or ""
    )
    audio_el.bind_visibility_from(
        vm.state, "model", backward=lambda m: bool(m.last_audio_data_url)
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


def _on_llm(vm: RewriteContentVM):  # type: ignore[return]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        target = next(
            (m for m in vm.state.model.llms if _llm_label(m) == e.value),
            None,
        )
        if target is not None:
            vm.set_llm_id(int(getattr(target, "id", 0)))

    return _cb


def _make_delete_history(vm: RewriteContentVM, content_id: int):  # type: ignore[return]
    def _cb() -> None:
        vm.request_delete(content_id)
    return _cb


async def _load(vm: RewriteContentVM) -> None:
    vm.load_command.execute()
