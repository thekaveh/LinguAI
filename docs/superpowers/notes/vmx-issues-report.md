# VMx — actionable issues found during LinguAI frontend overhaul recon

> Compiled on 2026-05-30 against `vmx==2.1.0` (editable install from `/Users/kaveh/repos/VMx/langs/python`). These are *not* tasks for the overhaul; they are findings to address in the VMx repo itself, at whatever cadence makes sense.

Each item lists: **what** (the issue), **observed in** (where I hit it during recon), **impact** (severity for downstream consumers), and a **suggested action**.

---

## A. Distribution / packaging

### A1. `vmx` is not published to PyPI despite README/getting-started docs saying it is

- **What:** `pip install vmx` fails with "No matching distribution found for vmx". The package's `pyproject.toml` is configured for publication (`hatchling` backend, full metadata), but no release has been uploaded to PyPI.
- **Observed in:** README §3.1 ("`pip install vmx`"), README §4.1 quickstart, `docs/getting-started/python.md` §1.
- **Impact:** **High.** Any external consumer reading the docs will hit a wall in the first command. The compatibility-matrix table also implies stable releases.
- **Suggested action:** Either (a) publish `2.1.0` to PyPI (and likely backfill `2.0.0` / `1.x` if you want the matrix to be honest), or (b) update README and getting-started docs to say "currently distributed via GitHub source / editable install only; PyPI publication tracked in #N" with a link to the tracking issue. Option (a) is much higher leverage if you intend external adoption.

### A2. No CI/release workflow visible for PyPI publication

- **What:** `.github/workflows/python.yml` runs tests but doesn't publish on tag. The release process appears manual.
- **Observed in:** `langs/python` repo browsing.
- **Impact:** **Medium.** Manual releases get forgotten; consumers see stale packages.
- **Suggested action:** Add a `publish-python.yml` workflow that triggers on `v*` tags, builds the sdist + wheel via hatchling, and uploads to PyPI with trusted publishing (OIDC). C# and TypeScript flavors likely need similar workflows.

### A3. Local editable install requires the host to know VMx's source path

- **What:** Consumers wanting to use a local checkout must either use Poetry's `path = "..."` dep (machine-specific paths in `pyproject.toml`) or pip-install in editable mode at runtime. Docker doesn't play nicely with either unless the consumer carefully arranges the build context.
- **Observed in:** Setting up `frontend/pyproject.toml` for the LinguAI overhaul.
- **Impact:** **Medium.** Friction for anyone integrating VMx as a dependency rather than reading/copying patterns. Largely mitigated if A1 is fixed.
- **Suggested action:** None on the VMx side beyond fixing A1. Document the "while we're pre-PyPI, use a submodule / `pip install git+https://github.com/thekaveh/VMx.git#subdirectory=langs/python`" path in README §4.1.

---

## B. Documentation / examples

### B1. Builder-first usage pattern under-emphasized in README + getting-started

- **What:** The getting-started doc *does* show `ComponentVMOf.builder()`, but the prose throughout the README talks about VMs as if they have ordinary constructors taking `name`, `services`, `model`. A reader skimming README arrives at code like `ComponentVMOf(name="x", services=(hub, dispatcher), model=M())` and finds it doesn't work (`TypeError: __init__() got unexpected keyword`). The fact that **builders are the only supported construction path** for these typed VMs should be in the second paragraph, not deep in the quickstart.
- **Observed in:** Tried writing `super().__init__(name=..., services=(...), model=...)` in a `ComponentVMOf` subclass — failed immediately.
- **Impact:** **Medium.** Onboarding consumers and LLMs reading the README will write broken code on the first attempt.
- **Suggested action:** Add a "Construction" subsection up top in the README. State plainly: "Every VM is constructed via its fluent builder (`X.builder().name(...).services(...).model(...).build()`). The base classes' `__init__` is private API and may change between minor versions." Repeat this in every flavor's quickstart.

### B2. `CompositeVMOf` doesn't have a model — but the "composite with state" pattern needs documenting

- **What:** Many real-world UIs want a composite of children that also holds its own state (e.g., a chat session: messages are children, but session-level state like persona/model/temperature is in the parent). `CompositeVMOf[ChildVM]` has no `.model`. The idiomatic VMx solution (compose: composite + aggregated `ComponentVMOf[State]`) isn't shown anywhere I could find.
- **Observed in:** Tried to design `PolyglotPuzzleVM : CompositeVMOf[AttemptVM, PolyglotPuzzleModel]` — that signature doesn't exist. Spent recon time figuring out the right composition pattern.
- **Impact:** **Medium.** This is THE common shape for UI pages with both a list and own-state; not having a recipe forces every consumer to invent it.
- **Suggested action:** Add a "Composite-with-state" recipe to `docs/getting-started/python.md` (and equivalent flavors). Show: composite holds an aggregate `ComponentVMOf[State]` for its own state, and `vm.state.model.<field>` is the path. Bonus: a `CompositeVMOfWithStateOf[ChildVM, StateModel]` helper class would let consumers skip the composition boilerplate.

### B3. RelayCommand async-task pattern is undocumented

- **What:** `RelayCommand.task: Callable[[], None]`. Real apps want commands that call async services (e.g., backend HTTP). The canonical pattern — wrap with `asyncio.create_task(_real_async())` inside a sync task body — isn't in any example I found. The Tk and Textual examples use synchronous work, so they sidestep the question.
- **Observed in:** Designing async backend calls for every page in the LinguAI overhaul.
- **Impact:** **High.** Most non-trivial apps need async; consumers will reinvent the pattern, possibly with `asyncio.run()` (wrong inside a running loop), `asyncio.run_coroutine_threadsafe` (wrong for the local loop case), etc.
- **Suggested action:** Either (a) add an `AsyncRelayCommand` / `RelayCommandAsync` whose task is `Callable[[], Awaitable[None]]` and which schedules on `RxDispatcher`'s background or foreground scheduler appropriately; or (b) document the wrapper pattern with a worked NiceGUI/FastAPI/asyncio example, including how to express `in_flight` state via the model.

### B4. `property_changed` emits names, hub emits messages — surface inconsistency

- **What:** `vm.property_changed` is `Observable[str]` (property names). `hub.messages` emits `PropertyChangedMessage` objects with `property_name` + `sender`. A consumer hooking either should know about both. The README mentions "PropertyChangedMessage" but doesn't make it obvious which surface emits which.
- **Observed in:** Wrote `vm.property_changed.subscribe(lambda msg: msg.property_name)` — crashed because `msg` is a `str`.
- **Impact:** **Low.** Easy to figure out from the error, but adds friction.
- **Suggested action:** Either rename `vm.property_changed` to `vm.property_names_changed` (more explicit) or add a `vm.property_changed_messages` returning the full-message stream for symmetry. At minimum, document the type in the README's reactivity section.

### B5. NiceGUI is named as a target host but no NiceGUI example exists

- **What:** README §1 lists "NiceGUI" as a Python target host. `examples/python/` contains a Tkinter app and a Textual TUI but no NiceGUI app. The LinguAI overhaul is precisely a NiceGUI integration; I would have built much faster from a reference example.
- **Observed in:** Looking for prior art before designing the binding patterns.
- **Impact:** **High** for consumers building NiceGUI apps.
- **Suggested action:** Add `examples/python/nicegui_todo_app/` — a small VMx + NiceGUI app showing: builder construction, RelayCommand async wrapping, composite + state pattern, and NiceGUI binding helpers (`bind_text_from(vm, "model", backward=lambda m: m.title)`, manual button `enabled` subscriber for `can_execute_changed`).

---

## C. API design observations (not bugs; worth considering)

### C1. `RelayCommand` is sync-only

- **What:** No first-class async command. Consumers wrap manually. Long-running async tasks scheduled inside a sync `task()` body have ambiguous error handling (what cancels them? when does `in_flight` clear if `create_task` task fails?).
- **Impact:** **Medium.** A first-class async command would prevent a class of bugs (forgetting to clear `in_flight`, unhandled exceptions in fire-and-forget tasks, double-fire prevention).
- **Suggested action:** Consider `AsyncRelayCommand` / `RelayCommandAsync` in v2.2. Could share most of the builder API but accept `task: Callable[[], Awaitable[None]]` and internally manage in-flight state + cancellation. See [Microsoft.Toolkit.Mvvm `AsyncRelayCommand`](https://learn.microsoft.com/en-us/dotnet/communitytoolkit/mvvm/asyncrelaycommand) for prior art.

### C2. `cmd.can_execute` is a method (callable), not a property

- **What:** Inconsistent with how UI binding systems (NiceGUI's `bind_enabled_from`, WPF's `IsEnabled` binding) typically consume command availability. Consumers writing `bind_enabled_from(cmd, "can_execute")` get the method object, not the bool.
- **Impact:** **Low.** Works once you know, but trips you up first time.
- **Suggested action:** Two options:
  1. Add a `cmd.is_executable` property that returns the current `can_execute()` value and changes alongside `can_execute_changed`. Keeps the existing method API for backward compat but adds the property for binding-friendliness.
  2. Add a thin helper `bind_button_enabled(button, cmd)` in a future `vmx.adapters.nicegui` sub-package (or document the pattern as a snippet).

### C3. `RelayCommandBuilder.triggers([obs])` accepts a list silently, crashes at build

- **What:** `.triggers(arg)` stores `arg` as a trigger. Pass a list-of-observables, you get a list stored as one "trigger". Build fails with `AttributeError: 'list' object has no attribute 'subscribe'` deep in `RelayCommand.__init__`. The intended usage is to call `.triggers(obs)` multiple times (additive), which the docstring says but is easy to miss.
- **Observed in:** Wrote `.triggers([vm.property_changed])` — crashed at build.
- **Impact:** **Low.** Easy-to-misuse API; cryptic failure mode.
- **Suggested action:** Validate the arg in `.triggers()` — if it's iterable but not an `rx.Observable`, raise a `BuilderValidationError` immediately with a hint ("did you mean to call .triggers() multiple times, once per observable?"). Cheap to add, catches the bug at the right spot.

### C4. `ConstructionStatus` naming

- **What:** Enum is `ConstructionStatus` with values that read like a *lifecycle* state machine (DISPOSED, DESTRUCTING, DESTRUCTED, CONSTRUCTING, CONSTRUCTED). README §1 calls it "the five-state construction lifecycle". Consumer mental model: "What's the lifecycle status?" → searches for `LifecycleStatus`, doesn't find it.
- **Impact:** **Very low.** Cosmetic.
- **Suggested action:** Either keep `ConstructionStatus` and update README prose to drop "lifecycle" wording, or rename to `LifecycleStatus` (with a deprecation alias) so the type matches the README's terminology.

### C5. Composite has no `on_property_value_changed("name")` helper for a single property

- **What:** To watch a single property of a single VM with the actual value, consumers must use `property_value_changed_messages_for(hub, source, name)` — verbose, requires importing from the top level, requires the hub instance. Without that helper, you'd `vm.property_changed.pipe(ops.filter(lambda n: n == "model"), ops.map(lambda _: vm.model))`.
- **Impact:** **Low.** API exists, just verbose.
- **Suggested action:** Consider adding `vm.observe_property(name) -> Observable[Any]` as a convenience method on the base class. Less coupling to the hub, no top-level import.

---

## D. Possible-bug-or-feature

### D1. NiceGUI integration story unclear (no examples + binding system mismatch)

- **What:** NiceGUI's `bind_value_from(vm, "model", backward=lambda m: m.x)` polls the source at 100ms intervals by default; it does NOT subscribe to rx observables. So VMx's reactive `property_changed` stream isn't actually driving the UI repaints — NiceGUI is just polling `vm.model` on a timer. For most things this is fine; for streaming chat tokens it adds 100ms latency per chunk.
- **Observed in:** Designing the streaming chat page.
- **Impact:** **Medium** for streaming use cases; **low** otherwise. Not really a VMx bug — it's a NiceGUI design choice. But a NiceGUI consumer who naively relies on VMx's reactivity to deliver tight UI updates will be surprised.
- **Suggested action:** When you add the NiceGUI example (B5), call this out. Show the alternative pattern: `vm.property_changed.subscribe(lambda _: ui_label.set_text(vm.model.text))` for cases where polling latency is unacceptable.

### D2. `examples/python/vmx_inspector` (Textual) is a useful pattern that should be more prominent

- **What:** Existence of `walk(root)` + a Textual TUI inspector is brilliant for debugging VM trees. Not surfaced in README §4.3 as much as it deserves.
- **Impact:** **Very low.** Marketing only.
- **Suggested action:** Mention `vmx_inspector` in README §1 or §3 alongside the bullet about tree utilities — "comes with a TUI inspector you can point at any VM tree".

---

## Summary by priority

| Priority | Item | Action |
|---|---|---|
| **High** | A1 PyPI publication | Publish, or doc that it's unpublished |
| **High** | B3 RelayCommand async pattern undocumented | Document or add `AsyncRelayCommand` |
| **High** | B5 No NiceGUI example | Add `examples/python/nicegui_*` |
| **Medium** | A2 CI release workflow | Add publish-on-tag workflow |
| **Medium** | B1 Builder-first pattern under-emphasized | Hoist into README intro |
| **Medium** | B2 Composite-with-state recipe missing | Add to getting-started |
| **Medium** | C1 First-class async command | Consider `AsyncRelayCommand` |
| **Low** | B4 property_changed surface inconsistency | Rename or add full-message stream |
| **Low** | C2 `can_execute` as property | Add `is_executable` or adapter |
| **Low** | C3 `.triggers([list])` accepts-then-crashes | Validate in builder |
| **Low** | C5 `vm.observe_property(name)` helper | Add convenience method |
| **Very low** | C4 `ConstructionStatus` naming | Cosmetic |
| **Very low** | D2 vmx_inspector visibility | Mention in README |
