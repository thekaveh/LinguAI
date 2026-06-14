from __future__ import annotations
from nicegui import ui

from viewmodels.chat.chat_message_vm import ChatMessageVM


def render(vm: ChatMessageVM) -> None:
    is_user = vm.model.role == "user"
    bubble_cls = (
        "rounded-xl border px-3.5 py-2.5 text-sm leading-relaxed " +
        ("border-[var(--brand)]/20 bg-[var(--brand)]/10 text-orange-100 rounded-tr-sm"
         if is_user else
         "border-white/5 bg-[var(--surface-1)] text-[var(--text-1)] rounded-tl-sm")
    )

    row_cls = ("items-start gap-3 max-w-[84%] " +
               ("self-end flex-row-reverse ml-auto" if is_user else ""))

    with ui.row().classes(row_cls):
        ui.label("YOU" if is_user else "AI").classes(
            "w-7 h-7 rounded-full text-white text-xs font-semibold flex items-center justify-center " +
            ("bg-violet-500" if is_user else "bg-pink-500")
        )
        with ui.column().classes("gap-1"):
            meta = ui.label().classes(
                "text-[10px] text-[var(--text-3)]" + (" text-right" if is_user else "")
            )
            meta.bind_text_from(
                vm, "model",
                backward=lambda m: f"{'You' if m.role == 'user' else 'AI'} · {m.timestamp_iso[11:16]}",
            )
            for img_b64 in vm.model.images_b64:
                ui.image(f"data:image/jpeg;base64,{img_b64}").classes("max-w-xs rounded-lg mt-1")
            text_lbl = ui.label().classes(bubble_cls)
            text_lbl.bind_text_from(
                vm, "model",
                backward=lambda m: m.text + (" ▎" if m.is_streaming else ""),
            )
