from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Tuple

from vmx import ComponentVMOf, MessageHub, RxDispatcher


@dataclass(frozen=True)
class HistoryEntry:
    language: str
    skill_level: str
    date_iso: str  # YYYY-MM-DD


@dataclass(frozen=True)
class AssessmentHistory:
    selected_language: str = ""
    entries: Tuple[HistoryEntry, ...] = field(default_factory=tuple)

    @property
    def filtered_entries(self) -> tuple[HistoryEntry, ...]:
        if not self.selected_language:
            return self.entries
        return tuple(e for e in self.entries if e.language == self.selected_language)


class AssessmentHistoryVM(ComponentVMOf[AssessmentHistory]):
    def set_entries(self, entries: list[HistoryEntry]) -> None:
        self.model = replace(self.model, entries=tuple(entries))

    def set_language_filter(self, lang: str) -> None:
        if lang != self.model.selected_language:
            self.model = replace(self.model, selected_language=lang)


def build_assessment_history_vm(
    hub: MessageHub, dispatcher: RxDispatcher
) -> AssessmentHistoryVM:
    vm = AssessmentHistoryVM(
        name="assessment-history",
        hint="",
        initial_model=AssessmentHistory(),
        modeled_hinter=lambda m: m.selected_language,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
