from __future__ import annotations
import pytest
from unittest.mock import AsyncMock

import httpx

from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.home.home_vm import build_home_vm


@pytest.fixture
def home(services):  # type: ignore[no-untyped-def]
    hub, dispatcher = services
    auth = AsyncMock()
    http = httpx.AsyncClient(base_url="http://test")
    session = build_user_session_vm(hub, dispatcher, auth, http)
    return build_home_vm(hub, dispatcher, session)


def test_home_route(home):  # type: ignore[no-untyped-def]
    assert home.route == "home"


def test_home_initial_model(home):  # type: ignore[no-untyped-def]
    assert home.model.languages_in_progress == 0
    assert home.model.last_session_label == "(none yet)"
    assert home.model.skill_cards == ()
    assert home.model.has_assessments is False
