from __future__ import annotations
import pytest
from dataclasses import replace as dc_replace
from unittest.mock import AsyncMock

from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import (
    build_polyglot_puzzle_vm,
    PolyglotPuzzleVM,
)
from viewmodels.polyglot_puzzle.embeddings_view_vm import build_embeddings_view_vm
from viewmodels.shell.notification_center_vm import build_notification_center

from models.domain.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse


@pytest.fixture
def vm(services) -> PolyglotPuzzleVM:
    hub, dispatcher = services
    puzzle, emb, lang, llm = AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock()
    notif = build_notification_center(hub, dispatcher)
    ev = build_embeddings_view_vm(hub, dispatcher)
    return build_polyglot_puzzle_vm(hub, dispatcher, puzzle, emb, lang, llm, notif, ev)


def test_starts_with_two_empty_attempts(vm: PolyglotPuzzleVM) -> None:
    assert len(vm.attempts) == 2
    assert all(a.model.text == "" for a in vm.attempts)


def test_generate_disabled_until_request_set(vm: PolyglotPuzzleVM) -> None:
    assert not vm.generate_command.can_execute()


def test_add_attempt_disabled_until_response_and_all_filled(vm: PolyglotPuzzleVM) -> None:
    # Set a request + response manually
    req = PolyglotPuzzleRequest(
        src_lang="EN", dst_lang="ES", difficulty="Easy", llm_id=1, llm_temperature=0.0
    )
    resp = PolyglotPuzzleResponse(src_lang_question="Hello", dst_lang_question="Hola")
    vm.state.set_model(dc_replace(vm.state.model, request=req, response=resp))
    # Attempts still empty → cannot add
    assert not vm.add_attempt_command.can_execute()
    for a in vm.attempts:
        a.set_text("hola")
    assert vm.add_attempt_command.can_execute()


def test_submit_disabled_until_response_and_all_filled(vm: PolyglotPuzzleVM) -> None:
    req = PolyglotPuzzleRequest(
        src_lang="EN", dst_lang="ES", difficulty="Easy", llm_id=1, llm_temperature=0.0
    )
    resp = PolyglotPuzzleResponse(src_lang_question="Hello", dst_lang_question="Hola")
    vm.state.set_model(dc_replace(vm.state.model, request=req, response=resp))
    assert not vm.submit_command.can_execute()
    for a in vm.attempts:
        a.set_text("hola")
    assert vm.submit_command.can_execute()
