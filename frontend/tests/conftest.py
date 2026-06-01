import pytest

from vmx import MessageHub, RxDispatcher


@pytest.fixture
def hub() -> MessageHub:
    return MessageHub()


@pytest.fixture
def dispatcher() -> RxDispatcher:
    return RxDispatcher.immediate()


@pytest.fixture
def services(hub: MessageHub, dispatcher: RxDispatcher):
    return hub, dispatcher
