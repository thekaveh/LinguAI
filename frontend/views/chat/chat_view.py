from __future__ import annotations
import asyncio
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.chat.chat_vm import ChatVM
from models.domain.llm import llm_label as _llm_label
from views.theme.components import card, pill_button, section_header, bind_button_enabled
from views.chat.message_bubble import render as render_bubble


def render(shell: AppShellVM) -> None:
    vm: ChatVM = shell._chat_vm  # type: ignore[attr-defined]

    if vm.state.model.persona is None:
        asyncio.create_task(_load_then_finish(vm))

    with ui.row().classes("w-full gap-4"):
        # Conversation pane
        with ui.column().classes("flex-1 gap-2"):
            with card():
                with ui.row().classes("items-center gap-3 w-full"):
                    ui.label().bind_text_from(
                        vm.state, "model",
                        backward=lambda m: m.persona.persona_name if m.persona else "(loading…)",
                    ).classes("text-sm font-semibold tracking-tight")
                    ui.label().bind_text_from(
                        vm.state, "model",
                        backward=lambda m: (
                            f"· {m.llm.display_name()}"
                            if m.llm else ""
                        ),
                    ).classes("text-xs text-[var(--text-3)]")
                    ui.space()
                    pill_button("Clear", on_click=vm.clear_command.execute)

            # Messages
            msg_col = ui.column().classes("gap-3 w-full mt-2 max-h-[58vh] overflow-y-auto")

            def _render_msgs(name: str) -> None:
                if name != "model":
                    return
                msg_col.clear()
                with msg_col:
                    for m in vm.messages:
                        render_bubble(m)

            _render_msgs("model")
            vm.state.property_changed.subscribe(_render_msgs)

            # Composer
            with card().classes("mt-2"):
                # Attachment preview — multiple thumbnails (up to MAX_ATTACHMENTS)
                attached_row = ui.row().classes("gap-2 mb-2 flex-wrap")

                def _render_attach(name: str) -> None:
                    if name != "model":
                        return
                    attached_row.clear()
                    imgs = vm.state.model.attached_images_b64
                    if not imgs:
                        return
                    with attached_row:
                        for i, b64 in enumerate(imgs):
                            with ui.element("div").classes("relative inline-block"):
                                ui.image(
                                    f"data:image/jpeg;base64,{b64}"
                                ).classes("max-w-[100px] max-h-[100px] rounded-md")
                                ui.button(
                                    icon="close",
                                    on_click=_make_remove_attach(vm, i),
                                ).props("flat dense round color=negative size=xs").classes(
                                    "absolute top-1 right-1"
                                )
                        # "Clear all" only when there's more than one
                        if len(imgs) > 1:
                            ui.button(
                                "Clear all", on_click=vm.clear_attachments
                            ).props("flat dense").classes("self-center text-xs")
                _render_attach("model")
                vm.state.property_changed.subscribe(_render_attach)

                with ui.row().classes("items-end gap-2 w-full"):
                    upload = ui.upload(
                        on_upload=_on_upload(vm), auto_upload=True, multiple=True,
                        max_files=vm.MAX_ATTACHMENTS,
                    ).props("flat hide-upload-btn accept=image/*").classes("hidden")
                    upload.bind_visibility_from(vm.state, "model", backward=lambda m: m.can_attach)

                    attach_btn = ui.button(icon="attach_file").props("flat round dense")
                    attach_btn.bind_enabled_from(vm.state, "model", backward=lambda m: m.can_attach)
                    attach_btn.on("click", lambda: upload.pick_files())

                    draft = ui.textarea(placeholder="Type your message…").classes("flex-1") \
                        .props("outlined autogrow dense")
                    draft.on_value_change(lambda e: vm.set_draft(e.value or ""))
                    # Sync draft back when state.draft gets cleared (after send)
                    def _sync_draft(name: str) -> None:
                        if name == "model" and draft.value != vm.state.model.draft:
                            draft.value = vm.state.model.draft
                    vm.state.property_changed.subscribe(_sync_draft)

                    send = ui.button(icon="send", on_click=vm.send_command.execute) \
                        .props("unelevated color=primary round dense")
                    bind_button_enabled(send, vm.send_command)

        # Right rail: session settings
        with ui.column().classes("w-72 gap-2"):
            with card():
                section_header("Session")
                ui.label("Persona").classes("text-xs text-[var(--text-3)] mt-2")
                persona_sel = ui.select([], with_input=True).props("outlined dense").classes("w-full")

                def _refresh_persona(name: str) -> None:
                    if name != "model":
                        return
                    persona_sel.options = [getattr(p, "persona_name", str(p)) for p in vm.state.model.personas]
                    persona_sel.update()
                    if vm.state.model.persona:
                        persona_sel.value = getattr(vm.state.model.persona, "persona_name", None)
                _refresh_persona("model")
                vm.state.property_changed.subscribe(_refresh_persona)
                persona_sel.on_value_change(_on_persona_change(vm))

                ui.label("Model").classes("text-xs text-[var(--text-3)] mt-2")
                llm_sel = ui.select([], with_input=True).props("outlined dense").classes("w-full")

                def _refresh_llm(name: str) -> None:
                    if name != "model":
                        return
                    llm_sel.options = [_llm_label(m) for m in vm.state.model.llms]
                    llm_sel.update()
                    if vm.state.model.llm:
                        llm_sel.value = _llm_label(vm.state.model.llm)
                _refresh_llm("model")
                vm.state.property_changed.subscribe(_refresh_llm)
                llm_sel.on_value_change(_on_llm_change(vm))

                ui.label("Temperature").classes("text-xs text-[var(--text-3)] mt-2")
                slider = ui.slider(min=0.0, max=1.0, step=0.05).props("color=primary dense")
                slider.bind_value_from(vm.state, "model", backward=lambda m: m.temperature)
                slider.on_value_change(lambda e: vm.set_temperature(float(e.value)))

                with ui.row().classes("items-center gap-2 mt-3"):
                    ui.switch("TTS").bind_value_from(
                        vm.state, "model", backward=lambda m: m.tts_enabled
                    ).on_value_change(lambda _: vm.toggle_tts())
                    ui.label().bind_text_from(
                        vm.state, "model",
                        backward=lambda m: "vision" if m.is_vision_llm else "no vision",
                    ).classes("text-xs text-[var(--text-3)] ml-auto")

    # TTS audio player — shown only when a data URL is available; autoplay on each update.
    # NiceGUI ui.audio accepts data URLs in 2.24.x; using ui.audio directly.
    audio_el = ui.audio("").props("autoplay")
    audio_el.bind_source_from(
        vm.state, "model", backward=lambda m: m.last_audio_data_url or ""
    )
    audio_el.bind_visibility_from(
        vm.state, "model", backward=lambda m: bool(m.last_audio_data_url)
    )


def _on_persona_change(vm: ChatVM):  # type: ignore[return]
    def _cb(e: object) -> None:
        target = next(
            (p for p in vm.state.model.personas if getattr(p, "persona_name", None) == getattr(e, "value", None)),
            None,
        )
        if target is not None:
            vm.set_persona(target)
    return _cb


def _on_llm_change(vm: ChatVM):  # type: ignore[return]
    def _cb(e: object) -> None:
        target = next(
            (m for m in vm.state.model.llms if _llm_label(m) == getattr(e, "value", None)),
            None,
        )
        if target is not None:
            vm.set_llm(target)
    return _cb


def _on_upload(vm: ChatVM):  # type: ignore[return]
    async def _cb(e: object) -> None:
        data = getattr(e, "content").read()
        vm.attach_image_bytes(data)
    return _cb


def _make_remove_attach(vm: ChatVM, index: int):  # type: ignore[return]
    def _cb() -> None: vm.remove_attachment(index)
    return _cb


async def _load_then_finish(vm: ChatVM) -> None:
    vm.load_options_command.execute()
