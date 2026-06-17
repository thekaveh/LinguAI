# VMx Python API Quickref

> Reconnaissance for the frontend MVVM overhaul. Verified against `vmx==2.1.0` (historical: installed editable from `external/vmx/langs/python`, commit `e2b23f8`) on 2026-05-30. VMx is now consumed as `vmx = "^2.6.0"` from PyPI; the import surface is unchanged. **Treat this file — not the spec pseudo-code — as ground truth for VMx APIs.**

## TL;DR for the implementer

The spec/plan uses informal pseudo-code like `super().__init__(name=..., services=(hub, dispatcher), model=...)`. **Don't write VMs that way.** Every VMx VM is built via its immutable **fluent builder** and frozen with `.build()`. Most spec snippets need a small translation pass.

## 0. Critical caveats vs. the spec/plan

| Spec/plan said | Reality |
|---|---|
| `vmx = "^2.1.0"` on PyPI | VMx now ships on PyPI. `frontend/pyproject.toml` pins `vmx = "^2.6.0"`; Poetry resolves it normally — no submodule, no path dep. (This quickref's API notes were verified against 2.1.0; the import surface is unchanged through 2.6.0.) |
| `super().__init__(name=..., services=(hub, dispatcher), model=...)` in a VM subclass | Build via `ComponentVMOf.builder().name(...).services(hub, disp).model(...).build()`. **Do NOT subclass to override `__init__` for the basic VMs** — wire them up in `core/di.py` (or a builder helper) using the fluent builder. |
| `CompositeVMOf[ChildVM, ModelType]` (composite with both children AND a model) | **Doesn't exist.** `CompositeVMOf` only has children + `current`. For "composite with a model", compose: hold a separate `ComponentVMOf[Model]` as an aggregate attribute on the composite. |
| `RelayCommand(execute=..., can_execute=..., can_execute_trigger=...)` | `RelayCommand.builder().task(callable).predicate(callable).triggers(observable).triggers(another_observable).build()`. Triggers are added one observable at a time (NOT a list). |
| `cmd.execute_async(...)` | No async-aware execute. `task` is `Callable[[], None]`. For async work, wrap: `def task(): asyncio.create_task(_real_async())`. |
| `cmd.can_execute` as a property | It's a **method**: call `cmd.can_execute()` to get the bool. Bind via `cmd.can_execute_changed` observable. |
| `vm.model_changed` | `vm.property_changed` (Observable[str] of property names). For value-typed observation use `vmx.property_value_changed_messages_for(hub, vm, "model")` or `vmx.from_sources(...)`. |
| `composite.add_child(vm)` / `composite.remove_child(vm)` | `composite.append(vm)` (or `.add(vm)` / `.insert(i, vm)`). Remove: `composite.remove(vm)` / `.remove_at(i)` / `.clear()`. |
| `composite.selected` | `composite.current` (the child VM) or `composite.current_child`. |
| `AggregateVM3.first/.second/.third` | `aggregate.component_1` / `.component_2` / `.component_3`. |
| `notifications.children_changed.subscribe(...)` | `notifications.on_collection_changed.subscribe(...)` (it's `on_collection_changed`, not `children_changed`). |
| `LifecycleStatus.DESTRUCTED → CONSTRUCTING → CONSTRUCTED → ...` | Enum is `ConstructionStatus` (not `LifecycleStatus`). Values: `DISPOSED=0, DESTRUCTING=1, DESTRUCTED=2, CONSTRUCTING=3, CONSTRUCTED=4`. After `.build()`, status is `DESTRUCTED` (2). Call `vm.construct()` to reach `CONSTRUCTED` (4). |

## 1. Installing VMx (PyPI + Poetry)

VMx is a published PyPI package — there is no submodule. In `frontend/pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.10"
vmx = "^2.6.0"
```

Poetry resolves it from PyPI on `poetry install`; the lock file (`frontend/poetry.lock`) pins the exact resolved version and hashes.

## 2. Imports cheat sheet

```python
# Most common top-level exports — flat-import via `from vmx import ...`
from vmx import (
    # VMs (typed and untyped variants)
    ComponentVM, ComponentVMOf,
    CompositeVM, CompositeVMOf,
    GroupVM,
    AggregateVM1, AggregateVM2, AggregateVM3, AggregateVM4, AggregateVM5,
    # Builders (rarely needed by name; use `ClassName.builder()`)
    ComponentVMOfBuilder, CompositeVMOfBuilder, GroupVMBuilder, AggregateVM3Builder, RelayCommandBuilder,
    # Commands
    RelayCommand, RelayCommandOf,
    CompositeCommand, DecoratorCommand, ConfirmationDecoratorCommand,
    # Services
    MessageHub, RxDispatcher,
    NullMessageHub, NullDispatcher, NULL_MESSAGE_HUB, NULL_DISPATCHER,
    # Messages
    PropertyChangedMessage, ConstructionStatusChangedMessage,
    CollectionChangedMessage, TreeStructureChangedMessage,
    # Lifecycle
    ConstructionStatus,
    # Derived properties (helpers)
    DerivedProperty,
    from_sources, property_value_changed_messages_for,
    # Tree walks
    walk, walk_expanded, find,
    # Forwarding decorators
    ForwardingComponentVM, ForwardingCompositeVM,
)
```

## 3. ComponentVMOf — leaf VM with a typed model

**Build via builder. Don't subclass to override `__init__`.**

```python
from dataclasses import dataclass, replace
from vmx import ComponentVMOf, MessageHub, RxDispatcher

@dataclass(frozen=True)
class CounterModel:
    value: int = 0

hub = MessageHub()
dispatcher = RxDispatcher.immediate()

vm: ComponentVMOf[CounterModel] = (
    ComponentVMOf.builder()
    .name("counter")                              # required
    .services(hub, dispatcher)                    # required
    .model(CounterModel())                        # required for ComponentVMOf
    .modeled_hinter(lambda m: f"value={m.value}") # optional: display hint
    .on_model_changed(lambda m: print("changed:", m))  # optional
    .on_construct(lambda: print("constructed"))   # optional
    .on_destruct(lambda: print("destructed"))    # optional
    .build()
)

vm.construct()                # transition DESTRUCTED → CONSTRUCTING → CONSTRUCTED
print(vm.status)              # ConstructionStatus.CONSTRUCTED (4)
vm.model = CounterModel(5)    # mutate (the model is immutable, but the VM's slot is)
```

### When you NEED a subclass with extra behavior

⚠️ **Discovered Phase 0 Task 0.7:** `ComponentVMOf.builder()`, `CompositeVM.builder()`, etc. are `@staticmethod` and always return an instance of the BASE class — NOT the subclass. If `SettingsVM.builder().build()` is called, it returns a `ComponentVMOf` lacking `set_theme()`. Furthermore, `GroupVM` has no `.builder()` at all (only `GroupVMBuilder()` exists, instantiated directly).

**The correct pattern for subclasses with behavior:** construct via `__init__` directly with the full kwarg set.

`ComponentVMOf.__init__` signature (positional/kwarg):
```python
ComponentVMOf(
    name: str,
    hint: str = "",
    initial_model: M = ...,
    modeled_hinter: Callable[[M], str] = lambda m: "",
    on_model_changed: Callable[[M], None] | None = None,
    hub: MessageHub,
    dispatcher: RxDispatcher,
)
```

(Exact kwargs may vary slightly per VMx version; introspect with `inspect.signature(ComponentVMOf.__init__)` before relying on defaults.)

Example — a real `SettingsVM` from the LinguAI overhaul:
```python
class SettingsVM(ComponentVMOf[Settings]):
    """Subclass for behavior; construct via __init__ (builder won't return subclass type)."""
    def set_theme(self, mode: ThemeMode) -> None:
        self.model = replace(self.model, theme_mode=mode)


def build_settings_vm(hub: MessageHub, dispatcher: RxDispatcher) -> SettingsVM:
    vm = SettingsVM(
        name="settings",
        hint="",
        initial_model=Settings(),
        modeled_hinter=lambda m: m.theme_mode,
        on_model_changed=None,
        hub=hub,
        dispatcher=dispatcher,
    )
    vm.construct()
    return vm
```

`GroupVM` subclasses follow the same pattern. `CompositeVM` and `CompositeVMOf` subclasses likewise — `.append(child)` is used to add children post-`__init__`.

**The builder pattern is still useful** for ad-hoc one-off VMs that don't need behavior methods (e.g., test fixtures, throwaway VMs). For named subclass types — which is most production code — use `__init__` directly.

## 4. CompositeVMOf — composite of typed children

```python
from vmx import CompositeVMOf, ComponentVMOf
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    name: str = ""

class ItemVM(ComponentVMOf[Item]):
    pass

container = (
    CompositeVMOf.builder()
    .name("items")
    .services(hub, dispatcher)
    .children_models([Item("a"), Item("b")])    # initial children's models
    .child_model_to_child_view_model(            # factory: model → child VM
        lambda m: ItemVM.builder().name(f"item-{m.name}").services(hub, dispatcher).model(m).build()
    )
    .auto_construct_on_add(True)                 # optional: construct children automatically
    .async_selection(False)                      # optional: synchronous select_child by default
    .build()
)
container.construct()
print(container.count)                # 2
for child in container:               # iterable
    print(child.name)
container.append(ItemVM.builder().name("item-c").services(hub, dispatcher).model(Item("c")).build())
container.remove(container[0])
container.select_child(container[0])  # set current
print(container.current.name)
```

### "Composite with a model" — compose, don't extend

There is no `CompositeVMOf[ChildVM, Model]`. To get the spec's "PolyglotPuzzleVM has children AND a model" shape:

```python
class PolyglotPuzzleVM(CompositeVMOf[AttemptVM]):
    """Composite of AttemptVMs. The puzzle's own state lives in a sibling
    ComponentVMOf[PolyglotPuzzleModel] held as `self.state`."""
    route = "polyglot_puzzle"

def build_polyglot_vm(hub, dispatcher, ...) -> PolyglotPuzzleVM:
    state = (ComponentVMOf.builder()
             .name("polyglot-state").services(hub, dispatcher)
             .model(PolyglotPuzzleModel()).build())
    state.construct()

    vm = (PolyglotPuzzleVM.builder()
          .name("polyglot-puzzle").services(hub, dispatcher)
          .children_models([Attempt(), Attempt()])
          .child_model_to_child_view_model(
              lambda m: AttemptVM.builder().name("attempt").services(hub, dispatcher).model(m).build())
          .auto_construct_on_add(True)
          .build())
    vm.construct()
    vm.state = state  # attach aggregate

    # Wire commands here (see § 6).
    return vm
```

Bind views to `vm.state.model.<field>` for the puzzle state and to `vm.children` for the attempts. Subscribe to `vm.state.property_changed` for state changes; `vm.on_collection_changed` for child adds/removes.

## 5. GroupVM, AggregateVMn

- **`GroupVM[VM]`** — collection of peer VMs (no selection semantics tied to "current"). Use for the notification center (toasts) and admin feature flags.
- **`AggregateVM3[VM1, VM2, VM3]`** — fixed-arity wrapper around three VMs accessed as `.component_1`, `.component_2`, `.component_3`. Use for the register wizard (account/profile/languages step VMs). Builder API:

```python
from vmx import AggregateVM3

wizard = (AggregateVM3.builder()
          .name("register").services(hub, dispatcher)
          .component_1(account_step_vm)
          .component_2(profile_step_vm)
          .component_3(languages_step_vm)
          .build())
wizard.construct()
print(wizard.component_1.model.username)
```

## 6. RelayCommand — wiring sync work + async work + predicates

**RelayCommand is synchronous.** For async service calls, wrap the task to schedule on the event loop. NiceGUI is already running an asyncio loop in production; in tests use `pytest-asyncio` and `await asyncio.gather(asyncio.create_task(...))` or use `RxDispatcher.immediate()` with carefully-scoped synchronous code.

### 6a. Sync command

```python
from vmx import RelayCommand

def increment() -> None:
    vm.model = replace(vm.model, value=vm.model.value + 1)

cmd = (RelayCommand.builder()
       .task(increment)
       .predicate(lambda: vm.model.value < 100)   # optional; default = always True
       .triggers(vm.property_changed)              # add one observable per call (additive)
       .build())

cmd.execute()           # runs `task`; safe to call even when predicate is False (it just no-ops)
cmd.can_execute()       # method, returns bool
sub = cmd.can_execute_changed.subscribe(lambda _: print("can_exec changed:", cmd.can_execute()))
```

### 6b. Async command (the most common pattern in NiceGUI)

```python
import asyncio
from vmx import RelayCommand

async def _do_real_work() -> None:
    response = await some_service.fetch(...)
    vm.model = replace(vm.model, response=response, in_flight=False)

def _start() -> None:
    # fire-and-forget: schedule on the running asyncio loop.
    vm.model = replace(vm.model, in_flight=True)
    asyncio.create_task(_do_real_work())

cmd = (RelayCommand.builder()
       .task(_start)
       .predicate(lambda: not vm.model.in_flight)
       .triggers(vm.property_changed)
       .build())
```

**Bind to NiceGUI:** `ui.button("Go", on_click=cmd.execute)` works because `cmd.execute()` is a sync 0-arg call. For the enabled binding, subscribe to `cmd.can_execute_changed` and update `button.set_enabled(cmd.can_execute())` manually — there's no direct `bind_enabled_from(cmd, ...)` because `can_execute` isn't a property.

### 6c. Re-evaluating `can_execute` on model changes

`RelayCommand` recomputes its `can_execute` value only when one of its **triggers** fires. To re-evaluate on every property change:

```python
cmd = (RelayCommand.builder()
       .task(...)
       .predicate(lambda: vm.model.is_valid)
       .triggers(vm.property_changed)        # any property change re-evaluates
       .build())
```

For multi-source predicates (e.g., re-evaluate on both `state.property_changed` and `composite.on_collection_changed`):

```python
cmd = (RelayCommand.builder()
       .task(...)
       .predicate(lambda: ...)
       .triggers(state.property_changed)
       .triggers(composite.on_collection_changed)   # additive; call .triggers() again
       .build())
```

## 7. MessageHub + property observation

`MessageHub` is a sink for all message traffic:

```python
hub = MessageHub()
hub.messages.subscribe(lambda msg: print(type(msg).__name__, msg))
hub.send(PropertyChangedMessage(sender=some_obj, property_name="x"))
```

VMs publish `PropertyChangedMessage` to the hub automatically when their model or other watched property changes. `ConstructionStatusChangedMessage` fires on lifecycle transitions. `CollectionChangedMessage` fires from composite/group child mutations.

### Observe just one property of one VM

```python
from vmx import property_value_changed_messages_for

# Each subscription emits the *current* value of `model` when it changes.
model_stream = property_value_changed_messages_for(hub, vm, "model")
sub = model_stream.subscribe(lambda current_model: print("model is now:", current_model))
```

### Build a DerivedProperty from multiple sources

```python
from vmx import from_sources, property_value_changed_messages_for

is_valid_prop = from_sources(
    property_value_changed_messages_for(hub, account_vm, "model"),
    property_value_changed_messages_for(hub, profile_vm, "model"),
    transform=lambda account_model, profile_model: account_model.is_valid and profile_model.is_valid,
)

print(is_valid_prop.value)  # cold-evaluated by reading sources on first read
sub = is_valid_prop.value_changed.subscribe(lambda v: print("validity:", v))
```

DerivedProperty's `value` is read on demand; `value_changed` is an observable for reactive consumers.

## 8. Lifecycle

```python
vm = ComponentVMOf.builder()....build()    # status = DESTRUCTED (2)
vm.construct()                              # status → CONSTRUCTING (3) → CONSTRUCTED (4); fires on_construct
vm.destruct()                               # CONSTRUCTED → DESTRUCTING (1) → DESTRUCTED (2); fires on_destruct
vm.reconstruct()                            # equivalent to destruct + construct; cleaner for "reset"
vm.dispose()                                # terminal: status = DISPOSED (0); subscriptions released
```

`vm.is_constructed` is a convenience boolean.

For composites, `construct()` is depth-first — children construct first.

To "reset everything on logout", call `app_shell.reconstruct()` from the shell's logout handler. All child VMs are recursively destructed and re-constructed.

## 9. Mapping spec/plan idioms to real VMx

| Spec/plan code | Translate to |
|---|---|
| `class X(ComponentVMOf[M]):` with custom `__init__` taking services | Subclass for type-marker only; build via `X.builder().name(...).services(...).model(...).build()` in a factory; attach extra deps after build. |
| `super().__init__(name=..., services=(hub, dispatcher), model=M())` | Use the builder. |
| `vm.add_child(child)` | `vm.append(child)` |
| `vm.remove_child(child)` | `vm.remove(child)` |
| `vm.children` (iterable) | `vm` is iterable directly: `for c in vm: ...`. Or `[c for c in vm]`. Or `vm[i]` indexed access. `vm.count` for length. |
| `vm.children_changed.subscribe(...)` | `vm.on_collection_changed.subscribe(...)` |
| `vm.selected` / `composite.selected` | `composite.current` (the selected child VM) |
| `composite.select(target)` | `composite.select_child(target)` (or `select_component(target)`) |
| `vm.model_changed.subscribe(...)` | `vm.property_changed.subscribe(lambda name: ... if name == "model" else ...)` OR build a `DerivedProperty` via `property_value_changed_messages_for(hub, vm, "model")`. |
| `RelayCommand(execute=fn, can_execute=pred, can_execute_trigger=obs)` | `RelayCommand.builder().task(fn).predicate(pred).triggers(obs).build()` |
| `cmd.execute_async()` | `cmd.execute()` (the `task` does the async scheduling internally) |
| `cmd.can_execute` (property) | `cmd.can_execute()` (method call) |
| `DerivedProperty(sources=[...], compute=lambda: ...)` | `from_sources(*source_observables, transform=lambda a, b, ...: result)` |
| `AggregateVM3[A, B, C](first=a, second=b, third=c)` with `.first/.second/.third` | `AggregateVM3.builder().name(...).services(...).component_1(a).component_2(b).component_3(c).build()`; access via `.component_1` etc. |
| `LifecycleStatus.CONSTRUCTED` | `ConstructionStatus.CONSTRUCTED` |
| `vm.reinitialize()` | `vm.reconstruct()` (equivalent semantically; uses the lifecycle state machine). |

## 10. View-side binding shortcuts (NiceGUI specifics)

NiceGUI's `bind_value_from` / `bind_text_from` / `bind_enabled_from` take an object + property name + optional `backward` transform. Our VMs expose `model` (a frozen dataclass) — bind to the VM and pick the model field in the transform:

```python
ui.label().bind_text_from(vm, "model", backward=lambda m: m.title)
```

This works because `vm.model` is a Python property whose value changes whenever the VM assigns a new model. NiceGUI's binding system polls (every 100ms by default) for value changes; **it does NOT subscribe to the rx observable.** For tight update loops (streaming chat tokens), this may show 100ms latency — acceptable for streamed text, possibly noticeable for high-rate updates. Use `ui.timer(0.05, ...)` or manual `label.text = ...` updates inside an `vm.property_changed.subscribe(...)` callback if jank surfaces.

For commands: subscribe to `cmd.can_execute_changed` and update the button manually:

```python
btn = ui.button("Go", on_click=cmd.execute)

def _refresh_enabled(_=None) -> None:
    btn.set_enabled(cmd.can_execute())

cmd.can_execute_changed.subscribe(_refresh_enabled)
_refresh_enabled()
```

A small helper in `views/theme/components.py` would centralize this:

```python
def bind_button_enabled(btn, cmd) -> None:
    def _refresh(_=None) -> None: btn.set_enabled(cmd.can_execute())
    cmd.can_execute_changed.subscribe(_refresh)
    _refresh()
```

Use everywhere we'd otherwise have written `btn.bind_enabled_from(cmd, "can_execute")`.

## 11. Dockerfile + docker-compose (historical)

> **Superseded.** VMx is now a PyPI dependency, so none of the submodule
> plumbing below is needed. The frontend image installs `vmx` from PyPI via
> `poetry install`; no source copy or bind mount is required, and a fresh
> clone needs no submodule initialisation step. This section is retained only as a
> historical record of the pre-2.6.0 setup.

## 12. Working example: minimal VM + Command end-to-end

```python
from dataclasses import dataclass, replace
import asyncio

from vmx import (
    ComponentVMOf, RelayCommand, MessageHub, RxDispatcher,
)


@dataclass(frozen=True)
class PingState:
    last_message: str = "(no ping yet)"
    in_flight: bool = False


class PingVM(ComponentVMOf[PingState]):
    pass


def build_ping_vm(hub: MessageHub, dispatcher: RxDispatcher, svc) -> tuple[PingVM, RelayCommand]:
    vm = (PingVM.builder()
          .name("ping").services(hub, dispatcher)
          .model(PingState())
          .build())
    vm.construct()

    async def _do_ping() -> None:
        result = await svc.ping()
        vm.model = replace(vm.model, last_message=result.message, in_flight=False)

    def _start() -> None:
        vm.model = replace(vm.model, in_flight=True)
        asyncio.create_task(_do_ping())

    cmd = (RelayCommand.builder()
           .task(_start)
           .predicate(lambda: not vm.model.in_flight)
           .triggers(vm.property_changed)
           .build())

    return vm, cmd
```

`view`:

```python
def render(vm: PingVM, cmd: RelayCommand) -> None:
    with ui.card():
        ui.label().bind_text_from(vm, "model", backward=lambda m: m.last_message)
        btn = ui.button("Ping backend", on_click=cmd.execute)
        # manual enabled binding:
        def _refresh(_=None) -> None: btn.set_enabled(cmd.can_execute())
        cmd.can_execute_changed.subscribe(_refresh); _refresh()
```

This compiles, runs, and behaves correctly. Use it as the prototype every other page borrows from.
