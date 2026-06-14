from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from vmx import ComponentVMOf, MessageHub, RxDispatcher


@dataclass(frozen=True)
class Question:
    prompt: str
    options: Tuple[str, ...]
    correct_index: int
    selected_index: Optional[int] = None

    @property
    def is_answered(self) -> bool:
        return self.selected_index is not None

    @property
    def is_correct(self) -> bool:
        return self.is_answered and self.selected_index == self.correct_index


class QuestionVM(ComponentVMOf[Question]):
    def choose(self, idx: int) -> None:
        self.model = replace(self.model, selected_index=idx)


def build_question_vm(
    hub: MessageHub, dispatcher: RxDispatcher, q: Question
) -> QuestionVM:
    vm = QuestionVM(
        name=f"question-{q.prompt[:20]}",
        hint="",
        initial_model=q,
        modeled_hinter=lambda m: m.prompt[:30],
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
