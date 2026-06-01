# LinguAI Frontend Overhaul Audit — Old Streamlit vs. New NiceGUI+VMx

**Date:** 2026-05-31  
**Branch:** `worktree-frontend-overhaul` (36 commits ahead of `develop`)  
**Auditor:** Claude (agent run)  
**Method:** Read old components from `develop` git history; read new tree on disk; rendered new UI via headless Chromium (Playwright) against the running compose stack (`localhost:50004`, backend `localhost:50003`).

Screenshots: `/tmp/audit-screenshots/00-login.png` … `10-admin.png`, plus drill-down captures `03b-chat-after-send.png`, `07b-polyglot-after-generate.png`, `09b-assessment-detail.png`. Not committed (they're local PNGs from a docker run); referenced inline for context.

Legend for "New status":
- ✅ Present — same or equivalent
- 🟡 Different — present but implemented differently
- ⚠️ Reduced — present but less capability than before
- ❌ Missing — not in the new version at all
- 🆕 Improved — new is materially better than old
- 🐛 Bug — present but broken at runtime

---

## Part A — Feature parity matrix

### 1. `app.py` → `main.py` + `views/app_shell.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Single Streamlit script entry | `streamlit run frontend/app.py`, runs `main()` each rerun | 🆕 Improved | NiceGUI `ui.page("/")` index + per-client `AppShellVM`; no rerun loop |
| Per-page navigation via sidebar option-menu | Streamlit `option_menu` with icons, regenerated each rerun | 🟡 Different | `views/shell/sidebar.py` renders grouped LEARN/YOU/SYSTEM sections; click drives `NavigationVM.go(route)`; only the content slot re-renders, not the chrome |
| Admin gets extra "Admin" item | `if user.user_type == "admin": components_info` includes Admin | ✅ Present | `if shell.session.model.is_admin: _section("SYSTEM", ...)` in `sidebar.py:39-40` |
| "Rewrite/Review/Content/Chat/Polyglot/Profile/Assessment" routes | All present | ✅ Present | All 9 page renderers registered in `views/app_shell.py:27-35` |
| Footer hidden on chat page | `if selected_component != chat: foot_notes.render()` | ❌ Missing | Footer always rendered now (`views/shell/footer.py`). Minor regression; the new footer is tiny so no visual conflict |
| Logger setup at entry | `setup_global_logging(...)` | ✅ Present | `core.logger.setup_logging` invoked at module import in `main.py:13` |
| Welcome banner with skill-level expander | `_welcome(user)` in header showed name + expander listing each language's skill | ⚠️ Reduced | New home view shows "Welcome back, <user>" + "0 language(s) in progress · (none yet)" placeholder; skill cards are a "connect data in phase 4" empty-state card |

### 2. `components/sidebar.py` → `views/shell/sidebar.py` + `viewmodels/auth/login_vm.py` + `views/auth/login_view.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Sidebar holds login form | Username + password inputs lived **in the sidebar** when not authenticated | 🟡 Different | New: full-content-area centered card at `views/auth/login_view.py`; sidebar is route nav only. Substantively cleaner |
| "Login" primary button | One button, posts to `UserService.authenticate` | ✅ Present | `LoginVM` + `RelayCommand` with `can_execute` predicate gating button enabled |
| Auto-login if both fields filled | `if st.button(...) or (username and password)` (questionable UX) | 🆕 Improved | Removed; explicit click required |
| Logout button | Sidebar "Logout" red button when authenticated | 🟡 Different | Moved to avatar menu in header → "Sign out" (`views/shell/header.py:50-51`). Discoverability slightly worse but matches modern app conventions |
| Greet on logout | `state_service.just_logged_out` → `NotificationService.greet(...)` toast next render | ❌ Missing | No logout greeting toast. Login still has "Welcome, <username>" success toast (`login_vm.py:54`) |
| Auth state preservation across reloads | None — Streamlit lost session on page reload | 🆕 Improved | Token + username persisted in `app.storage.user`; rehydrated on next page load (`main.py:32-35`) |
| Manual-select switch button (tour mode) | `manual_select = (last_visited + 1) % 8` to drive next-stop nav | ❌ Missing | Tour mode entirely removed (see Home section) |

### 3. `components/header.py` → `views/shell/header.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Logo image | `./static/logo5.png` 150px | 🟡 Different | Replaced with a 24x24 gradient orange/amber square + glow CSS box-shadow. No logo file is loaded |
| Username greeting | "Hi, {preferred_name or username}" with skill-level expander | ⚠️ Reduced | Greeting moved to Home view; header shows only "/{current page}" breadcrumb |
| Skill-level inline expander | "Your Current Skill Levels" expander iterated `user.learning_languages` | ❌ Missing | Replaced with "(connect data in phase 4)" placeholder on Home page |
| Theme toggle | None | 🆕 Improved | New `dark_mode` icon cycles `system → light → dark` and persists |
| Backend health indicator | None | 🆕 Improved | Green dot + "Backend" label (color is currently hard-coded green; real ping wiring lives in Admin page only) |
| User avatar | None | 🆕 Improved | First 2 letters of username in a violet pill, with sign-out menu attached |
| Drawer toggle | None | 🆕 Improved | "menu" hamburger icon toggles the sidebar |

### 4. `components/home.py` → `views/home/home_view.py` + `viewmodels/home/home_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Page-level subheader | "Personalized language learning for intermediate learners" | ❌ Missing | New Home is dashboard-shaped, not marketing-shaped |
| Hero image | `./static/different-languages.jpeg` | ❌ Missing | No hero image in new home |
| Unauthenticated marketing copy | Two-column features list + paragraph | ❌ Missing | New unauth state never reaches Home (login takes over the slot before render) — acceptable, but means the marketing surface is gone |
| Authenticated greeting | "Hi, {preferred_name} {last_name}" or "Hi, {first_name} {last_name}" | 🟡 Different | "Welcome back, {username}" — `username` only, not preferred/full name. Slight regression. HomeVM has nothing populated from UserService; `home_vm.py:48` notes "Phase 4 wires real skill data" |
| Welcome toast on first sight after login | `NotificationService.celebrate(...)` once on `just_logged_in` | ⚠️ Reduced | LoginVM pushes "Welcome, <username>" (info-toned, not celebration) |
| Skill-level expander | List of languages with skill levels | ❌ Missing | Replaced with "No skill data yet. Run an assessment to populate this dashboard." card |
| UI tour modal | Big multi-stage tour ("Take UI Tour" button, tour state walks 8 pages with intro paragraphs and "Next Stop: Chat" etc.) | ❌ Missing | Whole tour mode is removed. No equivalent onboarding in the new UI |
| Resume Tour button | After exiting once, "Resume Tour" appears | ❌ Missing | n/a |
| Form styling injection | `<style>[data-testid="stForm"]{...}</style>` | n/a | Streamlit-only |
| Greeting time-of-day | None | 🆕 Improved | "Sunday evening" computed from local time |
| Quick-action card grid | None | 🆕 Improved | 4 cards (Chat/Polyglot/Content/Rewrite) with icons, click → nav |
| "Start practice" primary CTA | None | 🆕 Improved | Pill button top-right routes to chat |
| "Recent activity" section | None | 🟡 Different | Placeholder card "(wired up in phase 4)" — currently empty |

### 5. `components/register.py` → `views/auth/register_view.py` + `viewmodels/auth/register_vm.py` + `register_steps.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Single huge form (15+ fields) | first/middle/last/preferred name, email, username, password, confirm, age, gender, discovery_method, phone, motivation, contact_preference, languages multiselect, topics multiselect, base_language | ⚠️ Reduced | New 3-step wizard: (1) username/email/password/confirm, (2) preferred/first/last name, (3) native + learning languages. Fields dropped: **middle name, age, gender, discovery method, phone, motivation, contact preference, topics multiselect** |
| Password + confirm with match validation | inline regex + match check | 🆕 Improved | `AccountStep` exposes `passwords_match`/`password_long_enough`/`is_valid` as Boolean flags; plaintext password kept off the published model (commit `0088e61`). Security win |
| Email regex validation | client-side regex check | ⚠️ Reduced | Only `"@" in email` check (`AccountStep.is_valid`); no full RFC-style regex |
| Name regex validation | `^[A-Za-z-' ]+$` for first/last/username | ❌ Missing | New version only checks `bool(first_name)` for the profile step |
| Age range 15–65 dropdown | required `selectbox(range(15,66))` | ❌ Missing | Field removed |
| Gender selectbox | required (Male/Female/Nonbinary/Prefer not to say) | ❌ Missing | Field removed |
| State of residence (50-state dict) | Hardcoded `states` dict referenced but **not actually rendered** in the old form (it's defined but unused) | n/a | Old code had the dict but never used it — net no-op |
| Topics multiselect | `fetch_topics_sync()` → multiselect | ❌ Missing | Topics chosen later via Profile page |
| Multiselect of learning languages | with `multiselect` | ✅ Present | Step 3 uses `ui.select(_LANGUAGES, multiple=True)`. Note: language list is hard-coded in the view (`register_view.py:11-14`), not fetched from `LanguageService` |
| Base-language dropdown | "Select Base Language*" with no default | ✅ Present | Step 3 single-select |
| Starter quiz after registration | After registration, walks through `starter_quizzes/{lang}_quiz.json` for each selected language and saves an `Assessment` per language | ❌ Missing | No starter quiz; users land on `/` and have to self-navigate to the Assessment page |
| `password_hash` field name (backend quirk) | Sent plaintext as `password_hash`; backend hashed | ✅ Present | Same field name; documented in `register_vm.py:84` comment |
| On success: success message, "click New User Registration" copy, return to login | rerun-based | 🟡 Different | Pushes "Account created. Please sign in." toast + `ui.navigate.to("/")` |
| **Renders without crashing** | yes | 🐛 **Bug** | **`/register` route returns HTTP 500: `AttributeError: 'AccountStep' object has no attribute 'password'`**. `views/auth/register_view.py:77,80,87,90,92,99,104` read `a.model.password`, `a.model.confirm`, `p.model.preferred_name`, `L.model.native`, etc. but commit `0088e61` removed `password` and `confirm` from `AccountStep` for security. The other fields (preferred_name, first_name, last_name, native, learning) DO exist on their respective step models so those specific lines wouldn't fail; only the two password reads crash. **Page is entirely unreachable from any browser** |

### 6. `components/chat.py` → `views/chat/chat_view.py` + `message_bubble.py` + `viewmodels/chat/chat_vm.py` + `chat_message_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Chat messages display | `st.chat_message(sender)` with markdown, images inline | 🆕 Improved | Custom bubble component: violet avatar (you), pink avatar (AI), timestamp, attachments above text, streaming cursor indicator |
| Chat input | `st.chat_input(...)` with disabled-when-no-persona-or-llm | ✅ Present | `ui.textarea` + send icon button. Disabled by `RelayCommand.can_execute` predicate |
| Multi-image attachments | `file_uploader(accept_multiple_files=True, type=["png","jpg","jpeg"])` | ⚠️ Reduced | `max_files=1` in `chat_view.py:71`. **Only single image per message in new version** |
| File-uploader disabled if LLM not vision-capable | yes | ✅ Present | `attach_btn.bind_enabled_from(... can_attach)` (`chat_view.py:75`), and ChatVM rejects attach with warning toast (`chat_vm.py:130-132`) |
| Clear Chat button | yes | ✅ Present | "Clear" pill in the card header |
| Persona dropdown | `st.selectbox` of PersonaService.get_all() | ✅ Present | Right rail "Session" card; populated lazily on first render |
| LLM dropdown | `st.selectbox` of LLMService.get_content() | ✅ Present | Same rail; with `display_name()` labels |
| Temperature slider 0–1, step 0.1 | yes | ✅ Present | Step 0.05 instead of 0.1 |
| Voiceover checkbox (TTS) | yes; triggers `TextToSpeechService.agenerate` and injects `<audio autoplay>` | ⚠️ Reduced | "TTS" switch present; on send, completes calls `tts.synthesize` and pushes "Audio ready" toast — **but no audio element is actually mounted**, so the user hears nothing. The old behavior embedded an inline auto-play `<audio>` |
| Streaming chunks rendered live | yes, via placeholder + `on_changed_fn` | ✅ Present | `assistant_vm.append_text(chunk)` + bubble label binds to `m.text + " ▎"` |
| Tour mode pane | "Welcome to the Chat Page!" etc. | ❌ Missing | All tour blocks removed |
| Persona-change toast | `NotificationService.success("Chat Persona changed to **{name}**")` | ❌ Missing | New persona select silently mutates state |
| Per-message export / copy | None | n/a | Neither version |

### 7. `components/polyglot_puzzle.py` → `views/polyglot_puzzle/*.py` + `viewmodels/polyglot_puzzle/*.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Intro paragraph + "Read more..." expander | Two-paragraph explanation of embeddings & t-SNE | ❌ Missing | New header is just "Polyglot Puzzle / Translate, then compare semantic similarity" |
| Source / target / difficulty selectors | three columns | ✅ Present | Three-flex row of selects |
| Generate Polyglot Puzzle button | primary | ✅ Present | |
| Clear button | secondary, disabled when no response | ✅ Present | `bind_button_enabled` |
| Disabled-text source-lang sentence field | `text_input(disabled=True)` | ✅ Present | Two labels in the response card (`polyglot_puzzle_view.py:69-77`) |
| Disabled-password ideal translation | `type="password"` (masked) | ⚠️ Reduced | New shows it as plain small text — **the "guess first" affordance is gone**. The old version explicitly masked it as a UX flourish |
| Multiple attempt text inputs (2–10) | dynamic list, add button until 10 | ✅ Present | `MIN_ATTEMPTS=2, MAX_ATTEMPTS=10` (`polyglot_puzzle_vm.py:28-29`) |
| Add Attempt button | disabled if response missing, < 2 attempts, > 10, or empty attempt | ✅ Present | `_can_add_attempt` |
| Submit button | disabled until all attempts non-empty | ✅ Present | `_can_submit` |
| Results table with color-coded similarity | HTML table, red→yellow→green | ❌ Missing | New only shows the 2D/3D plot — **no per-attempt sortable score table**. AttemptVM stores similarity but the view doesn't surface it tabularly |
| 2D embeddings scatter (plotly) | yes, with custom red→yellow→green colorscale + colorbar | ⚠️ Reduced | New plot is monochrome; no colorscale, no colorbar, no "0/0.5/1" ticks. Background is white-on-dark — looks broken |
| 3D embeddings scatter | yes, same colorscale | ⚠️ Reduced | New 3D plot exists via toggle but same issues |
| Caption note under each plot | "This visualization simplifies..." disclaimer | ❌ Missing | |
| 2D/3D toggle | None (both rendered) | 🆕 Improved | Single chart that toggles, less screen real estate |
| Embeddings LLM selector | sidebar `selectbox` of `LLMService.get_embeddings()` | ❌ Missing | No UI selector; first embeddings LLM auto-picked on load. Multiple-embeddings users lose choice |
| Structured-content LLM selector | sidebar `selectbox` of `LLMService.get_structured_content()` | ❌ Missing | Same — first structured LLM is auto-picked |
| Temperature slider | sidebar, 0–1, step 0.1 | ❌ Missing | No temperature control in new polyglot UI |
| Persistent VM per session | `st.session_state["polyglot_puzzle_view_model"]` | 🆕 Improved | Per-client VM lives in DI shell; CompositeVM pattern means state survives intra-session re-renders |
| On change of embeddings/structured LLM, toast | `NotificationService.success(...)` | ❌ Missing | n/a — no selectors |

### 8. `components/profile.py` → `views/profile/profile_view.py` + `viewmodels/profile/*.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Awards section (gamification) | `render_awards(user)`: "Consistent Learner", "New User", "Language Explorer", "Long Time User" | ❌ Missing | Entire awards block gone |
| Daily streak label | `Daily Streak: {user.consecutive_login_days}` | ❌ Missing | |
| Awards info expander (descriptions) | `render_awards_info()` | ❌ Missing | |
| Interest multiselect | `multiselect(topics, current_user_topics)`, auto-save on change | 🟡 Different | Interests are click-to-toggle **chips** (rendered via `views/profile/interest_chip.py`). Saves only when "Save" button is clicked, not on toggle |
| Learning languages multiselect | `multiselect(languages, current_user_languages)`, auto-save on change | ❌ Missing | New profile has no UI to edit learning languages |
| User profile edit form (expander) | `with st.form("profile_info"):` first/middle/last/preferred/base lang/gender, email, phone, contact pref, submit "Update Profile" | ⚠️ Reduced | New: only 4 fields editable (preferred_name, first_name, last_name, email). **Middle name, base_language, gender, phone, contact_preference are all gone from the edit form** |
| Change password expander | `change_password` form with current/new/confirm, calls `UserService.change_password` | ❌ Missing | No password-change UI in new profile |
| Save validation/error display | inline messages | 🟡 Different | `state.model.error` is bound to a `text-[var(--danger)]` label inline next to Save |
| Assessment history rendered? | `render_language_mastery(user)` defined but **not called** in old `render()` | 🆕 Improved | New profile renders an "Assessment history" card with language filter dropdown and date/level rows |
| Tour pane | yes | ❌ Missing | |

### 9. `components/assessment.py` → `views/assessment/assessment_view.py` + `viewmodels/assessment/*.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Language selector limited to user's learning languages | `selectbox(options=current_user_languages)` | ⚠️ Reduced | New auto-picks first learning language; **no UI dropdown to change it** (`assessment_vm.py:124-126`) |
| Start Assessment button | yes | ❌ Missing | New auto-loads questions on language selection |
| Questions from `starter_quizzes/{lang}_quiz.json` | Real JSON files per language with points-weighted answers | ❌ Missing | Replaced with hard-coded **3-question placeholder bank** of Spanish words regardless of selected language (`assessment_vm.py:31-49 _seed_questions`). E.g. with German selected, the user sees Spanish word "Hola/Adios/Gracias". **Net regression: the real quiz content from the old version was deleted in this branch** (need to check `starter_quizzes/` — old frontend deleted it too) |
| Per-question radio | yes, with `index=None` to force selection | ✅ Present | `ui.radio` per question; question VM tracks `selected_index` |
| Submit Quiz button | form-submit | ✅ Present | `pill_button("Submit")` |
| Skill-level mapping | 0–10 Beginner, 10–20 Intermediate, 20+ Advanced (Streamlit) | 🟡 Different | New uses percent-correct → CEFR (A1/A2/B1/B2/C1) (`assessment_vm.py:131-145`). Different scale; arguably more standard |
| Result display | `st.success("Your new skill level for {lang} is: {level}")` | ✅ Present | "Score: 33%" label + success toast |
| Backend save | `UserService.create_user_assessment(user_id, ...)` | ✅ Present | `_user_svc.add_assessment(user_id, UserAssessmentCreate(...))` |
| Questions actually render in browser | yes | 🐛 **Bug** | Confirmed via Playwright: page shows "Language: German" + "Submit" only, **zero question rows visible**. The `_render_questions()` call runs on `_refresh` subscription, but `_rebuild_questions(lang)` runs from `_do_load → set_language → _rebuild_questions` which mutates `self.questions` but **only nudges state through the question subscriptions, not via the initial rebuild**. The view's `_render_questions()` was called once before the questions list was populated and never re-runs. **Page is effectively unusable** |
| Tour pane (last in chain) | yes | ❌ Missing | |

### 10. `components/content_gen.py` → `views/content_gen/content_gen_view.py` + `viewmodels/content_gen/content_gen_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Welcome paragraph + instruction text | `_add_welcome` + `_add_instruction` (long text) | ❌ Missing | Just "Content reading / Generate a passage at your level" |
| Content type selection (radio) | `_render_content_types(content_types)` from `ContentService.list()` | ❌ Missing | No content-type picker; topic is just a freetext input |
| Topic checkbox grid | derived from `user.user_topics`; if none, fetched from TopicService.list(); rendered as 3-col checkbox grid | ⚠️ Reduced | Replaced with single freetext "Topic" input — user can't pick from their interests |
| Learning language radio | `_select_learning_language(user)` — restricted to user's learning langs | ⚠️ Reduced | Language dropdown lists ALL languages from `LanguageService.list()`, not just the user's learning ones |
| Skill level | Auto-inferred from last assessment of the chosen language, fallback "beginner" | 🟡 Different | User picks A1–C2 manually from a dropdown (`SKILL_LEVELS`); no auto-derivation from assessments |
| Streaming content generation | `ContentGenService.agenerate_content` with `on_changed/on_completed` callbacks | ✅ Present | `async for chunk in self._svc.stream(req): ...` |
| Voiceover (TTS) | sidebar checkbox; on completed, fetches `/text-to-speech` and embeds `<audio autoplay>` | ⚠️ Reduced | "🔊 Speak" button on result card calls `tts.synthesize` and toasts "Audio ready" — no audio element rendered |
| Generate / Clear buttons | yes | ⚠️ Reduced | Generate present; **Clear button removed** |
| Sidebar settings (LLM, temperature, TTS) | yes | 🟡 Different | LLM and temperature are now per-page (inside the form), not global sidebar. TTS toggle removed; only the per-result Speak button |
| Save generated content to backend | `UserContentService.create_user_content(...)` with 7-day expiry | ❌ Missing | New VM never persists generated content to backend |
| History expander (search previous, view, delete) | `_render_previous_delivered_contents(user)` — selectbox, preview, delete | ❌ Missing | No history surface at all in the new content-gen page |
| Error display for missing topic/lang/type | inline `st.error(err)` listing | ❌ Missing | New simply leaves the Generate button disabled via `can_execute` predicate (good — no errors needed) |
| Tour pane | yes | ❌ Missing | |

### 11. `components/rewrite_content.py` → `views/rewrite_content/rewrite_content_view.py` + `viewmodels/rewrite_content/rewrite_content_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Source textarea (height 400) | yes | ✅ Present | `ui.textarea` with `autogrow` |
| Skill level dropdown | from `SkillLevelService.list()` (CEFR levels from backend) | 🟡 Different | Hardcoded `["A1","A2","B1","B2","C1","C2"]` — no backend call |
| Target language dropdown | from `LanguageService.list()` | ⚠️ Reduced | Replaced with a **freetext input** (`rewrite_content_view.py:37`) defaulting "English" — user can type any string |
| Target style picker | None | 🆕 Improved | New "Target style" select: formal/casual/academic/humorous/concise |
| Rewrite Content button | primary | ✅ Present | Disabled until `llm_id && source_text.strip() && !in_flight` |
| Clear button | yes | ❌ Missing | |
| Validation message panel "Please Enter content..." | conditional `<div>` border-red | ❌ Missing | Replaced by disabled-button affordance |
| Streaming rewrite | yes | ✅ Present | `async for chunk in self._svc.stream(req)` |
| TTS | sidebar; auto `<audio>` on completion | ⚠️ Reduced | "🔊 Speak" button on result; toasts "Audio ready" but no audio element |
| Save to backend with 7-day expiry | yes | ❌ Missing | Not persisted |
| History expander (two-column preview, delete) | yes | ❌ Missing | No history |
| User base language + skill level fed into request | yes (auto-derived) | ⚠️ Reduced | `user_skill_level` / `user_base_language` are hardcoded "B1" / "English" in the model defaults (`rewrite_content_vm.py:26-27`); never derived from the session user |
| Tour pane | yes | ❌ Missing | |

### 12. `components/review_writing.py` → `views/review_writing/review_writing_view.py` + `viewmodels/review_writing/review_writing_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Writing textarea (height 400) | yes | ✅ Present | `autogrow` |
| Language auto-detection (`langdetect`) | yes; tells user "Text is written in : {lang}" | ❌ Missing | New requires user to pick language from a dropdown |
| Language dropdown | None | 🆕 Improved (sort of) | Now explicit; reduces magic but loses convenience |
| Current skill level + next skill level | Inferred from last assessment of detected language; auto-incremented via `_get_next_skill_level` | 🟡 Different | Two dropdowns (current/target) the user picks. Auto-bumps next-level on current change (`review_writing_vm.py:96-102`). Less smart than old |
| Strength + weakness | Pulled from last assessment row | 🟡 Different | Two optional text inputs the user fills (`review_writing_view.py:99-111`) |
| Review Writing button | disabled if no assessment | ✅ Present | Disabled until `llm_id && input_content.strip()` |
| Clear button | yes | ❌ Missing | |
| Streaming review | yes | ✅ Present | |
| Markdown feedback display | yes | ✅ Present | `whitespace-pre-wrap` label |
| TTS | sidebar; auto `<audio>` | ❌ Missing | Review-writing has no TTS button at all (other content pages do) |
| Backend save with 7-day expiry | yes | ❌ Missing | |
| History expander | yes | ❌ Missing | |
| "We do not have any assessment" guidance | yes | ❌ Missing | |
| Tour pane | yes | ❌ Missing | |

### 13. `components/admin.py` → `views/admin/admin_view.py` + `viewmodels/admin/admin_vm.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| User List title | `st.title("User List")` | ❌ Missing | Page is now "Admin / Feature flags & backend health" |
| Username/Email/User Type table | `UserService.list()` enumerated | ❌ Missing | No user list rendered |
| Delete user button (🗑️ per row) | yes, with confirmation flow | ❌ Missing | **Lost capability**; admins can no longer prune accounts from the UI. Confirmed in commit message of `69d33f9` ("admin sidebar populate") only the sidebar visibility was fixed, not actual admin functionality |
| Confirm-delete two-step | `st.session_state['confirm_delete']` workflow | ❌ Missing | n/a |
| Feature flags display | None | 🆕 Improved (cosmetic) | 4 hardcoded chips (`vision-chat · on`, `tts · on`, `polyglot-3d · on`, `streaming-chat · on`); these are **not real flags** — they're static labels in `admin_vm.py:21-26` |
| Backend ping | None | 🆕 Improved | "Ping backend" button calls `PingService.ping()` and shows last result + toast |

### 14. `components/foot_notes.py` → `views/shell/footer.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Footer "LinguAI Inc." + copyright | Two-column orange-bg fixed-bottom div | 🟡 Different | Minimal footer: "LinguAI · learning with AI" tiny label, non-fixed |
| Orange branding | `background-color: #ff6600` full-width | 🆕 Improved | Less obtrusive |

### 15. `components/interest_selection.py` → folded into `views/profile/profile_view.py` interest chips

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Standalone page | yes (registered nowhere in main but file existed) | n/a | Was effectively orphaned in old; new chip-based UI in Profile is the right home |
| Multiselect interests | yes | 🟡 Different | Click-to-toggle chips |

### 16. `.streamlit/config.toml` → `views/theme/palette.py` + `views/theme/typography.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| Orange `#ff6600` primary | yes | 🟡 Different | New brand orange is `#F97316` (Tailwind orange-500); close but different shade |
| Single theme (light) | yes | 🆕 Improved | Dual light/dark palette + theme toggle in header |
| `font = "sans serif"` | OS default | 🆕 Improved | Inter + JetBrains Mono via Google Fonts |
| Hides hamburger menu | `[deprecation] showMenu = false` | n/a | NiceGUI does its own chrome |

### 17. `services/state_service.py` → split across shell VMs + per-page VMs

Field-by-field migration of `StateService` (Streamlit session-state god object):

| Old field | New home | Status |
|---|---|---|
| `_username` / `username` | `UserSessionVM.model.username` | ✅ |
| `_user_type` | `UserSessionVM.model.user_type` | ✅ |
| `_session_user` | (full user object never re-cached in shell; pages call `user_svc.get_by_username()` lazily) | ⚠️ — slight perf regression: per-page refetch |
| `_chat_messages` | `ChatVM.messages: list[ChatMessageVM]` | ✅ |
| `_chat_file_upload_key` | n/a — file-upload key trick was Streamlit-specific | ✅ Not needed |
| `_chat_persona` | `ChatVM.state.model.persona` | ✅ |
| `_content_llm` | Per-page `state.model.llm_id` (Chat / ContentGen / Rewrite / Review have their own) | 🟡 Different — no longer a single shared LLM; each page has its own selection. Net: more flexibility, but no global "session default LLM" anymore (though `SettingsVM.default_llm_id` exists, only ChatVM honors it) |
| `_content_temperature` | Per-page `state.model.temperature` | 🟡 Same pattern |
| `_content_tts` | Per-page (Chat has a switch; ContentGen/Rewrite have a Speak button) | ⚠️ Inconsistent across pages |
| `_review_writing`, `_rewrite_content`, `_content_reading` | Per-page `state.model.result` | ✅ |
| `_tour_mode`, `_last_visited`, `_switch_button` | n/a — tour mode removed | ❌ Feature lost |
| `_vision_llm` | Derived from `ChatVM.state.model.is_vision_llm` property | ✅ |
| `_just_logged_in`, `_just_logged_out` | LoginVM pushes "Welcome, X"; **logout toast missing** | ⚠️ Half-migrated |

### 18. `services/notification_service.py` → `viewmodels/shell/notification_center_vm.py` + `views/shell/toast_host.py`

| Feature (old) | Old behavior | New status | Notes |
|---|---|---|---|
| `success`, `failure`, `info`, `warning` toasts | `st.toast(msg, icon=...)` | ✅ Present | `push_success`/`push_info`/`push_warning`/`push_error`; mapped to NiceGUI `ui.notify(type=...)` |
| `greet`, `celebrate` (special icons) | 👋 / 🎉 | ❌ Missing | New only has 4 severities, no special celebration variant |
| Sync wrappers (`asyncio.run`) | yes | n/a | Per-client async lifecycle handles it |

---

## Part B — UX/UI assessment (live render)

Captured via headless Chromium @ 1440×900 against `localhost:50004`. Screenshots in `/tmp/audit-screenshots/`.

### Global chrome

**Strengths**
- Persistent shell (header + sidebar + footer) survives navigation; no Streamlit-style full-page rerun flash.
- Sidebar grouping (LEARN / YOU / SYSTEM) gives sensible information architecture.
- Theme tokens via CSS variables; dark palette is genuinely good — modern depth, low-glare backgrounds.
- Inter typography + tight tracking + small uppercase eyebrow labels feel like a 2024-era SaaS app rather than a 2018 Streamlit demo.
- Backend status dot + theme toggle + avatar menu in header — standard SaaS conventions, the user knows where to find them.
- Single-page routing via `NavigationVM`; URL doesn't change but content area swaps cleanly.

**Problems**
- **Header is solid orange.** Full-width `#F97316` band dominates every page. The palette comments call it `bg-[var(--surface-0)]/70 backdrop-blur` but the Quasar `q-header` defaults to `primary` color which is set to brand orange by `ui.colors(primary=p.brand)`. The CSS class isn't winning. Severe visual issue — every screenshot shows it.
- The header status dot is **hard-coded green** (`bg-emerald-400`); doesn't reflect actual backend health.
- The "?" menu (top-right when logged out, replaced by "KA" avatar when logged in) doesn't have any feedback affordance — no hover state, no popover hint.
- The avatar menu (sign-out) is collapsed and only shows when the avatar is clicked — but the avatar has no visual "menu" indicator (arrow, hover state).
- Sidebar items have no active-state highlighting (the dark-on-dark gray text doesn't change to brand color when selected — only the current page is faintly bracketed by a hover background that may or may not stick).
- Footer is generic and unhelpful ("LinguAI · learning with AI"); no useful info (version, environment).

### Login page (`00-login.png`)

- Centered card, "Sign in to LinguAI", username + password with visibility-toggle, primary Sign In button, "Create an account" link.
- Clean and minimal.
- **Issue**: Sign In button is disabled until both fields have content — correct behavior — but **the disabled state is visually identical to enabled** (both show full orange background) at default Quasar styling; only `cursor: not-allowed` differentiates.

### Register page (`01-register.png`) — 🐛 **BROKEN**

- **HTTP 500: `AttributeError: 'AccountStep' object has no attribute 'password'`**
- Page is entirely unreachable. Cannot exercise the 3-step wizard at all.

### Home (`02-home.png`)

- Greeting band, quick-action card grid, placeholders for skill data + recent activity.
- "Start practice" pill button top-right — good primary CTA.
- 4 quick-action cards with brand-orange icons feel premium.
- **Issue**: Two empty-state cards ("No skill data yet" + "(wired up in phase 4)") admit unfinished work. Either populate them by phase 4 or replace with hidden sections + a "Get started" CTA.

### Chat (`03-chat.png`, `03b-chat-after-send.png`)

- Two-pane layout: conversation (flex-1) + Session card (w-72) right rail.
- Header strip shows persona + LLM + Clear button.
- Composer is a card with attach button, autogrow textarea, send button.
- **Works end-to-end**: typed message, AI bubble appears with timestamp, streaming cursor visible.
- **Issues**:
  - The AI bubble appears even when the streamed text is still empty (cursor "▎" on its own). Looks like a parsing artifact for a few seconds before tokens arrive.
  - **Multi-image attach reduced to single image** (`max_files=1`).
  - **TTS doesn't actually play audio** — just toasts "Audio ready" (so the user has no way to actually hear the TTS).
  - The "no vision" hint sits awkwardly to the right of the TTS switch with no visual separation.

### Content gen (`04-content_gen.png`)

- Single card: Language / Level / Model selects, Topic input, Temperature slider, Generate button.
- Clean, but **functionally bare**:
  - **No interests/topics integration** — just a freetext topic.
  - **No content-type selector**.
  - **No history of generated articles**.
  - **No Clear button**.
  - **TTS only as a post-hoc Speak button that doesn't play audio**.

### Rewrite (`05-rewrite_content.png`)

- Source textarea + 4 selects (style/language/level/model) + temperature + Rewrite.
- **Issue**: "Target language" is a **freetext input** (`ui.input`, not `ui.select`). The old version pulled from `LanguageService.list()`. Allows nonsense values like "Klingon" without errors.
- Same TTS-button-that-doesn't-play issue.

### Review writing (`06-review_writing.png`)

- After auto-load of the language list and LLM, the screenshot still shows only a single empty card with just "Your writing" textarea — the form below (lang/current/target/model + strength/weakness + temperature + button) is **not rendered**. Likely a missing await on `_load` — the `_refresh` subscription fires only on `state.property_changed` which hasn't yet been re-emitted by the time the screenshot was taken. The user has to navigate away and back to see the form.
- This is a soft 🐛 bug — page is technically reachable but unusable on first visit.

### Polyglot (`07-polyglot_puzzle.png`, `07b-polyglot-after-generate.png`)

- Generate puzzle, source/target/difficulty, attempts list, 2D/3D embeddings plot.
- **Issue 1**: Source/Target both default to "English"; users probably want different default langs.
- **Issue 2**: 2D/3D plot background is **white-on-dark** — Plotly default theme not honoring dark mode. Looks broken.
- **Issue 3**: After generating, the response card doesn't appear within 8 seconds — likely waiting on LLM, but no loading indicator (no spinner, no skeleton, no toast "Generating…"). User sees nothing happen.
- **Issue 4**: No embeddings-LLM selector, no structured-content-LLM selector, no temperature — old version had all 3 in sidebar.
- **Issue 5**: Old version had a color-coded results table + per-plot colorscale + caption disclaimer; new has none.

### Profile (`08-profile.png`)

- Profile card: preferred/email/first/last + Interests chips + Save.
- Assessment history card with language filter + list.
- **Strengths**: Chips visualization is much nicer than the old multiselect.
- **Issues**:
  - Cannot edit middle name, base language, gender, phone, contact preference.
  - Cannot change password.
  - Cannot edit learning languages.
  - Awards / gamification entirely gone.

### Assessment (`09-assessment.png`, `09b-assessment-detail.png`) — 🐛 **BROKEN**

- Card header "Skill assessment / Language: German / Submit".
- **No questions are rendered.** The radio inputs that should appear between the header and submit are simply absent.
- Root cause (likely): `_render_questions()` runs once before `_rebuild_questions` populates `self.questions`. The `state.property_changed` subscription that calls `_refresh` is wired AFTER the initial call. When `set_language(...)` fires (in `_do_load`), `_rebuild_questions` is called but no re-render is triggered (only individual question subscriptions are wired).
- Result: page is **non-functional**. Cannot take an assessment from the UI.

### Admin (`10-admin.png`)

- 4 chips (fake feature flags) + backend health line + Ping button.
- **Strength**: Working ping is nice for ops.
- **Issues**:
  - Feature-flag chips are decorative — there's no toggle or interaction.
  - **User list + delete capability is gone**. Was a real admin tool; now there's no way to manage users from the UI.

---

## Part C — Verdict

### Things that are definitively better

1. **Visual design**. The new chrome (dark surfaces, tight spacing, Inter typography, modular cards, branded gradient logo, theme toggle) makes the app look ~5 years more modern than the old Streamlit version (which was orange-bg footer + form-styled-as-yellow-box + emoji headers).
2. **Architecture**. MVVM with VMx eliminates the Streamlit "rerun the whole page on every input" model. Persistent state, command predicates, observable models — the codebase is now actually structured. Every new page is a self-contained VM tree with strict typing.
3. **Auth persistence**. Token + username in `app.storage.user` means refreshes don't kick the user out — Streamlit lost session on every reload.
4. **Header chrome**. Backend status dot, theme toggle, avatar menu, drawer toggle, breadcrumb — all standard-conventional and not in the old version.
5. **Home dashboard layout**. Greeting + quick-action grid is materially more useful than the old marketing-page-with-tour-button.
6. **Chip-based interests in Profile**. Visually nicer than a Streamlit multiselect.
7. **Reactive command enablement**. `RelayCommand.can_execute` + `bind_button_enabled` means buttons disable themselves correctly without "click → see error message" UX.
8. **Password plaintext security**. `AccountStep` keeps the plaintext off the published model — a real security hardening over Streamlit's session-state-everywhere pattern.

### Things that are at parity

- Chat (when it works): persona/LLM/temperature/streaming/clear/vision-attach are all there.
- Admin ping (vs. old admin which only had user delete).
- Assessment skill-level mapping (different scale but same concept).
- Polyglot's source/target/difficulty + multi-attempt flow.
- Rewrite/Review streaming.

### Things that are worse OR missing

| Category | What was lost |
|---|---|
| **🐛 Outright bugs** | **`/register` returns HTTP 500** (`AccountStep.password` AttributeError). Assessment page renders zero questions. Review-writing form barely renders on first visit. |
| **Admin** | User list + delete entirely removed. Replaced with fake feature-flag chips. |
| **Profile editing** | Middle name, base language, gender, phone, contact preference, password change, learning-languages editor — all gone. |
| **Awards/gamification** | "Consistent Learner", "New User", "Language Explorer", "Long Time User" badges + daily-streak label — gone. |
| **Content pages history** | Old saved every generation to backend with 7-day expiry and had a per-page history expander with preview + delete. **All three content pages lost this.** |
| **Tour mode** | The whole 8-page guided tour ("Take UI Tour" → modal walks user through each page) — gone with no replacement onboarding. |
| **Auto language detection** in review writing — gone; user has to pick. |
| **Smart skill-level inference** | Old Review/Rewrite/ContentGen pages auto-derived the user's level from their last assessment; new pages make the user pick A1–C2 manually. |
| **Topic interests integration** | Old ContentGen rendered checkbox grid of user's topics; new just has a freetext "Topic" input. |
| **Multi-image chat attachments** | Reduced from N to 1. |
| **TTS audio playback** | Old version embedded `<audio autoplay>`; new only toasts "Audio ready" — **no sound plays**. |
| **Polyglot embeddings-LLM and structured-LLM selectors** | Both removed; first option auto-picked. |
| **Polyglot temperature slider** | Removed. |
| **Polyglot results table + colorscale + captions** | Removed; the dark/light contrast on the plot is broken too. |
| **Starter quiz after registration** | Per-language quiz JSON walk-through after signup — gone. |
| **Logout toast** | Login still toasts "Welcome"; logout silently zeroes state. |
| **Persona-change toast** | Old toasted on every LLM/persona/temperature change ("Chat Persona changed to **X**"); new silently mutates. |
| **Registration field richness** | Lost: middle name, age, gender, discovery method, phone, motivation, contact preference, topics multiselect, email regex, name regex. |
| **Footer hidden on chat** | Always shown now (minor). |
| **Welcome-back greeting uses preferred name** | Old: "Hi, {preferred_name} {last_name}"; new: "Welcome back, {username}". |
| **Skill-level expander in header** | Iterated user's learning languages; gone. |
| **Plotly dark theming** | Embeddings plot is white-on-dark page background — looks broken. |

### Net verdict

**No — not yet manifestly better. It's "mostly better visually and architecturally, but with three runtime bugs that block core flows and roughly twenty material feature losses."** The new codebase is clearly the right long-term foundation: MVVM with VMx, dark-mode-first design, real navigation, real session persistence. But **as a user product right now**, the new version:

- can't register new users (500 error),
- can't run assessments (questions don't render),
- can't review writing on first visit (form doesn't render),
- can't manage users in admin,
- can't change a password,
- can't hear TTS audio,
- can't see embeddings results properly,
- can't see history of generated content,
- can't see awards/streaks,
- can't see preferred-name in greeting.

The right framing is: **the old version is feature-complete-but-ugly; the new version is beautiful-but-functionally-half-done**. Phases 0–7 of the overhaul plan delivered the chrome and the MVVM scaffolding spectacularly well; phases 4 and 6 left obvious wiring gaps that the gate-passes didn't catch because they tested only the green-path import surface.

A merge to `develop` today would be a regression for users. With ~3 days of focused bug-fix + 1 week of feature-restoration work, it would be a clear win.

---

## Part D — Recommendations

| # | Item | Severity | Recommendation |
|---|---|---|---|
| 1 | `/register` 500 — `AccountStep.password`/`.confirm` AttributeError | 🐛 | **Block merge.** Trivial fix in `views/auth/register_view.py:77,80`: drop the `value=` reads (they're not needed since plaintext is owned by the VM, not the model), or read from `a._password` / `a._confirm` directly. |
| 2 | Assessment renders no questions | 🐛 | **Block merge.** In `AssessmentVM._rebuild_questions`, after assigning `self.questions`, nudge state via `self.state.set_model(replace(self.state.model))` so the view's `_refresh` re-runs `_render_questions()`. |
| 3 | Review-writing form half-renders on first visit | 🐛 | **Block merge.** Same root cause: the initial `_refresh("model")` call in `review_writing_view.py:90` runs before `_load` completes; subscribe BEFORE the initial call OR have `_do_load` always end with a no-op `replace(...)` to force `property_changed`. |
| 4 | Polyglot plot has white background in dark mode | 🐛 | **Fix soon.** Set `layout.template="plotly_dark"` (or `paper_bgcolor` + `plot_bgcolor` to `var(--surface-1)` equivalent) in `views/polyglot_puzzle/embeddings_plot.py:_figure_for`. |
| 5 | Header bar is full-bleed orange instead of `var(--surface-0)/70` | 🐛 | **Fix soon.** `ui.colors(primary=p.brand)` sets the Quasar primary which overrides the q-header background. Either set `q-header` color explicitly via props (`color="dark"`) or move `ui.colors(primary=...)` only to elements that need it. |
| 6 | Header backend dot is hardcoded green | 🐛 | **Fix soon.** Bind to `shell.session.model.backend_status`; on logout it's "unknown", on login set it from a real ping. |
| 7 | TTS doesn't actually play audio in Chat/ContentGen/Rewrite | ⚠️ | **Fix soon.** `TextToSpeechService.synthesize` returns audio data; mount via `ui.audio(data_url, autoplay=True)` to actually play it. Currently no user hears anything despite the "Audio ready" toast. |
| 8 | Admin lost the user list + delete | ⚠️ | **Fix soon.** Re-add a `ui.table` with username/email/user_type + a destructive "Delete" action with confirmation dialog. The data path (`UserService.list()` + `delete_user`) already exists. |
| 9 | Profile lost middle name, base language, gender, phone, contact pref, password change, learning-languages | ⚠️ | **Fix soon.** Either restore the form fields or document them as intentionally cut (the registration form was also pruned, so this is somewhat consistent). Password change in particular is a basic SaaS expectation. |
| 10 | ContentGen / Rewrite / Review lost history persistence | ⚠️ | **Fix soon.** Either restore `UserContentService` writes + a history surface, or formally deprecate the history feature and remove `user_content` from backend too. |
| 11 | Rewrite "Target language" is freetext | ⚠️ | **Fix soon.** Change to `ui.select` populated from `LanguageService.list()` like ContentGen does. |
| 12 | Old auto-derivation of user's skill level + base language in Rewrite/Review | ⚠️ | **Fix soon.** Pull from `session.model.username` → `UserService.get_by_username` → most-recent assessment. Currently hardcoded "B1" / "English". |
| 13 | Polyglot lost embeddings-LLM, structured-LLM, temperature selectors | ⚠️ | Accept loss or **fix soon**. If kept, add a collapsible "Advanced" section to the puzzle card. |
| 14 | Polyglot lost the results table + colorscale + disclaimer | ⚠️ | **Fix soon.** The semantic-similarity number is the actual *answer* to the puzzle; only showing it as a scatter plot is a regression. |
| 15 | Chat reduced to single-image attach | ⚠️ | **Fix soon.** Set `max_files=N` (e.g., 4) in the upload widget and accumulate b64 strings into a tuple in ChatSession. |
| 16 | Tour mode removed | ⚠️ | **Accept loss** OR **fix soon** by adding a `?tour=1` query-param + a single "Take the tour" link on Home — the old tour was clunky but provided an onboarding ramp. |
| 17 | Awards / gamification removed | ⚠️ | **Accept loss** OR **fix soon**. The old awards were string-based and trivial; backend still has `consecutive_login_days` so a single "Daily streak" badge could be reinstated easily. |
| 18 | Logout toast removed | ⚠️ | **Fix soon.** One-line: in `header._logout`, push an info toast "Signed out — see you soon!" before clearing storage. |
| 19 | Persona/LLM/temperature change toasts removed | ⚠️ | **Accept loss.** The old toasts were noisy. |
| 20 | Welcome-back greeting uses username instead of preferred name | ⚠️ | **Fix soon.** Load user profile on login (the `_do_login → enrich user_type` block already calls `get_by_username`); store preferred_name on session and bind home greeting to it. |
| 21 | Auto-language-detect on Review Writing | ⚠️ | **Accept loss** OR add `langdetect` and re-derive — minor convenience, the dropdown is fine. |
| 22 | Content-gen lost interests integration + content-type selector | ⚠️ | **Fix soon.** Pull `user.user_topics` and render as suggestion chips above the freetext Topic input; restore content-type radio (or drop the concept if backend permits). |
| 23 | Registration field richness lost | ⚠️ | **Accept loss.** Modern SaaS conventions are lean signup forms; backend tolerates the optional fields being null. Don't undo this. |
| 24 | Starter quiz post-registration | ⚠️ | **Accept loss.** Replace with a "Take your first assessment" CTA on Home for users with zero assessments. |
| 25 | Sidebar items have no active-state highlighting | ⚠️ | **Fix soon.** Bind each row's bg/text color to `shell.navigation.model.current == route`. |
| 26 | `/ping` smoke route returns 404 | ⚠️ | **Accept loss** OR remove from docs. It was added in commit `51987cb` for early-phase debugging; production doesn't need it. |
| 27 | Home placeholder cards ("connect data in phase 4") | ⚠️ | **Fix soon** — either complete the wiring or hide the cards. Shipping with explicit "phase 4" cruft on the marquee page is a bad first impression. |

### Suggested merge order

1. **Pre-merge mandatory (block):** fix items 1, 2, 3, plus visual smoke-test in CI.
2. **Day-of-merge (fix soon, batch into a follow-up PR within a day):** items 4, 5, 6, 7, 18, 25, 27 — these are all small, high-impact UI fixes.
3. **Within the first sprint after merge (fix soon):** items 8, 9, 10, 11, 12, 14, 15, 20, 22 — these are functionality restorations.
4. **Backlog / accept-loss:** items 13, 16, 17, 19, 21, 23, 24, 26 — judgment calls; document as intentional cuts.
