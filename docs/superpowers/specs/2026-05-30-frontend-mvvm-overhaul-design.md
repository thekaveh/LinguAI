# Frontend MVVM Overhaul — Design Spec

**Date:** 2026-05-30
**Status:** Approved for implementation planning
**Branch:** `feature/nicegui-overhaul` (this worktree)

---

## 1. Goal

Replace the LinguAI Streamlit frontend with a NiceGUI application built strictly on MVVM, with VMx as the sole ViewModel layer. Eliminate the structural debt of the current frontend (mixed view+business logic, hand-rolled session-state singletons, ad-hoc async wrappers, kitchen-sink global services) and raise the visual bar to modern-SaaS quality. Single-developer, no external users, no need to coexist with the current Streamlit app during the migration.

## 2. Non-goals

- Backend changes beyond minor contract tweaks discovered during migration.
- Multi-tenant or production-scale concerns (sticky sessions, multi-worker uvicorn).
- Mobile-first responsive design (graceful degradation only).
- Internationalization in this round (seam preserved, strings English-only).
- Telemetry / analytics.

## 3. Key decisions (recorded)

| Decision | Choice | Rationale |
|---|---|---|
| UI framework | **NiceGUI** (FastAPI + Vue 3 + Quasar) | Only Python option where VMx is unambiguously the sole VM layer. Reflex's `rx.State` and Shiny's reactive decorators both compete with VMx; NiceGUI's binding model lets VMx VMs be the source of truth. |
| VMx consumption | **PyPI library** (`vmx = "^2.1.0"`) | Cleanest dep graph, identical dev/prod. Editable install reserved as escape valve if VMx gaps surface during migration. |
| Folder topology | **Horizontal** — top-level `models/`, `viewmodels/`, `views/` | Matches the "strict M vs VM vs V" framing; makes layer-violation PRs visually obvious. |
| Visual direction | **Dual-Mode Studio** — follows OS preference, brand orange as the constant accent across light + dark | Modern SaaS aesthetic; preserves brand identity; respects user preference. |
| Migration strategy | **Big-bang on feature branch** | Single-developer project, no external users — coexistence infrastructure (nginx, dual auth) is overkill. Worktree already set up for this. |
| Theme location | **`views/theme/`** (under views/) | Theme is purely a view-layer concern; subordinating it preserves the three-layer mental model. |

## 4. Architecture

### 4.1 Layer diagram (request flow)

```
Browser (Vue 3 + Quasar, served by NiceGUI)
        │ WebSocket
        ▼
views/             render functions; bind to VM properties, dispatch VM commands
        │
        ▼
viewmodels/        VMx primitives (ComponentVMOf, CompositeVMOf, GroupVM,
                   AggregateVMn, RelayCommand, DerivedProperty); subscribes
                   to MessageHub; no NiceGUI imports
        │
        ▼
models/            domain entities, wire DTOs, async httpx gateways to backend
        │ HTTP (httpx.AsyncClient)
        ▼
Backend (FastAPI)
```

### 4.2 ViewModel hierarchy

```
AppShellVM  : CompositeVM[PageVM]    (per-client; built inside ui.page handler)
│
├─ aggregates: UserSessionVM         (auth, current user, languages, role)
│              SettingsVM            (theme mode, default LLM, default persona)
│              NotificationCenterVM  (toast queue, error sink)
│              NavigationVM          (current_route, history, drawer_open)
│
└─ children (selected via CompositeVM.selected):
   ├─ HomeVM
   ├─ ChatVM                 : CompositeVMOf[ChatMessageVM, ChatSessionModel]
   ├─ ContentGenVM
   ├─ RewriteContentVM
   ├─ ReviewWritingVM
   ├─ PolyglotPuzzleVM       : CompositeVMOf[AttemptVM, PolyglotPuzzleModel]
   │                           + EmbeddingsViewVM (aggregate)
   ├─ ProfileVM              : CompositeVMOf[InterestVM, ProfileModel]
   │                           + AssessmentHistoryVM (aggregate)
   ├─ AssessmentVM           : CompositeVMOf[QuestionVM, AssessmentModel]
   ├─ RegisterVM             : AggregateVM3 of step VMs (wizard)
   └─ AdminVM                : GroupVM[FeatureFlagVM] (gated by UserSessionVM.is_admin)
```

Process-scoped (shared across clients): `MessageHub`, `RxDispatcher`, `httpx.AsyncClient`, all `models/services/*` instances.

Per-client (rebuilt per session): `AppShellVM` and everything underneath.

### 4.3 The four hard rules

1. **No `import nicegui` in `viewmodels/` or `models/`.** Enforced by import-linter contract. Makes VMs unit-testable headlessly and is what makes the design *strictly* MVVM rather than MVVM-flavored.
2. **No service calls in `views/`.** Views bind to VM properties and dispatch VM commands. Enforced by import-linter contract (`views/` may not import `models/services/`).
3. **Every VM is constructed via a builder/constructor and wired through `core/di.py`.** No `ClassName.instance()` singletons. No `st.session_state` equivalent.
4. **Async services are awaited in command bodies, never inside `render()`.** No `asyncio.run()`, no `*_sync()` wrappers, no new event loops. Single uvicorn asyncio loop end to end.

## 5. Folder structure

```
frontend/
├── main.py                       # NiceGUI entry: build DI, mount AppShell, ui.run()
├── pyproject.toml                # adds: nicegui, vmx, pydantic-settings, import-linter, respx
│                                 # removes: streamlit, streamlit-option-menu, streamlit-modal
├── poetry.lock
├── Dockerfile                    # CMD: python -m main
├── importlinter.toml             # layer boundary contracts
│
├── core/                         # cross-cutting plumbing
│   ├── config.py                 # AppConfig (pydantic-settings, env-driven)
│   ├── logger.py                 # setup_logging (was utils/logger_config.py)
│   ├── http.py                   # shared httpx.AsyncClient factory + auth header injection
│   └── di.py                     # composition root: builds hub, dispatcher, services, AppShellVM
│
├── models/
│   ├── domain/                   # plain Python entities — no httpx, no NiceGUI
│   │   ├── llm.py, persona.py, embeddings.py, polyglot_puzzle.py, user_skill.py
│   ├── schemas/                  # wire DTOs (was: top-level schema/)
│   │   ├── authentication.py, chat.py, content_gen.py, content.py, language.py,
│   │   │ password_change.py, prompt.py, review_writing.py, rewrite_content.py,
│   │   │ skill_level.py, text_to_speech.py, topic.py, user_assessment.py,
│   │   │ user_content.py, user_language.py, user_topic.py, user.py, list_response.py
│   └── services/                 # async httpx gateways to backend (was: top-level services/)
│       ├── auth_service.py       # split out of user_service
│       ├── chat_service.py, content_gen_service.py, content_service.py,
│       │ embeddings_service.py, language_service.py, llm_service.py,
│       │ persona_service.py, polyglot_puzzle_service.py, review_writing_service.py,
│       │ rewrite_content_service.py, skill_level_service.py, text_to_speech_service.py,
│       │ topic_service.py, user_content_service.py, user_service.py
│   # gone: state_service.py (split into VMs)
│   # gone: notification_service.py (→ NotificationCenterVM)
│
├── viewmodels/                   # VMx-based — never imports nicegui
│   ├── app_shell_vm.py           # root CompositeVM[PageVM]
│   ├── shell/
│   │   ├── user_session_vm.py, settings_vm.py, navigation_vm.py, notification_center_vm.py
│   ├── home/home_vm.py
│   ├── auth/
│   │   ├── login_vm.py
│   │   └── register_vm.py        # AggregateVM3 wizard (3 steps)
│   ├── chat/
│   │   ├── chat_vm.py            # CompositeVMOf[ChatMessageVM, ChatSessionModel]
│   │   └── chat_message_vm.py
│   ├── content_gen/content_gen_vm.py
│   ├── rewrite_content/rewrite_content_vm.py
│   ├── review_writing/review_writing_vm.py
│   ├── polyglot_puzzle/
│   │   ├── polyglot_puzzle_vm.py    # CompositeVMOf[AttemptVM, PolyglotPuzzleModel]
│   │   ├── attempt_vm.py
│   │   └── embeddings_view_vm.py    # 2D / 3D plotly data
│   ├── profile/
│   │   ├── profile_vm.py
│   │   └── interest_vm.py
│   ├── assessment/assessment_vm.py
│   └── admin/admin_vm.py
│
├── views/                        # NiceGUI render fns — never imports models/services/
│   ├── app_shell.py              # mount(): chrome (drawer + header + content slot + toasts)
│   ├── theme/
│   │   ├── tokens.py             # SPACING, RADIUS, SHADOW, MOTION constants
│   │   ├── palette.py            # ColorPalette dataclass; LIGHT + DARK; BRAND_ORANGE = "#F97316"
│   │   ├── typography.py         # Inter (UI) + JetBrains Mono (code) loader
│   │   └── components.py         # helpers: card(), pill_button(), chip(), code_block(), section_header()
│   ├── shell/
│   │   ├── header.py, sidebar.py, footer.py, login_panel.py, toast_host.py
│   ├── home/home_view.py
│   ├── auth/{login_view.py, register_view.py}
│   ├── chat/{chat_view.py, message_bubble.py}
│   ├── content_gen/content_gen_view.py
│   ├── rewrite_content/rewrite_content_view.py
│   ├── review_writing/review_writing_view.py
│   ├── polyglot_puzzle/{polyglot_puzzle_view.py, attempt_row.py, embeddings_plot.py}
│   ├── profile/{profile_view.py, interest_chip.py}
│   ├── assessment/assessment_view.py
│   └── admin/admin_view.py
│
├── static/                       # existing logos / svgs + new self-hosted fonts
└── tests/
    ├── conftest.py               # vmx fixtures: hub, immediate dispatcher, mocked services
    ├── viewmodels/               # unit tests, no NiceGUI
    └── views/                    # integration tests using NiceGUI's user fixture
```

## 6. App shell

Single-page-app. `views/app_shell.py` stays mounted; only the content slot rerenders when `NavigationVM.current_route` changes.

- **Header (sticky, blurred):** logo + breadcrumb + ⌘K jump-to + backend-status dot + bell + theme toggle + user avatar menu.
- **Left rail (collapsible Quasar `q-drawer`):** grouped nav sections (Learn / You / System), active item highlighted with brand orange icon, badge chips for counts, daily-streak callout pinned at the bottom of the rail.
- **Content slot:** renders `selected_page.view()` for the currently selected child of `AppShellVM`.
- **Toast host (fixed overlay, top-right):** subscribes to `NotificationCenterVM.children_changed`; renders Quasar notifications.

Theme mode lives on `SettingsVM.theme_mode` (`"system" | "light" | "dark"`), persisted in `app.storage.user`. When it changes, `views/app_shell.py` reapplies `ui.colors(...)`. Brand orange (`#F97316`) is identical in both modes — the visual through-line.

## 7. Per-page MVVM pattern

Every page follows the same template, exemplified by polyglot puzzle (the most complex VM in the catalog).

### 7.1 Model layer

- `models/domain/polyglot_puzzle.py` — `PolyglotPuzzleModel` dataclass holding `src_langs`, `dst_langs`, `difficulties`, `request`, `response`, `embeddings_llm`. Plain Python; no httpx, no NiceGUI.
- `models/schemas/polyglot_puzzle.py` (where applicable) — Pydantic request/response DTOs.
- `models/services/polyglot_puzzle_service.py` — `class PolyglotPuzzleService` with `async def generate(request)` etc. Takes `httpx.AsyncClient` in constructor; raises typed `BackendError` subclasses.

### 7.2 ViewModel layer

```python
class PolyglotPuzzleVM(CompositeVMOf[AttemptVM, PolyglotPuzzleModel]):
    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        puzzle_svc: PolyglotPuzzleService,
        embeddings_svc: EmbeddingsService,
        notifications: NotificationCenterVM,
        embeddings_vm: EmbeddingsViewVM,
    ) -> None:
        super().__init__(name="polyglot-puzzle", services=(hub, dispatcher))
        self._svc = puzzle_svc
        self._emb = embeddings_svc
        self._notify = notifications
        self.embeddings = embeddings_vm

        self.can_submit = DerivedProperty(
            sources=[self.children_changed, self.model_changed],
            compute=lambda: self.model.has_response
                and len(self.children) >= 2
                and all(c.model.text.strip() for c in self.children),
        )

        self.generate_command = RelayCommand(execute=self._generate, ...)
        self.submit_command   = RelayCommand(execute=self._submit,
                                             can_execute=lambda: self.can_submit.value,
                                             can_execute_trigger=self.can_submit.changed)
        self.add_attempt_command = RelayCommand(...)

    async def _generate(self) -> None:
        response = await self._svc.generate(self.model.request)
        self.model = self.model.with_response(response)

    async def _submit(self) -> None:
        texts = [self.model.response.dst_lang_question] + [c.model.text for c in self.children]
        sims  = await self._emb.similarities_for(texts, llm=self.model.embeddings_llm)
        for child, score in zip(self.children, sims):
            child.model = child.model.with_similarity(score)
        self.embeddings.update_from(sims)
```

### 7.3 View layer

```python
def render(vm: PolyglotPuzzleVM) -> None:
    with card():
        section_header("Polyglot Puzzle", subtitle="...")
        with ui.row().classes("gap-3 items-end w-full"):
            ui.select(options=vm.model.src_langs, label="Source language").bind_value(vm.model, "src_lang")
            ui.select(options=vm.model.dst_langs, label="Target language").bind_value(vm.model, "dst_lang")
            ui.select(options=vm.model.difficulties, label="Difficulty").bind_value(vm.model, "difficulty")
        pill_button("Generate puzzle", on_click=vm.generate_command.execute_async) \
            .bind_enabled_from(vm.generate_command, "can_execute")

    with card().bind_visibility_from(vm.model, "has_response"):
        ui.label().bind_text_from(vm.model.response, "src_lang_question")
        ui.label().bind_text_from(vm.model.response, "dst_lang_question")
        with ui.column().classes("gap-2 mt-4"):
            for attempt_vm in vm.children:
                render_attempt_row(attempt_vm)
        with ui.row():
            pill_button("Add attempt", on_click=vm.add_attempt_command.execute) \
                .bind_enabled_from(vm.add_attempt_command, "can_execute")
            pill_button("Submit", variant="primary", on_click=vm.submit_command.execute_async) \
                .bind_enabled_from(vm.submit_command, "can_execute")
        render_embeddings_plot(vm.embeddings)
```

### 7.4 DI wiring

```python
# core/di.py
def build_app_shell(cfg: AppConfig, loop: asyncio.AbstractEventLoop) -> AppShellVM:
    hub        = MessageHub()
    dispatcher = RxDispatcher.asyncio(loop)
    http       = build_http_client(cfg)

    auth_svc, puzzle_svc, embeddings_svc, chat_svc, ... = (
        AuthService(http), PolyglotPuzzleService(http), EmbeddingsService(http), ChatService(http), ...
    )

    notifications = NotificationCenterVM(hub, dispatcher)
    settings      = SettingsVM(hub, dispatcher)
    session       = UserSessionVM(hub, dispatcher, auth_svc, notifications)
    navigation    = NavigationVM(hub, dispatcher)

    polyglot = PolyglotPuzzleVM(hub, dispatcher, puzzle_svc, embeddings_svc,
                                notifications, EmbeddingsViewVM(hub, dispatcher))
    # …other page VMs…

    return AppShellVM(
        hub, dispatcher,
        aggregates=(session, settings, navigation, notifications),
        children=(home, chat, content_gen, rewrite, review,
                  polyglot, profile, assessment, admin),
    )
```

### 7.5 Per-page VM type map

| Page | VM type | Notable shape |
|---|---|---|
| Home | `ComponentVMOf[HomeModel]` | Read-only dashboard; derives stats from `UserSessionVM` |
| Chat | `CompositeVMOf[ChatMessageVM, ChatSessionModel]` | Children grow as messages stream; `AttachmentVM` aggregate |
| Content Gen / Rewrite / Review | `ComponentVMOf[…]` | Request + result + 1 long-running command each |
| Polyglot Puzzle | `CompositeVMOf[AttemptVM, PolyglotPuzzleModel]` | Worked example above |
| Profile | `CompositeVMOf[InterestVM, ProfileModel]` + `AssessmentHistoryVM` aggregate | Interests as children, history as aggregate |
| Register | `AggregateVM3[StepOneVM, StepTwoVM, StepThreeVM]` | Wizard with per-step validity |
| Assessment | `CompositeVMOf[QuestionVM, AssessmentModel]` | Questions as children, score as derived |
| Admin | `GroupVM[FeatureFlagVM]` | Peers without explicit selection |

## 8. Cross-cutting concerns

### 8.1 Auth & session

- `UserSessionVM` owns `is_authenticated`, `current_user`, `auth_token`. Persists token to `app.storage.user["auth_token"]`; rehydrates on startup.
- Login: `LoginVM.login_command` → `AuthService.authenticate(creds)` → on success sets session token → injects header on shared `httpx` client → publishes `UserLoggedInMessage` → `NavigationVM` routes to `HomeVM`.
- Logout: `UserSessionVM.logout_command` clears `app.storage.user`, removes auth header, publishes `UserLoggedOutMessage`. Subscribing VMs reset via VMx's `reconstruct()` lifecycle primitive — replaces the current `PolyglotPuzzleViewModel.instance().reinitialize()` hack in `sidebar.py`.
- Route guards: `AppShellVM` selects between `LoginVM` and the requested page VM based on `UserSessionVM.is_authenticated`. Admin pages additionally gate on `is_admin`.

### 8.2 Async story

One asyncio loop end to end. NiceGUI runs on uvicorn; `RxDispatcher.asyncio(loop)` hands VMx that same loop; `httpx.AsyncClient` uses it; `async def` event handlers awaited by NiceGUI use it. CPU-bound work (e.g., plotly data prep) goes to `asyncio.to_thread`.

Anti-patterns deleted: `asyncio.run(...)` inside render, `loop.run_until_complete(...)` wrappers, `*_sync()` helper functions, `ClassName.list_sync()` static methods.

### 8.3 Notifications & errors

Three tiers, three sinks:

| Kind | Surface | Mechanism |
|---|---|---|
| Field validation | Inline next to input | VM exposes `field_x_error: DerivedProperty[str]`; view binds via `bind_text_from` |
| Operation result | Toast (top-right) | VM calls `notifications.push_success(...)` / `push_error(...)` |
| Fatal / unknown | Modal with retry | Global `FatalErrorVM`; shell swaps content slot |

`NotificationCenterVM` is a `GroupVM[ToastVM]`. `views/shell/toast_host.py` subscribes to `children_changed` and renders `ui.notify(...)`. Services never call UI — they raise typed exceptions (`AuthError`, `BackendUnavailable`, `ValidationError`); the VM command body catches and routes.

Network resilience: shared `httpx.AsyncClient` with `connect=5s, read=15s` timeouts and a tiny retry (max 2) on 5xx. Sustained outage flips `UserSessionVM.backend_status` to `"offline"`; the status dot in the header turns red.

### 8.4 Testing strategy

| Layer | Test kind | Tooling |
|---|---|---|
| `models/domain` | Unit (pure) | pytest |
| `models/services` | Unit with mocked httpx | pytest + respx |
| `viewmodels/*` | Unit, headless | pytest-asyncio + `RxDispatcher.immediate()` + service mocks |
| `views/*` | Smoke (happy-path per page) | NiceGUI's `user` pytest fixture |
| Layering | Static contract | import-linter (CI + pre-commit) |

VM tests never import NiceGUI; they instantiate with mock services + immediate dispatcher, drive commands, assert on property values. Run in <100ms each, form the bulk of the suite. View tests are deliberately thin — exist to catch binding regressions, not re-test logic.

### 8.5 Layer-boundary enforcement (`importlinter.toml`)

```toml
[importlinter]
root_packages = ["frontend"]

[[importlinter.contracts]]
name = "MVVM layering"
type = "layers"
layers = ["frontend.views", "frontend.viewmodels", "frontend.models", "frontend.core"]

[[importlinter.contracts]]
name = "viewmodels are UI-free"
type = "forbidden"
source_modules = ["frontend.viewmodels"]
forbidden_modules = ["nicegui"]

[[importlinter.contracts]]
name = "models are UI-free"
type = "forbidden"
source_modules = ["frontend.models"]
forbidden_modules = ["nicegui"]

[[importlinter.contracts]]
name = "views do not call services"
type = "forbidden"
source_modules = ["frontend.views"]
forbidden_modules = ["frontend.models.services"]
```

(`views.theme` belongs to `frontend.views` and is covered by the same contracts — no separate layer entry needed.)

### 8.6 CI & pre-commit

Pre-commit hooks: ruff (lint + format), mypy `--strict` on `models/`, `viewmodels/`, `core/`, `views/theme/`, import-linter, VM unit tests. CI runs the full pytest suite + import-linter.

## 9. Migration plan

Phased on the `feature/nicegui-overhaul` branch in this worktree. Each phase ships a verifiable deliverable; phases 1 and 2 establish the patterns, phase 3 stress-tests them, phases 4–6 apply them at scale, phase 7 cleans up and cuts over.

| Phase | Scope | Gate |
|---|---|---|
| 0 — Foundation | Deps, `core/`, `views/theme/`, `viewmodels/app_shell_vm.py` + shell aggregates, `views/app_shell.py` + `views/shell/*`, Dockerfile, `importlinter.toml`, pre-commit hooks | App boots; renders shell chrome with empty content slot; theme toggle works; import-linter passes |
| 1 — Smoke | One throwaway "hello VM" page (input bound 2-way, button bound to command, async service call) | Bindings work both ways; `can_execute` drives button state; async handler doesn't block event loop |
| 2 — Auth + Home | `LoginVM/View`, `RegisterVM` wizard, `HomeVM/View` dashboard, `UserSessionVM` + cookie persistence + auth header injection | Register, log in, see dashboard, log out cleanly (lifecycle reconstruct verified) |
| 3 — Polyglot Puzzle | Hardest VM shape (composite + aggregate + derived + multiple commands + plotly); old `PolyglotPuzzleViewModel` deleted | Working puzzle with attempts list + embeddings viz |
| 4 — Profile + Assessment | Profile (interests, languages, history). Assessment (questions composite + score derived) | Profile edits persist; assessment runs end-to-end |
| 5 — Chat | `ChatVM` composite, streaming-token UI, persona switching, image upload, TTS playback (matches polish-v2 mockup) | Streaming renders smoothly; image upload + vision works; persona switch preserves history |
| 6 — Content trio | `ContentGenVM`, `RewriteContentVM`, `ReviewWritingVM` (same shape, built in parallel) | Each generates, plays TTS, displays result without UI jank |
| 7 — Admin + cutover | `AdminVM/View`. Delete `components/`, `services/state_service.py`, `services/notification_service.py`, top-level `schema/`, `.streamlit/`, `app.py`. Drop `streamlit*` from `pyproject.toml`. Final repo greps. Squash-merge to `develop`. | Clean repo, single frontend stack; full manual smoke passes; CI green |

## 10. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| VMx + NiceGUI integration gaps (no public reference example) | Medium | Phase 1 smoke page validates patterns end-to-end. Editable-install escape valve allows in-place VMx patches during migration. |
| VM lifecycle ≠ NiceGUI client lifecycle | Medium | `AppShellVM` is per-client (built inside `ui.page` handler), not a process global. Hub/dispatcher/http/services are process-scoped. |
| Streaming chat UI jank | Medium | `ChatMessageVM.text` is an accumulator; view binds once; bound label updates in place. Validate in phase 5 smoke. |
| Plotly reactivity quirks | Low | Re-emit figure object on data change rather than mutate in place. Fallback: echarts via `ui.echart`. |
| Long-lived branch drift | Medium | No Streamlit-side feature work during overhaul. Rebase feature branch onto `develop` at the end of each phase. |
| Backend contract gaps | Low | Discovered service-by-service; any backend change ships in a separate PR to `develop` first; feature branch rebases. |
| Image upload UX gap (Streamlit `st.file_uploader` vs NiceGUI `ui.upload`) | Low | Phase 5 smoke validates with single image; iterate. |
| Multi-worker deploy needs sticky sessions | Low | Not a current need (single container). Documented as future consideration. |

## 11. Open questions (parked, defaults chosen)

1. **Tour mode** — currently embedded as an intro pane in each page. **Default: drop**; reintroduce as a lightweight `ui.dialog` "What's new" later if missed.
2. **Multi-tab behavior** — `app.storage.user` shared across tabs; VMs per-client. **Assumed acceptable.**
3. **Auth token shape** — JWT vs opaque session vs cookie. **Confirm against backend during phase 2.**
4. **i18n** — VMx ships `ILocalizer`. **Default: defer**; preserve seam in VM constructors; English-only for now.
5. **Mobile / responsive** — design is desktop-first (≥1280px). **Default: graceful single column under `md` breakpoint**, no further polish.
6. **Theme default on first visit** — **Default: follow system**; persist user override.
7. **Telemetry / analytics** — **Default: none**; revisit later.
8. **Chart library** — **Default: keep Plotly** through phase 3; evaluate echarts swap based on what we hit.
9. **VMx exact type compositions** — the spec uses `CompositeVMOf[ChildVM, Model]` notationally to indicate "composite with both children and a model". Whether VMx exposes this directly or the same shape is achieved by composing `CompositeVM[VM]` with a `ComponentVMOf[M]` aggregate gets pinned during phase 0/1 against the actual library surface. **Default: prefer the most idiomatic VMx form discovered in phase 0**; spec signatures are design intent, not API contracts.

## 12. Definition of done

- All current pages have NiceGUI views + VMx viewmodels equivalents. Feature parity verified by manual smoke (register → every page → logout).
- Repo greps return empty: `import streamlit`, `asyncio.run\(` in render paths, `_sync\(` wrappers, `\.instance\(\)` singletons, `st\.session_state`.
- Deleted: `frontend/app.py`, `frontend/components/`, `frontend/services/state_service.py`, `frontend/services/notification_service.py`, top-level `frontend/schema/`, `frontend/.streamlit/`.
- `pyproject.toml` no longer lists `streamlit*`; adds `nicegui`, `vmx`, `pydantic-settings`, `import-linter`, `respx`.
- import-linter passes (4 contracts); mypy `--strict` passes on `models/`, `viewmodels/`, `core/`, `views/theme/`.
- VM unit tests cover the worked-example pages (chat, polyglot puzzle) at minimum; suite runs in <30s.
- Docker image builds; `docker compose up` serves the NiceGUI app on existing `FRONTEND_PORT`; manual smoke passes.
- Single squash-merge from `feature/nicegui-overhaul` to `develop`.
