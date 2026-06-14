from viewmodels.shell.settings_vm import build_settings_vm


def test_settings_default_theme_is_system(services):
    vm = build_settings_vm(*services)
    assert vm.model.theme_mode == "system"


def test_set_theme_updates_model(services):
    vm = build_settings_vm(*services)
    vm.set_theme("dark")
    assert vm.model.theme_mode == "dark"
