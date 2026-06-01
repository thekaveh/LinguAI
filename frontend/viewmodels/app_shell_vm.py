from __future__ import annotations
from typing import Iterable

from vmx import CompositeVM, ComponentVM, MessageHub, RxDispatcher

from viewmodels.shell.navigation_vm import NavigationVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM
from viewmodels.shell.user_session_vm import UserSessionVM


class PageVM(ComponentVM):
    """Marker base for top-level page view-models.

    Subclasses set ``route`` as a class attribute matching a NavigationVM Route literal.

    Note: ComponentVM.builder() is a @staticmethod returning a base ComponentVM.
    PageVM subclasses must be constructed directly via __init__ (or their own factory).
    """

    route: str = "home"


class AppShellVM(CompositeVM[PageVM]):
    """Root VM, per-NiceGUI-client.

    Process-scoped services (hub/dispatcher/http) are passed in;
    everything below is per-client.

    Note: CompositeVM.builder() is a @staticmethod returning a base CompositeVM.
    AppShellVM is constructed directly via __init__ in build_app_shell().
    """

    def _bind(
        self,
        *,
        session: UserSessionVM,
        settings: SettingsVM,
        navigation: NavigationVM,
        notifications: NotificationCenterVM,
        pages: Iterable[PageVM],
    ) -> None:
        """Attach aggregates + children. Called once by the factory after construction."""
        self.session = session
        self.settings = settings
        self.navigation = navigation
        self.notifications = notifications

        for p in pages:
            self.append(p)

        self._route_to_page: dict[str, PageVM] = {p.route: p for p in self}

        # When NavigationVM.model changes, sync our CompositeVM selection.
        def _sync_selection(property_name: str) -> None:
            if property_name != "model":
                return
            target = self._route_to_page.get(self.navigation.model.current)
            if target is not None and self.current is not target:
                self.select_child(target)

        self.navigation.property_changed.subscribe(_sync_selection)
        # Perform initial sync to match starting route.
        _sync_target = self._route_to_page.get(self.navigation.model.current)
        if _sync_target is not None:
            self.select_child(_sync_target)


def build_app_shell(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    *,
    session: UserSessionVM,
    settings: SettingsVM,
    navigation: NavigationVM,
    notifications: NotificationCenterVM,
    pages: Iterable[PageVM],
) -> AppShellVM:
    """Factory: build and construct the root AppShellVM.

    Uses direct __init__ construction because CompositeVM.builder() is a
    @staticmethod that always returns a base CompositeVM, not AppShellVM.
    """
    vm = AppShellVM(
        name="app-shell",
        hint="",
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    vm._bind(
        session=session,
        settings=settings,
        navigation=navigation,
        notifications=notifications,
        pages=pages,
    )
    return vm
