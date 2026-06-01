from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional

from vmx import ComponentVMOf, MessageHub, RxDispatcher


ThemeMode = Literal["system", "light", "dark"]


@dataclass(frozen=True)
class Settings:
    theme_mode: ThemeMode = "system"
    default_llm_id: Optional[str] = None
    default_persona_id: Optional[str] = None


class SettingsVM(ComponentVMOf[Settings]):
    """User-level preferences. Persistence (app.storage.user) is wired by the View layer.

    Note: ComponentVMOf.builder() is a @staticmethod that always returns a base
    ComponentVMOf instance. Subclasses must be constructed directly via __init__.
    """

    def set_theme(self, mode: ThemeMode) -> None:
        self.model = replace(self.model, theme_mode=mode)

    def set_default_llm(self, llm_id: str) -> None:
        self.model = replace(self.model, default_llm_id=llm_id)

    def set_default_persona(self, persona_id: str) -> None:
        self.model = replace(self.model, default_persona_id=persona_id)


def build_settings_vm(hub: MessageHub, dispatcher: RxDispatcher) -> SettingsVM:
    """Factory: build and construct a SettingsVM."""
    vm = SettingsVM(
        name="settings",
        hint="",
        initial_model=Settings(),
        modeled_hinter=lambda m: m.theme_mode,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
