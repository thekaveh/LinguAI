from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional, Tuple

from vmx import ComponentVMOf, MessageHub, RxDispatcher


Role = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class ChatBubble:
    role: Role
    text: str = ""
    timestamp_iso: str = ""
    images_b64: Tuple[str, ...] = ()   # base64-encoded images (for vision)
    is_streaming: bool = False


class ChatMessageVM(ComponentVMOf[ChatBubble]):
    def append_text(self, chunk: str) -> None:
        self.model = replace(self.model, text=self.model.text + chunk)

    def finalize(self) -> None:
        if self.model.is_streaming:
            self.model = replace(self.model, is_streaming=False)


def build_chat_message_vm(hub: MessageHub, dispatcher: RxDispatcher, bubble: ChatBubble) -> ChatMessageVM:
    vm = ChatMessageVM(
        name=f"chat-msg-{bubble.timestamp_iso or bubble.role}", hint="",
        initial_model=bubble,
        modeled_hinter=lambda m: m.text[:30],
        on_model_changed=None,
        hub=hub, dispatcher=dispatcher,
    )
    vm.construct()
    return vm
