from __future__ import annotations
from dataclasses import dataclass, replace

from vmx import ComponentVMOf, MessageHub, RxDispatcher


@dataclass(frozen=True)
class Interest:
    topic_name: str
    selected: bool = False

    def with_selected(self, s: bool) -> "Interest":
        return replace(self, selected=s)


class InterestVM(ComponentVMOf[Interest]):
    def toggle(self) -> None:
        self.model = self.model.with_selected(not self.model.selected)


def build_interest_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    topic_name: str,
    selected: bool = False,
) -> InterestVM:
    vm = InterestVM(
        name=f"interest-{topic_name}",
        hint="",
        initial_model=Interest(topic_name=topic_name, selected=selected),
        modeled_hinter=lambda m: m.topic_name,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
