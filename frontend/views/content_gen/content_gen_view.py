from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.content_gen.content_gen_vm import ContentGenVM
from views.theme.components import card, pill_button, section_header, bind_button_enabled


def render(shell: AppShellVM) -> None:
    vm: ContentGenVM = shell._content_gen_vm  # type: ignore[attr-defined]

    if not vm.state.model.languages:
        asyncio.create_task(_load(vm))

    with card():
        section_header("Content reading", subtitle="Generate a passage at your level")
        with ui.row().classes("gap-3 w-full"):
            lang_sel = (
                ui.select([], label="Language")
                .props("outlined dense")
                .classes("flex-1")
            )
            level_sel = (
                ui.select(
                    ["A1", "A2", "B1", "B2", "C1", "C2"],
                    label="Level",
                    value=vm.state.model.skill_level,
                )
                .props("outlined dense")
                .classes("flex-1")
            )
            llm_sel = (
                ui.select([], label="Model")
                .props("outlined dense")
                .classes("flex-1")
            )

        # Topic suggestions chips row (populated by _render_suggestions)
        suggestions_row = ui.row().classes("flex-wrap gap-1 w-full mt-2 mb-1")

        def _render_suggestions(name: str) -> None:
            if name != "model":
                return
            suggestions_row.clear()
            suggested = vm.state.model.suggested_topics
            if not suggested:
                return
            with suggestions_row:
                ui.label("Suggested topics:").classes(
                    "text-xs text-[var(--text-3)] mr-1 self-center"
                )
                for t in suggested[:12]:
                    t_chip = ui.label(t).classes(
                        "inline-flex items-center px-2 py-0.5 rounded-full text-xs cursor-pointer "
                        "bg-white/5 text-[var(--text-2)] hover:bg-white/10"
                    )
                    t_chip.on("click", _make_pick_topic(vm, t))

        _render_suggestions("model")
        vm.state.property_changed.subscribe(_render_suggestions)

        topic = ui.input("Topic").props("outlined dense").classes("w-full mt-1")
        topic.on_value_change(lambda e: vm.set_topic(e.value or ""))

        def _refresh(name: str) -> None:
            if name != "model":
                return
            lang_sel.options = [
                getattr(L, "language_name", str(L)) for L in vm.state.model.languages
            ]
            lang_sel.update()
            if vm.state.model.language:
                lang_sel.value = getattr(vm.state.model.language, "language_name", None)
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
            level_sel.value = vm.state.model.skill_level
            # Reflect chip-click topic changes into the input
            if topic.value != vm.state.model.topic:
                topic.value = vm.state.model.topic

        _refresh("model")
        vm.state.property_changed.subscribe(_refresh)

        lang_sel.on_value_change(_on_lang(vm))
        level_sel.on_value_change(lambda e: vm.set_skill_level(e.value or "B1"))
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
            gen = pill_button(
                "Generate", variant="primary", on_click=vm.generate_command.execute
            )
            bind_button_enabled(gen, vm.generate_command)

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


def _llm_label(llm: object) -> str:
    dn = getattr(llm, "display_name", None)
    if callable(dn):
        return dn()
    return str(dn) if dn else getattr(llm, "model_name", str(llm))


def _on_lang(vm: ContentGenVM):  # type: ignore[return]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        target = next(
            (
                L
                for L in vm.state.model.languages
                if getattr(L, "language_name", None) == e.value
            ),
            None,
        )
        if target is not None:
            vm.set_language(target)

    return _cb


def _on_llm(vm: ContentGenVM):  # type: ignore[return]
    def _cb(e) -> None:  # type: ignore[no-untyped-def]
        target = next(
            (m for m in vm.state.model.llms if _llm_label(m) == e.value),
            None,
        )
        if target is not None:
            vm.set_llm_id(int(getattr(target, "id", 0)))

    return _cb


def _make_pick_topic(vm: ContentGenVM, topic: str):  # type: ignore[return]
    def _cb() -> None:
        vm.set_topic(topic)
    return _cb


def _make_delete_history(vm: ContentGenVM, content_id: int):  # type: ignore[return]
    def _cb() -> None:
        vm.request_delete(content_id)
    return _cb


async def _load(vm: ContentGenVM) -> None:
    vm.load_command.execute()
