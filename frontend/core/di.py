from __future__ import annotations
import asyncio

import httpx

from vmx import MessageHub, RxDispatcher

from core.config import AppConfig
from core.http import build_http_client

from models.services.auth_service import AuthService

from viewmodels.app_shell_vm import build_app_shell, AppShellVM
from viewmodels.shell.navigation_vm import build_navigation_vm
from viewmodels.shell.notification_center_vm import build_notification_center
from viewmodels.shell.settings_vm import build_settings_vm
from viewmodels.shell.user_session_vm import build_user_session_vm
from viewmodels.home.home_vm import build_home_vm
from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.services.embeddings_service import EmbeddingsService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService
from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import build_polyglot_puzzle_vm
from viewmodels.polyglot_puzzle.embeddings_view_vm import build_embeddings_view_vm
from models.services.user_service import UserService
from models.services.topic_service import TopicService
from viewmodels.profile.profile_vm import build_profile_vm
from viewmodels.assessment.assessment_vm import build_assessment_vm
from models.services.chat_service import ChatService
from models.services.text_to_speech_service import TextToSpeechService
from models.services.persona_service import PersonaService
from viewmodels.chat.chat_vm import build_chat_vm
from models.services.content_gen_service import ContentGenService
from models.services.rewrite_content_service import RewriteContentService
from models.services.review_writing_service import ReviewWritingService
from viewmodels.content_gen.content_gen_vm import build_content_gen_vm
from viewmodels.rewrite_content.rewrite_content_vm import build_rewrite_content_vm
from viewmodels.review_writing.review_writing_vm import build_review_writing_vm
from models.services.user_content_service import UserContentService
from models.services.ping_service import PingService
from viewmodels.admin.admin_vm import build_admin_vm


def build_process_scoped(
    cfg: AppConfig,
    loop: asyncio.AbstractEventLoop,
) -> tuple[MessageHub, RxDispatcher, httpx.AsyncClient, AuthService]:
    """Build the things that outlive any single NiceGUI client."""
    hub: MessageHub = MessageHub()
    dispatcher = RxDispatcher.asyncio(loop)
    http = build_http_client(cfg)
    auth_svc = AuthService(http)
    return hub, dispatcher, http, auth_svc


def build_shell(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    http: httpx.AsyncClient,
    auth_svc: AuthService,
) -> AppShellVM:
    """Build one AppShellVM per NiceGUI client. Process-scoped objects passed in."""
    notifications = build_notification_center(hub, dispatcher)
    settings = build_settings_vm(hub, dispatcher)
    navigation = build_navigation_vm(hub, dispatcher)
    session = build_user_session_vm(hub, dispatcher, auth_svc, http)

    user_svc = UserService(http)
    home = build_home_vm(hub, dispatcher, session, user_svc=user_svc)
    pages = [home]

    shell = build_app_shell(
        hub, dispatcher,
        session=session, settings=settings, navigation=navigation, notifications=notifications,
        pages=pages,
    )

    puzzle_svc = PolyglotPuzzleService(http)
    emb_svc = EmbeddingsService(http)
    lang_svc = LanguageService(http)
    llm_svc = LLMService(http)
    polyglot = build_polyglot_puzzle_vm(
        hub, dispatcher, puzzle_svc, emb_svc, lang_svc, llm_svc,
        notifications, build_embeddings_view_vm(hub, dispatcher),
    )
    shell._polyglot_vm = polyglot  # type: ignore[attr-defined]
    topic_svc = TopicService(http)
    profile = build_profile_vm(
        hub, dispatcher, user_svc, topic_svc, session, notifications,
        lang_svc=lang_svc, http=http,
    )
    shell._profile_vm = profile  # type: ignore[attr-defined]

    assessment = build_assessment_vm(
        hub, dispatcher, user_svc, lang_svc, session, notifications
    )
    shell._assessment_vm = assessment  # type: ignore[attr-defined]

    chat_svc = ChatService(http)
    persona_svc = PersonaService(http)
    tts_svc = TextToSpeechService(http)
    chat = build_chat_vm(hub, dispatcher, chat_svc, llm_svc, persona_svc, tts_svc, settings, notifications)
    shell._chat_vm = chat  # type: ignore[attr-defined]

    content_gen_svc = ContentGenService(http)
    rewrite_svc = RewriteContentService(http)
    review_svc = ReviewWritingService(http)
    user_content_svc = UserContentService(http)

    content_gen = build_content_gen_vm(
        hub, dispatcher, content_gen_svc, llm_svc, lang_svc, user_svc, tts_svc,
        session, notifications,
        user_content_svc=user_content_svc,
        topic_svc=topic_svc,
    )
    shell._content_gen_vm = content_gen  # type: ignore[attr-defined]

    rewrite = build_rewrite_content_vm(
        hub, dispatcher, rewrite_svc, llm_svc, tts_svc, user_svc,
        session, notifications,
        lang_svc=lang_svc,
        user_content_svc=user_content_svc,
    )
    shell._rewrite_content_vm = rewrite  # type: ignore[attr-defined]

    review = build_review_writing_vm(
        hub, dispatcher, review_svc, llm_svc, lang_svc, user_svc,
        session, notifications,
        user_content_svc=user_content_svc,
    )
    shell._review_writing_vm = review  # type: ignore[attr-defined]

    ping_svc = PingService(http)
    admin = build_admin_vm(hub, dispatcher, ping_svc, user_svc, session, notifications)
    shell._admin_vm = admin  # type: ignore[attr-defined]

    return shell
