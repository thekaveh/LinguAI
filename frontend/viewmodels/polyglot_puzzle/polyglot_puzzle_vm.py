from __future__ import annotations
import asyncio
from dataclasses import replace

from vmx import ComponentVMOf, RelayCommand, MessageHub, RxDispatcher

from viewmodels.polyglot_puzzle.attempt_vm import AttemptVM, build_attempt_vm
from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.domain.llm import llm_label
from models.domain.polyglot_puzzle import (
    PolyglotPuzzleModel,
    PolyglotPuzzleRequest,
)
from models.domain.embeddings import (
    EmbeddingsGetRequest,
    EmbeddingsReduceRequest,
    EmbeddingsSimilaritiesRequest,
)
from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.services.embeddings_service import EmbeddingsService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService


MIN_ATTEMPTS = 2
MAX_ATTEMPTS = 10


class PolyglotPuzzleStateVM(ComponentVMOf[PolyglotPuzzleModel]):
    """Wrapper VM around PolyglotPuzzleModel so the view can bind to .state.model.*"""

    def set_model(self, m: PolyglotPuzzleModel) -> None:
        self.model = m


class PolyglotPuzzleVM:
    """Polyglot Puzzle page VM. Plain Python class composing three VMx VMs + commands.

    Not a VMx subclass — composition over subclassing because we need both children
    (attempts) AND own state, which CompositeVMOf alone doesn't support.
    """

    route = "polyglot_puzzle"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        puzzle_svc: PolyglotPuzzleService,
        embeddings_svc: EmbeddingsService,
        language_svc: LanguageService,
        llm_svc: LLMService,
        notifications: NotificationCenterVM,
        embeddings_view: EmbeddingsViewVM,
    ) -> None:
        self._hub = hub
        self._dispatcher = dispatcher
        self._puzzle = puzzle_svc
        self._emb = embeddings_svc
        self._lang = language_svc
        self._llm = llm_svc
        self._notify = notifications
        self.embeddings = embeddings_view

        # State VM (own model)
        self.state = PolyglotPuzzleStateVM(
            name="polyglot-state",
            hint="",
            initial_model=PolyglotPuzzleModel(),
            modeled_hinter=lambda m: f"req={'set' if m.request else 'no'}",
            on_model_changed=None,
            hub=hub,
            dispatcher=dispatcher,
        )
        self.state.construct()

        # Attempts: list of AttemptVMs. Start with MIN_ATTEMPTS empty attempts.
        self.attempts: list[AttemptVM] = [
            build_attempt_vm(hub, dispatcher, name=f"attempt-{i}")
            for i in range(MIN_ATTEMPTS)
        ]
        self._subscribe_to_attempts()

        # Busy flag (separate from model so it doesn't bloat the immutable model)
        self._busy = False

        # Commands
        self.load_options_command = self._build_load_options_command()
        self.generate_command = self._build_generate_command()
        self.add_attempt_command = self._build_add_attempt_command()
        self.submit_command = self._build_submit_command()
        self.clear_command = self._build_clear_command()

    # ---------- attempt subscription ----------

    def _subscribe_to_attempts(self) -> None:
        """Subscribe to each attempt's property_changed to nudge state when text changes.

        When an attempt's model changes, we do a no-op replace on state.model
        to fire state.property_changed — causing all predicate-bearing commands
        (add_attempt, submit) to re-evaluate their can_execute().
        """
        for a in self.attempts:
            a.property_changed.subscribe(self._on_attempt_changed)

    def _on_attempt_changed(self, name: str) -> None:
        if name == "model":
            self.state.set_model(replace(self.state.model))

    # ---------- LLM / temperature setters ----------

    def set_structured_llm(self, llm_id: int) -> None:
        if self.state.model.request:
            new_req = self.state.model.request.model_copy(update={"llm_id": llm_id})
            self.state.set_model(replace(self.state.model, request=new_req))

    def set_embeddings_llm(self, llm_id: int) -> None:
        self.state.set_model(replace(self.state.model, embeddings_llm_id=llm_id))

    def set_temperature(self, t: float) -> None:
        if self.state.model.request:
            new_req = self.state.model.request.model_copy(update={"llm_temperature": t})
            self.state.set_model(replace(self.state.model, request=new_req))

    # ---------- predicates ----------

    def _can_generate(self) -> bool:
        return self.state.model.request is not None and not self._busy

    def _can_add_attempt(self) -> bool:
        return (
            self.state.model.has_response
            and MIN_ATTEMPTS <= len(self.attempts) < MAX_ATTEMPTS
            and all(a.model.text.strip() for a in self.attempts)
        )

    def _can_submit(self) -> bool:
        return (
            self.state.model.has_response
            and len(self.attempts) >= MIN_ATTEMPTS
            and all(a.model.text.strip() for a in self.attempts)
            and not self._busy
        )

    # ---------- command bodies ----------

    async def _do_load_options(self) -> None:
        try:
            languages = [L.language_name for L in await self._lang.list()]
            structured = await self._llm.get_structured_content()
            embeddings = await self._llm.get_embeddings()
            if not (languages and structured and embeddings):
                self._notify.push_error("Could not load languages or LLMs.")
                return

            structured_pairs: tuple[tuple[int, str], ...] = tuple(
                (int(getattr(L, "id", 0)), llm_label(L)) for L in structured
            )
            embeddings_pairs: tuple[tuple[int, str], ...] = tuple(
                (int(getattr(L, "id", 0)), llm_label(L)) for L in embeddings
            )

            req = PolyglotPuzzleRequest(
                src_lang=languages[0],
                dst_lang=languages[0],
                difficulty="Easy",
                llm_id=structured[0].id,
                llm_temperature=0.0,
            )
            self.state.set_model(
                replace(
                    self.state.model,
                    src_langs=tuple(languages),
                    dst_langs=tuple(languages),
                    request=req,
                    embeddings_llm_id=embeddings[0].id,
                    structured_llms=structured_pairs,
                    embeddings_llms=embeddings_pairs,
                )
            )
        except Exception as e:
            self._notify.push_error(f"Loading options failed: {e}")

    async def _do_generate(self) -> None:
        if self.state.model.request is None:
            return
        self._busy = True
        try:
            # Reset attempts to MIN_ATTEMPTS empties
            self.attempts = [
                build_attempt_vm(self._hub, self._dispatcher, name=f"attempt-{i}")
                for i in range(MIN_ATTEMPTS)
            ]
            self._subscribe_to_attempts()
            response = await self._puzzle.generate(self.state.model.request)
            self.state.set_model(self.state.model.with_response(response))
            self.embeddings.clear()
        finally:
            self._busy = False

    async def _do_submit(self) -> None:
        s = self.state.model
        if s.response is None or s.embeddings_llm_id is None:
            return
        self._busy = True
        try:
            texts: list[str] = [s.response.dst_lang_question] + [
                a.model.text for a in self.attempts
            ]
            embeds = await self._emb.get(
                EmbeddingsGetRequest(llm_id=s.embeddings_llm_id, texts=texts)
            )
            sims = await self._emb.similarities(
                EmbeddingsSimilaritiesRequest(embeddings=embeds.embeddings)
            )
            # similarities returns a flat list; first item is self-similarity (ideal vs ideal = 1.0)
            scores = list(sims.similarities)
            attempt_scores = (
                scores[1:] if len(scores) == len(self.attempts) + 1 else scores
            )
            for vm, score in zip(self.attempts, attempt_scores):
                vm.model = vm.model.with_similarity(score)
            # 2D and 3D reductions
            r2 = await self._emb.reduce(
                EmbeddingsReduceRequest(embeddings=embeds.embeddings, target_dims=2)
            )
            r3 = await self._emb.reduce(
                EmbeddingsReduceRequest(embeddings=embeds.embeddings, target_dims=3)
            )
            labels = ["ideal"] + [f"attempt {i+1}" for i in range(len(self.attempts))]
            self.embeddings.update(
                labels, r2.reduced_embeddings, r3.reduced_embeddings, attempt_scores
            )
        finally:
            self._busy = False

    # ---------- command builders ----------

    def _build_load_options_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_load_options())

        return RelayCommand.builder().task(_start).build()

    def _build_generate_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_generate())

        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(self._can_generate)
            .triggers(self.state.property_changed)
            .build()
        )

    def _build_add_attempt_command(self) -> RelayCommand:
        def _add() -> None:
            self.attempts.append(
                build_attempt_vm(
                    self._hub,
                    self._dispatcher,
                    name=f"attempt-{len(self.attempts)}",
                )
            )
            # Subscribe the new attempt so its changes also nudge state
            self.attempts[-1].property_changed.subscribe(self._on_attempt_changed)
            # Nudge state to trigger predicate re-evaluation
            self.state.set_model(replace(self.state.model))

        return (
            RelayCommand.builder()
            .task(_add)
            .predicate(self._can_add_attempt)
            .triggers(self.state.property_changed)
            .build()
        )

    def _build_submit_command(self) -> RelayCommand:
        def _start() -> None:
            asyncio.create_task(self._do_submit())

        return (
            RelayCommand.builder()
            .task(_start)
            .predicate(self._can_submit)
            .triggers(self.state.property_changed)
            .build()
        )

    def _build_clear_command(self) -> RelayCommand:
        def _clear() -> None:
            self.attempts = [
                build_attempt_vm(
                    self._hub, self._dispatcher, name=f"attempt-{i}"
                )
                for i in range(MIN_ATTEMPTS)
            ]
            self._subscribe_to_attempts()
            self.state.set_model(
                PolyglotPuzzleModel(
                    src_langs=self.state.model.src_langs,
                    dst_langs=self.state.model.dst_langs,
                    request=self.state.model.request,
                    embeddings_llm_id=self.state.model.embeddings_llm_id,
                    structured_llms=self.state.model.structured_llms,
                    embeddings_llms=self.state.model.embeddings_llms,
                )
            )
            self.embeddings.clear()

        return RelayCommand.builder().task(_clear).build()


def build_polyglot_puzzle_vm(
    hub: MessageHub,
    dispatcher: RxDispatcher,
    puzzle_svc: PolyglotPuzzleService,
    embeddings_svc: EmbeddingsService,
    language_svc: LanguageService,
    llm_svc: LLMService,
    notifications: NotificationCenterVM,
    embeddings_view: EmbeddingsViewVM,
) -> PolyglotPuzzleVM:
    return PolyglotPuzzleVM(
        hub,
        dispatcher,
        puzzle_svc,
        embeddings_svc,
        language_svc,
        llm_svc,
        notifications,
        embeddings_view,
    )
