"""
Full headless VM-tree integration test.

Exercises the entire AppShellVM tree — every shell aggregate, every page VM,
and every primary command — against a mocked backend. No NiceGUI, no real HTTP.

Pattern:
  - build_shell() constructs the production DI graph.
  - httpx.AsyncClient is built with base_url="http://test/v1"; respx.mock() intercepts
    all requests at the transport layer, so the real /v1 prefix wiring is exercised.
  - Commands use asyncio.create_task(); we drain the event loop with asyncio.sleep(0)
    (multiple yields) to let coroutines settle.

Bug-fixes recorded here:
  - (none found during test authoring — all wiring was correct)
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest
import respx

from vmx import MessageHub, RxDispatcher

from core.config import AppConfig
from core.di import build_shell
from core.http import build_http_client
from models.services.auth_service import AuthService
from viewmodels.app_shell_vm import AppShellVM


# ---------------------------------------------------------------------------
# Shared response payloads
# ---------------------------------------------------------------------------

_LANGUAGES_JSON = [
    {"language_name": "English", "language_id": 1},
    {"language_name": "Spanish", "language_id": 2},
]

_TOPICS_JSON = [
    {"topic_name": "Travel", "topic_id": 1},
    {"topic_name": "Food", "topic_id": 2},
]

_PERSONAS_JSON = [
    {
        "persona_id": 1,
        "persona_name": "Tutor",
        "description": "A patient language tutor.",
        "is_default": True,
    },
]

# LLM shape — all numeric capability fields required (default -1 means "not capable").
_LLM_CONTENT_JSON = [
    {
        "id": 10,
        "name": "gpt-4",
        "provider": "openai",
        "is_active": True,
        "vision": -1,
        "content": 1,
        "structured_content": -1,
        "embeddings": -1,
    },
]

_LLM_STRUCTURED_JSON = [
    {
        "id": 11,
        "name": "gpt-4-turbo",
        "provider": "openai",
        "is_active": True,
        "vision": -1,
        "content": -1,
        "structured_content": 1,
        "embeddings": -1,
    },
]

_LLM_EMBEDDINGS_JSON = [
    {
        "id": 12,
        "name": "text-embedding-ada-002",
        "provider": "openai",
        "is_active": True,
        "vision": -1,
        "content": -1,
        "structured_content": -1,
        "embeddings": 1,
    },
]

_USER_ALICE_JSON = {
    "user_id": 1,
    "username": "alice",
    "email": "alice@example.com",
    "user_type": "admin",
    "first_name": "Alice",
    "last_name": "Test",
}


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def cfg() -> AppConfig:
    return AppConfig(backend_endpoint="http://test", frontend_log_file="/tmp/test.log")


@pytest.fixture
def mock_backend() -> Any:
    """
    Open a respx mock router that pre-registers stubs for every endpoint the
    VM tree might touch at construction / load time.

    assert_all_called=False — we only assert on the VMs we exercise, not that
    every route was hit.
    """
    with respx.mock(assert_all_called=False) as router:
        # ---- reference data lists ----
        router.get("http://test/v1/languages/list").mock(
            return_value=httpx.Response(200, json=_LANGUAGES_JSON)
        )
        router.get("http://test/v1/topics/list").mock(
            return_value=httpx.Response(200, json=_TOPICS_JSON)
        )
        router.get("http://test/v1/personas/").mock(
            return_value=httpx.Response(200, json=_PERSONAS_JSON)
        )

        # ---- LLM variants ----
        router.get("http://test/v1/llms/all/").mock(
            return_value=httpx.Response(200, json=_LLM_CONTENT_JSON + _LLM_STRUCTURED_JSON + _LLM_EMBEDDINGS_JSON)
        )
        router.get("http://test/v1/llms/content/").mock(
            return_value=httpx.Response(200, json=_LLM_CONTENT_JSON)
        )
        router.get("http://test/v1/llms/structured_content/").mock(
            return_value=httpx.Response(200, json=_LLM_STRUCTURED_JSON)
        )
        router.get("http://test/v1/llms/embeddings/").mock(
            return_value=httpx.Response(200, json=_LLM_EMBEDDINGS_JSON)
        )
        router.get("http://test/v1/llms/vision/").mock(
            return_value=httpx.Response(200, json=[])
        )

        # ---- user endpoints ----
        router.get("http://test/v1/users/username/alice").mock(
            return_value=httpx.Response(200, json=_USER_ALICE_JSON)
        )
        router.get("http://test/v1/users/username/alice/id").mock(
            return_value=httpx.Response(200, json=1)
        )

        # ---- auth ----
        router.post("http://test/v1/users/authenticate").mock(
            return_value=httpx.Response(
                200,
                json={"status": True, "username": "alice", "message": "Login successful"},
            )
        )

        # ---- admin ping ----
        router.get("http://test/v1/health").mock(
            return_value=httpx.Response(200, json={"message": "pong"})
        )

        yield router


@pytest.fixture
def http(cfg: AppConfig) -> httpx.AsyncClient:
    """Production-shaped client; respx intercepts at transport level."""
    return build_http_client(cfg)


@pytest.fixture
def shell(http: httpx.AsyncClient, mock_backend: Any) -> AppShellVM:
    """Full VM tree wired the same way main.py does it."""
    hub = MessageHub()
    dispatcher = RxDispatcher.immediate()
    auth = AuthService(http)
    return build_shell(hub, dispatcher, http, auth)


# ---------------------------------------------------------------------------
# 1. Smoke — tree construction
# ---------------------------------------------------------------------------

def test_shell_constructs_with_all_page_vms(shell: AppShellVM) -> None:
    """Every VM in the tree builds without error."""
    assert shell.session is not None
    assert shell.settings is not None
    assert shell.navigation is not None
    assert shell.notifications is not None
    assert hasattr(shell, "_polyglot_vm")
    assert hasattr(shell, "_chat_vm")
    assert hasattr(shell, "_profile_vm")
    assert hasattr(shell, "_assessment_vm")
    assert hasattr(shell, "_content_gen_vm")
    assert hasattr(shell, "_rewrite_content_vm")
    assert hasattr(shell, "_review_writing_vm")
    assert hasattr(shell, "_admin_vm")


# ---------------------------------------------------------------------------
# 2. Navigation
# ---------------------------------------------------------------------------

def test_navigation_initial_route_is_home(shell: AppShellVM) -> None:
    assert shell.navigation.model.current == "home"


def test_navigation_go_changes_current_route(shell: AppShellVM) -> None:
    shell.navigation.go("chat")
    assert shell.navigation.model.current == "chat"


def test_navigation_go_to_all_routes(shell: AppShellVM) -> None:
    """Verify every declared route is accepted without error."""
    routes = ["home", "chat", "content_gen", "rewrite_content", "review_writing",
              "polyglot_puzzle", "profile", "assessment", "admin"]
    for route in routes:
        shell.navigation.go(route)
        assert shell.navigation.model.current == route


def test_navigation_toggle_drawer(shell: AppShellVM) -> None:
    initial = shell.navigation.model.drawer_open
    shell.navigation.toggle_drawer()
    assert shell.navigation.model.drawer_open is not initial


def test_navigation_change_syncs_appshell_selection(shell: AppShellVM) -> None:
    """AppShellVM.current (CompositeVM selection) syncs with NavigationVM.

    The shell has HomeVM as its only registered PageVM child; navigation to
    other routes (which aren't in _route_to_page) leaves current unchanged but
    NavigationVM.model.current updates correctly.
    """
    # HomeVM is in the composite's page list.
    shell.navigation.go("home")
    assert shell.navigation.model.current == "home"
    # current is the selected child VM (HomeVM).
    assert shell.current is not None
    assert shell.current.route == "home"


# ---------------------------------------------------------------------------
# 3. Settings
# ---------------------------------------------------------------------------

def test_settings_set_theme_fires_property_changed(shell: AppShellVM) -> None:
    observed: list[str] = []
    shell.settings.property_changed.subscribe(observed.append)
    shell.settings.set_theme("dark")
    assert shell.settings.model.theme_mode == "dark"
    assert "model" in observed


def test_settings_set_theme_light(shell: AppShellVM) -> None:
    shell.settings.set_theme("light")
    assert shell.settings.model.theme_mode == "light"


def test_settings_set_default_llm(shell: AppShellVM) -> None:
    shell.settings.set_default_llm("llm-42")
    assert shell.settings.model.default_llm_id == "llm-42"


# ---------------------------------------------------------------------------
# 4. Notifications
# ---------------------------------------------------------------------------

def test_notifications_push_success_increments_count(shell: AppShellVM) -> None:
    assert shell.notifications.count == 0
    shell.notifications.push_success("hello")
    assert shell.notifications.count == 1


def test_notifications_subscriber_fires_before_push(shell: AppShellVM) -> None:
    """Subscriber registered BEFORE push must receive the event.

    on_collection_changed emits a CollectionChangedEvent; the subscriber must
    accept it as a positional argument.
    """
    fired: list[bool] = []
    # GroupVM.on_collection_changed emits CollectionChangedEvent objects.
    shell.notifications.on_collection_changed.subscribe(lambda _evt: fired.append(True))
    shell.notifications.push_info("world")
    assert fired, "on_collection_changed did not fire"


def test_notifications_all_severities(shell: AppShellVM) -> None:
    shell.notifications.push_success("ok")
    shell.notifications.push_info("info")
    shell.notifications.push_warning("warn")
    shell.notifications.push_error("err")
    assert shell.notifications.count == 4


# ---------------------------------------------------------------------------
# 5. Auth — login + logout full flow
# ---------------------------------------------------------------------------

async def test_login_full_flow(shell: AppShellVM) -> None:
    """
    log_in → is_authenticated, user_type=admin, is_admin.
    The get_by_username follow-up is pre-registered in mock_backend.
    """
    ok = await shell.session.log_in("alice", "secret")
    # log_in fires a create_task to enrich user_type; drain the loop.
    for _ in range(4):
        await asyncio.sleep(0)

    assert ok is True
    assert shell.session.model.is_authenticated
    assert shell.session.model.username == "alice"
    assert shell.session.model.user_type == "admin"
    assert shell.session.model.is_admin is True


async def test_logout_clears_session(shell: AppShellVM) -> None:
    await shell.session.log_in("alice", "secret")
    for _ in range(4):
        await asyncio.sleep(0)
    assert shell.session.model.is_authenticated

    await shell.session.log_out()
    assert not shell.session.model.is_authenticated
    assert shell.session.model.token is None
    assert shell.session.model.username is None


# ---------------------------------------------------------------------------
# 6. LoginVM — standalone (lazy, built per call)
# ---------------------------------------------------------------------------

async def test_login_vm_standalone(shell: AppShellVM, mock_backend: Any) -> None:
    """Build LoginVM against the mocked session and drive login_command."""
    from viewmodels.auth.login_vm import build_login_vm

    vm, cmd = build_login_vm(
        shell.navigation._hub,  # type: ignore[attr-defined]
        shell.navigation._dispatcher,  # type: ignore[attr-defined]
        shell.session,
        shell.notifications,
    )
    assert not cmd.can_execute()  # fields empty

    vm.set_username("alice")
    vm.set_password("s3cret")
    assert cmd.can_execute()

    cmd.execute()
    for _ in range(6):
        await asyncio.sleep(0)

    assert shell.session.model.is_authenticated
    assert shell.session.model.is_admin is True
    assert vm.model.username == ""  # cleared after success


# ---------------------------------------------------------------------------
# 7. PolyglotPuzzleVM — load options then generate
# ---------------------------------------------------------------------------

async def test_polyglot_load_options(shell: AppShellVM) -> None:
    vm = shell._polyglot_vm  # type: ignore[attr-defined]
    assert vm.state.model.request is None  # initial state

    vm.load_options_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    m = vm.state.model
    assert m.request is not None
    assert "English" in m.src_langs
    assert m.embeddings_llm_id == 12  # from _LLM_EMBEDDINGS_JSON


async def test_polyglot_generate(shell: AppShellVM, mock_backend: Any) -> None:
    """load_options then generate — response populates model."""
    mock_backend.post("http://test/v1/polyglot_puzzle/generate").mock(
        return_value=httpx.Response(
            200,
            json={"src_lang_question": "How are you?", "dst_lang_question": "¿Cómo estás?"},
        )
    )

    vm = shell._polyglot_vm  # type: ignore[attr-defined]
    vm.load_options_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    assert vm.generate_command.can_execute(), "generate should be enabled after load"

    vm.generate_command.execute()
    for _ in range(6):
        await asyncio.sleep(0)

    assert vm.state.model.has_response
    assert vm.state.model.response is not None
    assert vm.state.model.response.dst_lang_question == "¿Cómo estás?"


# ---------------------------------------------------------------------------
# 8. ChatVM — load options
# ---------------------------------------------------------------------------

async def test_chat_load_options(shell: AppShellVM) -> None:
    vm = shell._chat_vm  # type: ignore[attr-defined]
    assert vm.state.model.persona is None

    vm.load_options_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    m = vm.state.model
    assert m.persona is not None
    assert m.persona.persona_name == "Tutor"
    assert m.llm is not None
    assert len(m.personas) >= 1
    assert len(m.llms) >= 1


async def test_chat_send_message(shell: AppShellVM, mock_backend: Any) -> None:
    """Load options, set draft, send — response appended as assistant message."""
    mock_backend.post("http://test/v1/chat").mock(
        return_value=httpx.Response(200, text="Hola, ¿cómo estás?")
    )

    vm = shell._chat_vm  # type: ignore[attr-defined]
    vm.load_options_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    vm.set_draft("Hello!")
    assert vm.send_command.can_execute()

    vm.send_command.execute()
    # The send command streams; give it several ticks.
    for _ in range(10):
        await asyncio.sleep(0)

    # At least 2 messages: user + assistant.
    assert len(vm.messages) >= 2
    # The last message (assistant) should be finalized with text.
    last = vm.messages[-1]
    assert last.model.role == "assistant"
    assert last.model.text != ""


# ---------------------------------------------------------------------------
# 9. ContentGenVM — load options then generate
# ---------------------------------------------------------------------------

async def test_content_gen_load_options(shell: AppShellVM) -> None:
    vm = shell._content_gen_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    m = vm.state.model
    assert m.language is not None
    assert m.llm_id != 0


async def test_content_gen_generate(shell: AppShellVM, mock_backend: Any) -> None:
    mock_backend.post("http://test/v1/content_gen/gen_by_content_topic").mock(
        return_value=httpx.Response(200, text="Great travel content in English!")
    )
    # content_gen also tries to get user_id — stub that too.
    mock_backend.get("http://test/v1/users/username/alice/id").mock(
        return_value=httpx.Response(200, json=1)
    )

    vm = shell._content_gen_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    vm.set_topic("Travel")
    assert vm.generate_command.can_execute()

    vm.generate_command.execute()
    for _ in range(10):
        await asyncio.sleep(0)

    assert "travel" in vm.state.model.result.lower() or vm.state.model.result != ""


# ---------------------------------------------------------------------------
# 10. RewriteContentVM — load options then rewrite
# ---------------------------------------------------------------------------

async def test_rewrite_content_load(shell: AppShellVM) -> None:
    vm = shell._rewrite_content_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    assert vm.state.model.llm_id != 0


async def test_rewrite_content_rewrite(shell: AppShellVM, mock_backend: Any) -> None:
    mock_backend.post("http://test/v1/rewrite_content/").mock(
        return_value=httpx.Response(200, text="Rewritten formally.")
    )

    vm = shell._rewrite_content_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    vm.set_source_text("Hello world, how are you doing today?")
    vm.set_target_style("formal")
    assert vm.rewrite_command.can_execute()

    vm.rewrite_command.execute()
    for _ in range(10):
        await asyncio.sleep(0)

    assert vm.state.model.result != ""


# ---------------------------------------------------------------------------
# 11. ReviewWritingVM — load then review
# ---------------------------------------------------------------------------

async def test_review_writing_load(shell: AppShellVM) -> None:
    vm = shell._review_writing_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    assert vm.state.model.llm_id != 0


async def test_review_writing_review(shell: AppShellVM, mock_backend: Any) -> None:
    mock_backend.post("http://test/v1/review_writing/").mock(
        return_value=httpx.Response(200, text="Your writing is clear and concise.")
    )

    vm = shell._review_writing_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    vm.set_input_content("This is my writing sample for review.")
    vm.set_curr_skill_level("B1")
    assert vm.review_command.can_execute()

    vm.review_command.execute()
    for _ in range(10):
        await asyncio.sleep(0)

    assert vm.state.model.result != ""


# ---------------------------------------------------------------------------
# 12. ProfileVM — load (requires authenticated session)
# ---------------------------------------------------------------------------

async def test_profile_load_when_authenticated(shell: AppShellVM, mock_backend: Any) -> None:
    """ProfileVM auto-loads on session authentication. Drive manually too."""
    # Extra endpoints needed by _do_load: get_by_username (user with topics) + topics/list
    # Both are already pre-registered in mock_backend.

    # Authenticate so profile knows the username.
    ok = await shell.session.log_in("alice", "secret")
    for _ in range(4):
        await asyncio.sleep(0)
    assert ok

    # Profile's _on_session_changed subscribed to session; it may have auto-loaded.
    # Manually trigger to be sure.
    vm = shell._profile_vm  # type: ignore[attr-defined]
    vm.load_command.execute()
    for _ in range(6):
        await asyncio.sleep(0)

    assert vm.state.model.username == "alice"
    assert vm.state.model.email == "alice@example.com"


# ---------------------------------------------------------------------------
# 13. AssessmentVM
# ---------------------------------------------------------------------------

async def test_assessment_set_language_builds_questions(shell: AppShellVM) -> None:
    vm = shell._assessment_vm  # type: ignore[attr-defined]
    vm.set_language("Spanish")
    assert vm.state.model.language == "Spanish"
    assert len(vm.questions) > 0


async def test_assessment_submit(shell: AppShellVM, mock_backend: Any) -> None:
    """Answer all questions correctly, submit, assert completed_score is set."""
    # Need authenticated session + user_id for the submission.
    await shell.session.log_in("alice", "secret")
    for _ in range(4):
        await asyncio.sleep(0)

    # Stub the assessment POST endpoint.
    from datetime import datetime, timezone
    mock_backend.post("http://test/v1/users/1/assessments/").mock(
        return_value=httpx.Response(
            200,
            json={
                "assessment_id": 100,
                "user_id": 1,
                "skill_level": "B1",
                "assessment_type": "placement",
                "assessment_date": datetime.now(timezone.utc).isoformat(),
                "language": {"language_id": 2, "language_name": "Spanish"},
            },
        )
    )
    # Stub get_by_name for language lookup.
    mock_backend.get("http://test/v1/languages/Spanish").mock(
        return_value=httpx.Response(200, json={"language_id": 2, "language_name": "Spanish"})
    )

    vm = shell._assessment_vm  # type: ignore[attr-defined]
    vm.set_language("Spanish")

    # Answer all questions with the correct index.
    # QuestionVM exposes .choose(idx: int) — not .select().
    for q in vm.questions:
        q.choose(q.model.correct_index)

    assert vm.all_answered
    assert vm.submit_command.can_execute()

    vm.submit_command.execute()
    for _ in range(8):
        await asyncio.sleep(0)

    assert vm.state.model.completed_score is not None


# ---------------------------------------------------------------------------
# 14. AdminVM — ping command
# ---------------------------------------------------------------------------

async def test_admin_ping(shell: AppShellVM) -> None:
    vm = shell._admin_vm  # type: ignore[attr-defined]
    assert vm.state.model.last_ping == "(no ping yet)"

    vm.ping_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    assert vm.state.model.last_ping == "pong"
    # Notification pushed: success toast.
    assert shell.notifications.count >= 1


# ---------------------------------------------------------------------------
# 15. MessageHub — PropertyChangedMessage flows when VM model changes
# ---------------------------------------------------------------------------

def test_hub_propagates_property_changed_message(shell: AppShellVM) -> None:
    """Setting settings.theme fires a message that subscribers on hub.messages observe."""
    from vmx import MessageHub  # just verify it's the right type
    assert isinstance(shell.session._hub, MessageHub)  # type: ignore[attr-defined]

    received: list[Any] = []
    shell.settings._hub.messages.subscribe(received.append)  # type: ignore[attr-defined]
    shell.settings.set_theme("dark")
    # With RxDispatcher.immediate(), subscriptions fire synchronously.
    assert len(received) >= 1


# ---------------------------------------------------------------------------
# 16. Cross-cutting: PolyglotPuzzleVM attempt subscription nudges commands
# ---------------------------------------------------------------------------

async def test_polyglot_attempt_text_nudges_generate_predicate(shell: AppShellVM, mock_backend: Any) -> None:
    """
    After load_options, generate is enabled; after generate, attempts are reset
    and attempt text changes nudge state, re-evaluating add_attempt and submit.
    """
    mock_backend.post("http://test/v1/polyglot_puzzle/generate").mock(
        return_value=httpx.Response(
            200,
            json={"src_lang_question": "Hello", "dst_lang_question": "Hola"},
        )
    )

    vm = shell._polyglot_vm  # type: ignore[attr-defined]
    vm.load_options_command.execute()
    for _ in range(4):
        await asyncio.sleep(0)

    vm.generate_command.execute()
    for _ in range(6):
        await asyncio.sleep(0)

    assert vm.state.model.has_response

    # Attempts are MIN_ATTEMPTS (2) empty strings after generate — submit not enabled.
    assert not vm.submit_command.can_execute()

    # Fill both attempts.
    vm.attempts[0].model = vm.attempts[0].model.with_text("Mi respuesta")
    vm.attempts[1].model = vm.attempts[1].model.with_text("Otra respuesta")
    # Nudge state so predicate re-evaluates (mimics what the view does on input change).
    from dataclasses import replace
    vm.state.set_model(replace(vm.state.model))

    assert vm.submit_command.can_execute()
