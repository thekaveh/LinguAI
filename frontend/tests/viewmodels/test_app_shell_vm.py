import pytest
import httpx

from viewmodels.app_shell_vm import build_app_shell, PageVM
from viewmodels.shell.navigation_vm import build_navigation_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.shell.settings_vm import build_settings_vm
from viewmodels.shell.user_session_vm import build_user_session_vm
from models.services.auth_service import AuthService


class _FakePage(PageVM):
    """Minimal page subclass for testing. route is set per-instance after construction."""


def _build_fake_page(hub, dispatcher, route: str) -> _FakePage:
    # PageVM subclasses ComponentVM (non-modeled). Direct __init__ construction is
    # required because ComponentVM.builder() is a @staticmethod returning a base
    # ComponentVM, not the subclass.
    vm = _FakePage(name=f"page-{route}", hint="", hub=hub, dispatcher=dispatcher)
    vm.route = route
    vm.construct()
    return vm


@pytest.fixture
def shell(services):
    hub, dispatcher = services
    http = httpx.AsyncClient(base_url="http://example.test")
    auth = AuthService(http)  # stub — authenticate() raises NotImplementedError, never called here
    return build_app_shell(
        hub, dispatcher,
        session=build_user_session_vm(hub, dispatcher, auth, http),
        settings=build_settings_vm(hub, dispatcher),
        navigation=build_navigation_vm(hub, dispatcher),
        notifications=build_notification_center(hub, dispatcher),
        pages=[
            _build_fake_page(hub, dispatcher, "home"),
            _build_fake_page(hub, dispatcher, "chat"),
        ],
    )


def test_initial_selection_matches_navigation(shell):
    assert shell.current is not None
    assert shell.current.route == "home"


def test_navigation_change_updates_selection(shell):
    shell.navigation.go("chat")
    assert shell.current is not None
    assert shell.current.route == "chat"
