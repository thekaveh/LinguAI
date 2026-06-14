from __future__ import annotations
import asyncio
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.assessment.question_vm import QuestionVM, Question, build_question_vm
from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.services.user_service import UserService
from models.services.language_service import LanguageService
from models.schemas.user_assessment import UserAssessmentCreate
from models.schemas.language import Language


@dataclass(frozen=True)
class AssessmentModel:
    language: str = ""
    in_flight: bool = False
    completed_score: Optional[int] = None


class AssessmentStateVM(ComponentVMOf[AssessmentModel]):
    def set_model(self, m: AssessmentModel) -> None:
        self.model = m


def _seed_questions(lang: str) -> list[Question]:
    """Placeholder question bank. Replace with /assessments/questions when backend supports it."""
    return [
        Question(
            prompt=f"Pick the greeting in {lang}.",
            options=("Adios", "Hola", "Gracias", "Por favor"),
            correct_index=1,
        ),
        Question(
            prompt=f"Which is a verb in {lang}?",
            options=("Casa", "Comer", "Libro", "Mesa"),
            correct_index=1,
        ),
        Question(
            prompt=f"Translate 'thank you' in {lang}.",
            options=("Por favor", "Buenas noches", "Gracias", "Hola"),
            correct_index=2,
        ),
    ]


class AssessmentVM:
    route = "assessment"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        user_svc: UserService,
        language_svc: LanguageService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._user_svc = user_svc
        self._lang_svc = language_svc
        self._session = session
        self._notify = notifications

        self.state = AssessmentStateVM(
            name="assessment-state",
            hint="",
            initial_model=AssessmentModel(),
            modeled_hinter=lambda m: m.language or "(no lang)",
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        self.questions: list[QuestionVM] = []

        self.load_command = self._build_load_command()
        self.submit_command = self._build_submit_command()

    @property
    def score_percent(self) -> int:
        if not self.questions:
            return 0
        correct = sum(1 for q in self.questions if q.model.is_correct)
        return round(100 * correct / len(self.questions))

    @property
    def all_answered(self) -> bool:
        return bool(self.questions) and all(q.model.is_answered for q in self.questions)

    def set_language(self, lang: str) -> None:
        if lang != self.state.model.language:
            # Rebuild questions FIRST so that any view subscribed to
            # state.property_changed sees a populated self.questions list when
            # the model change fires below. (If we set_model() first, the view
            # re-renders against the *previous* (empty/stale) self.questions.)
            self._rebuild_questions(lang)
            self.state.set_model(
                replace(self.state.model, language=lang, completed_score=None)
            )

    def _rebuild_questions(self, lang: str) -> None:
        self.questions = [
            build_question_vm(self._hub, self._dispatcher, q)
            for q in _seed_questions(lang)
        ]
        # Subscribe each question's property_changed to nudge state for command re-eval.
        for q in self.questions:
            q.property_changed.subscribe(
                lambda name: self.state.set_model(replace(self.state.model))
                if name == "model"
                else None
            )

    async def _do_load(self) -> None:
        username = self._session.model.username
        if not username:
            return
        try:
            user = await self._user_svc.get_by_username(username)
            learning = list(getattr(user, "learning_languages", None) or [])
            if learning:
                self.set_language(learning[0])
        except Exception as e:
            self._notify.push_error(f"Could not load assessment: {e}")

    async def _do_submit(self) -> None:
        username = self._session.model.username
        if not username:
            return
        score = self.score_percent
        skill_level = (
            "A1"
            if score < 30
            else "A2"
            if score < 50
            else "B1"
            if score < 70
            else "B2"
            if score < 85
            else "C1"
        )
        self.state.set_model(replace(self.state.model, in_flight=True))
        try:
            user = await self._user_svc.get_by_username(username)
            user_id = getattr(user, "user_id", None)
            if user_id is None:
                self._notify.push_error("No user_id; cannot save assessment.")
                self.state.set_model(replace(self.state.model, in_flight=False))
                return

            # Resolve language_id from the language name via LanguageService
            lang_name = self.state.model.language
            try:
                lang_obj = await self._lang_svc.get_by_name(lang_name)
                language_id = lang_obj.language_id
                language = lang_obj
            except Exception:
                # Fallback: create a minimal Language placeholder with id=0
                language_id = 0
                language = Language(language_id=0, language_name=lang_name)

            await self._user_svc.add_assessment(
                user_id,
                UserAssessmentCreate(
                    user_id=user_id,
                    language_id=language_id,
                    language=language,
                    skill_level=skill_level,
                    assessment_type="placement",
                    assessment_date=datetime.utcnow(),
                ),
            )
            self._notify.push_success(f"Score: {score}% — level {skill_level}")
            self.state.set_model(
                replace(self.state.model, in_flight=False, completed_score=score)
            )
        except Exception as e:
            self.state.set_model(replace(self.state.model, in_flight=False))
            self._notify.push_error(f"Could not save assessment: {e}")

    def _build_load_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load())

        return RelayCommand.builder().task(_start).build()

    def _build_submit_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_submit())

        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(
                lambda: self.all_answered
                and not self.state.model.in_flight
                and bool(self.state.model.language)
            )
            .triggers(self.state.property_changed)
            .build()
        )


def build_assessment_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    user_svc: UserService,
    language_svc: LanguageService,
    session: UserSessionVM,
    notifications: NotificationCenterVM,
) -> AssessmentVM:
    return AssessmentVM(hub, dispatcher, user_svc, language_svc, session, notifications)
