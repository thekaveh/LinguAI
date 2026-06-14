from viewmodels.shell.navigation_vm import build_navigation_vm


def test_navigation_starts_at_home(services):
    vm = build_navigation_vm(*services)
    assert vm.model.current == "home"
    assert vm.model.drawer_open is True


def test_go_updates_route(services):
    vm = build_navigation_vm(*services)
    vm.go("chat")
    assert vm.model.current == "chat"


def test_toggle_drawer_flips_state(services):
    vm = build_navigation_vm(*services)
    vm.toggle_drawer()
    assert vm.model.drawer_open is False
    vm.toggle_drawer()
    assert vm.model.drawer_open is True
