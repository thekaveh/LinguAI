from __future__ import annotations
import pytest
from unittest.mock import AsyncMock

from viewmodels.chat.chat_vm import build_chat_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.shell.settings_vm import build_settings_vm


@pytest.fixture
def vm(services):
    hub, dispatcher = services
    return build_chat_vm(
        hub, dispatcher,
        AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock(),
        build_settings_vm(hub, dispatcher),
        build_notification_center(hub, dispatcher),
    )


def test_can_send_false_when_no_llm_or_draft(vm):
    assert not vm.send_command.can_execute()


def test_route_is_chat(vm):
    assert vm.route == "chat"


def test_is_vision_llm_detection(vm):
    class _LLM:
        id = 7
        purpose = "vision-chat"
    vm.set_llm(_LLM())
    assert vm.state.model.is_vision_llm
    assert vm.state.model.can_attach


def test_attach_image_blocked_when_not_vision(vm):
    class _LLM:
        id = 1
        purpose = "content"
    vm.set_llm(_LLM())
    vm.attach_image_bytes(b"hello")
    assert vm.state.model.attached_images_b64 == ()


def test_multi_image_attach_when_vision(vm):
    class _VisionLLM:
        id = 7
        vision = 1
    vm.set_llm(_VisionLLM())
    vm.attach_image_bytes(b"first")
    vm.attach_image_bytes(b"second")
    vm.attach_image_bytes(b"third")
    assert len(vm.state.model.attached_images_b64) == 3


def test_attach_caps_at_max(vm):
    class _VisionLLM:
        id = 7
        vision = 1
    vm.set_llm(_VisionLLM())
    for i in range(vm.MAX_ATTACHMENTS + 2):  # try to add more than allowed
        vm.attach_image_bytes(f"img{i}".encode())
    assert len(vm.state.model.attached_images_b64) == vm.MAX_ATTACHMENTS


def test_remove_attachment(vm):
    class _VisionLLM:
        id = 7
        vision = 1
    vm.set_llm(_VisionLLM())
    vm.attach_image_bytes(b"a")
    vm.attach_image_bytes(b"b")
    vm.attach_image_bytes(b"c")
    vm.remove_attachment(1)
    assert len(vm.state.model.attached_images_b64) == 2
    # 'b' (index 1) gone; 'a' and 'c' remain in order
