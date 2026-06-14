from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from vmx import GroupVM, ComponentVMOf, MessageHub, RxDispatcher


Severity = Literal["success", "info", "warning", "error"]


@dataclass(frozen=True)
class Toast:
    severity: Severity
    message: str


class ToastVM(ComponentVMOf[Toast]):
    """Single toast — child of NotificationCenterVM."""


class NotificationCenterVM(GroupVM[ToastVM]):
    """Peer collection of toast VMs.

    Views subscribe to ``on_collection_changed`` and render via ``ui.notify``.

    Subscriber arity note: ``GroupVM.on_collection_changed`` emits
    ``CollectionChangedEvent`` objects, so subscriber callbacks must accept
    exactly one argument. The most common pattern is
    ``notifications.on_collection_changed.subscribe(lambda _evt: ...)``.

    Note: _hub and _dispatcher are stored by _ComponentVMBase.__init__ (which
    GroupVM calls at construction time); push_* methods access them directly
    since this is a subclass of GroupVM.
    """

    def push_success(self, message: str) -> None:
        self._push("success", message)

    def push_info(self, message: str) -> None:
        self._push("info", message)

    def push_warning(self, message: str) -> None:
        self._push("warning", message)

    def push_error(self, message: str) -> None:
        self._push("error", message)

    def _push(self, severity: Severity, message: str) -> None:
        toast = Toast(severity=severity, message=message)
        # _hub and _dispatcher are set by _ComponentVMBase.__init__ (GroupVM's base);
        # they are always available after construction.
        vm = ToastVM(
            name=f"toast-{self.count}",
            hint="",
            initial_model=toast,
            modeled_hinter=lambda m: m.message,
            on_model_changed=None,
            hub=self._hub,
            dispatcher=self._dispatcher,
        )
        vm.construct()
        self.append(vm)


def build_notification_center(hub: MessageHub, dispatcher: RxDispatcher) -> NotificationCenterVM:
    """Factory: build and construct a NotificationCenterVM.

    GroupVM subclasses cannot use the GroupVMBuilder (it always returns a base
    GroupVM instance). We construct directly via __init__ instead.
    """
    vm = NotificationCenterVM(
        name="notifications",
        hint="",
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
