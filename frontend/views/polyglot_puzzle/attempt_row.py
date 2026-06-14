from __future__ import annotations
from nicegui import ui

from viewmodels.polyglot_puzzle.attempt_vm import AttemptVM


def render(vm: AttemptVM) -> None:
    with ui.row().classes("items-center gap-2 w-full"):
        inp = ui.input("Your translation", value=vm.model.text) \
            .props("outlined dense").classes("flex-1")
        inp.on_value_change(lambda e: vm.set_text(e.value or ""))
        # similarity badge (only visible once submitted)
        ui.label().bind_text_from(
            vm, "model",
            backward=lambda m: "" if m.similarity is None else f"{m.similarity*100:.0f}%",
        ).classes("text-xs text-[var(--text-3)] w-12 text-right")
