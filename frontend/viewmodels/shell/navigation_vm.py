from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal

from vmx import ComponentVMOf, MessageHub, RxDispatcher


Route = Literal[
    "home", "chat", "content_gen", "rewrite_content", "review_writing",
    "polyglot_puzzle", "profile", "assessment", "admin", "register", "login",
]


@dataclass(frozen=True)
class NavigationState:
    current: Route = "home"
    drawer_open: bool = True


class NavigationVM(ComponentVMOf[NavigationState]):
    """Navigation state for the app shell.

    Note: ComponentVMOf.builder() is a @staticmethod returning a base ComponentVMOf.
    This subclass is constructed directly via __init__ in the factory function.
    """

    def go(self, route: Route) -> None:
        if route != self.model.current:
            self.model = replace(self.model, current=route)

    def toggle_drawer(self) -> None:
        self.model = replace(self.model, drawer_open=not self.model.drawer_open)


def build_navigation_vm(hub: MessageHub, dispatcher: RxDispatcher) -> NavigationVM:
    """Factory: build and construct a NavigationVM."""
    vm = NavigationVM(
        name="navigation",
        hint="",
        initial_model=NavigationState(),
        modeled_hinter=lambda m: m.current,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
