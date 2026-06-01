from __future__ import annotations
from nicegui import ui

from viewmodels.profile.interest_vm import InterestVM


def render(vm: InterestVM) -> None:
    def _selected_classes() -> str:
        if vm.model.selected:
            return "bg-[var(--brand)] text-[var(--surface-0)]"
        return "bg-white/5 text-[var(--text-2)] hover:bg-white/10"

    chip = ui.label(vm.model.topic_name).classes(
        f"inline-flex items-center px-2 py-0.5 rounded-full text-xs cursor-pointer mr-1 mb-1 {_selected_classes()}"
    )
    chip.on("click", vm.toggle)

    def _refresh(name: str) -> None:
        if name != "model":
            return
        # Rebuild the full classes string to avoid sticking both color sets.
        chip._classes = []  # type: ignore[attr-defined]
        chip.classes(
            f"inline-flex items-center px-2 py-0.5 rounded-full text-xs cursor-pointer mr-1 mb-1 {_selected_classes()}"
        )
        chip.update()

    vm.property_changed.subscribe(_refresh)
