from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx import ComponentVMOf, MessageHub, RxDispatcher


@dataclass(frozen=True)
class Attempt:
    text: str = ""
    similarity: Optional[float] = None

    def with_text(self, t: str) -> "Attempt":
        return replace(self, text=t)

    def with_similarity(self, s: float) -> "Attempt":
        return replace(self, similarity=s)


class AttemptVM(ComponentVMOf[Attempt]):
    def set_text(self, t: str) -> None:
        self.model = self.model.with_text(t)


def build_attempt_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    *,
    name: str = "attempt",
    initial_text: str = "",
) -> AttemptVM:
    vm = AttemptVM(
        name=name,
        hint="",
        initial_model=Attempt(text=initial_text),
        modeled_hinter=lambda m: m.text[:20],
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
