# Frontend MVVM Overhaul Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the LinguAI Streamlit frontend with a NiceGUI + VMx single-page-app, built on strict horizontal MVVM (top-level `models/`, `viewmodels/`, `views/`), single asyncio loop end-to-end, dual-mode (light/dark) studio aesthetic with brand-orange accent.

**Architecture:** NiceGUI serves a Vue 3 + Quasar UI via uvicorn; per-client `AppShellVM` (VMx `CompositeVM[PageVM]`) holds shell aggregates (UserSession, Settings, Navigation, NotificationCenter) and selected page VM as children; views bind to VM properties and dispatch VM commands; services are async httpx gateways; layer boundaries enforced by import-linter.

**Tech Stack:** NiceGUI (FastAPI + Vue 3 + Quasar), VMx (`vmx` PyPI package, Python flavor; reactivex backend), httpx (async), pydantic + pydantic-settings, pytest + pytest-asyncio + respx, import-linter, ruff, mypy `--strict` on `models/` / `viewmodels/` / `core/` / `views/theme/`, Poetry, Python ≥ 3.10.

**Spec:** [`docs/superpowers/specs/2026-05-30-frontend-mvvm-overhaul-design.md`](../specs/2026-05-30-frontend-mvvm-overhaul-design.md) — read before starting.

---

## Before You Start

- Working directory: `/Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul` (this worktree, branch `worktree-frontend-overhaul`).
- Backend at `backend/` must be runnable for phase 1+ smoke tests. Either `docker compose up backend db` or have it running locally; default `BACKEND_ENDPOINT=http://backend:8000` (Docker) or `http://localhost:8000` (host).
- All shell paths in this plan are relative to `frontend/` unless explicitly prefixed.
- Tests use pytest. Run `poetry run pytest -x -q` from `frontend/` to execute them.
- **Strict rule throughout:** when an `import nicegui` accidentally lands in `viewmodels/` or `models/`, fix it before committing — import-linter will fail CI but it's faster to catch locally.

## Phase Structure

Each phase ends with a verification gate (a checklist of what must be true to proceed). Phases are dependent — do not skip ahead. Commits within a phase should be small; the phase-gate commit is a marker, not a squash point.

---

# Phase 0 — Foundation

**Goal of this phase:** install deps, restructure existing files into the new horizontal layout (without rewriting them), build all cross-cutting infrastructure (core/, theme/, shell VMs, app shell view, DI wiring, main.py, Docker, import-linter), boot the app to render an empty-content-slot shell. **No user-visible pages migrated yet.**

**Phase 0 gate:** `docker compose up frontend` (or `poetry run python -m main` locally) starts the NiceGUI app on `FRONTEND_PORT`, renders the shell chrome (header + sidebar + footer + login panel in content slot when logged out), theme toggle persists across reloads, `poetry run lint-imports` exits 0.

---

## Task 0.1: VMx Python API reconnaissance

**Files:**
- Create: `docs/superpowers/notes/vmx-api-quickref.md`

The spec uses notation like `CompositeVMOf[AttemptVM, PolyglotPuzzleModel]` as design intent. Before writing VMs, pin the actual API surface so later tasks use real class names and method signatures.

- [ ] **Step 1: Install vmx into a scratch env**

```bash
cd /tmp && python3 -m venv vmx-recon && source vmx-recon/bin/activate
pip install vmx
python -c "import vmx; print(vmx.__version__)"
```

Expected: prints `2.1.0` or newer.

- [ ] **Step 2: Catalog the public API**

```bash
python -c "import vmx, pkgutil; [print(m.name) for m in pkgutil.walk_packages(vmx.__path__, prefix='vmx.')]"
python -c "from vmx import components, commands, services, messages; print(dir(components)); print(dir(commands)); print(dir(services))"
```

Note down: exact class names for ComponentVM / CompositeVM / GroupVM / AggregateVMn, RelayCommand signature, MessageHub + RxDispatcher constructors, DerivedProperty if it exists (the README mentions it but may be in a sub-module).

- [ ] **Step 3: Write the cheat-sheet**

Capture in `docs/superpowers/notes/vmx-api-quickref.md`:
- Exact import paths (e.g., `from vmx.components import ComponentVMOf, CompositeVM`)
- Constructor / builder signatures with required and optional args
- How to construct a `ComponentVMOf[M]` (builder vs. direct ctor)
- How children attach to `CompositeVM`
- How `RelayCommand` consumes async execute functions
- How `DerivedProperty` declares sources and recomputes (or the substitute pattern if it's not a direct class)
- Whether `app.storage.user` integration requires anything special in VMs (it shouldn't — VMs are storage-agnostic)

Three sentences max per entry. This file is consulted from every subsequent VM task.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/notes/vmx-api-quickref.md
git commit -m "docs: VMx Python API quickref for overhaul"
```

- [ ] **Step 5: Deactivate scratch env**

```bash
deactivate && rm -rf /tmp/vmx-recon
```

---

## Task 0.2: Update pyproject.toml, Dockerfile, importlinter, pre-commit

**Files:**
- Modify: `frontend/pyproject.toml`
- Modify: `frontend/Dockerfile`
- Create: `frontend/importlinter.toml`
- Create or modify: `.pre-commit-config.yaml` (repo root)

- [ ] **Step 1: Update pyproject.toml dependencies**

Replace the `[tool.poetry.dependencies]` block in `frontend/pyproject.toml` with:

```toml
[tool.poetry.dependencies]
python = "^3.10"
nicegui = "^2.0"
vmx = "^2.1.0"
httpx = "^0.27"
pydantic = {extras = ["email"], version = "^2.6.3"}
pydantic-settings = "^2.2"
email-validator = "^2.1.1"
langdetect = "^1.0.9"
plotly = "^5.20.0"
pandas = "^2.2.2"
numpy = "^1.26.4"

[tool.poetry.group.dev.dependencies]
pytest = "^8.1.1"
pytest-asyncio = "^0.23.6"
pytest-cov = "^5.0.0"
respx = "^0.21"
import-linter = "^2.0"
mypy = "^1.10"
ruff = "^0.5"
```

Removed: `streamlit`, `streamlit-option-menu`, `streamlit-modal`, `websockets`, `sqlmodel`, `requests`.
Added: `nicegui`, `vmx`, `pydantic-settings`, plus dev tooling (`respx`, `import-linter`, `mypy`, `ruff`).

- [ ] **Step 2: Regenerate lockfile**

```bash
cd frontend && poetry lock --no-update && poetry install
```

Expected: resolves cleanly. If a version conflict surfaces, relax the upper bound on the conflicting dep (e.g., `pandas = "^2.0"`).

- [ ] **Step 3: Update Dockerfile**

Replace the `CMD` line in `frontend/Dockerfile`:

```dockerfile
# Specify the command to run the NiceGUI app
CMD ["python", "-m", "main"]
```

Keep the rest of the Dockerfile as-is. NiceGUI defaults to port 8080; the docker-compose port mapping in repo root will need to map `FRONTEND_PORT` to `8080` (was `8501`). We'll fix that in Task 0.11.

- [ ] **Step 4: Create importlinter.toml**

Write `frontend/importlinter.toml`:

```toml
[importlinter]
root_packages = ["frontend"]

[[importlinter.contracts]]
name = "MVVM layering"
type = "layers"
layers = [
    "frontend.views",
    "frontend.viewmodels",
    "frontend.models",
    "frontend.core",
]

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

Note: import-linter resolves package names from the current working dir. The repo's existing `pyproject.toml` is in `frontend/`; running `lint-imports` from `frontend/` will work because the `frontend.` prefix is the package name from that root. If the tool can't find `frontend` as a package, add `frontend/__init__.py` (empty) — current layout doesn't have one, but creating an empty marker is harmless.

- [ ] **Step 5: Create / update pre-commit config**

If `.pre-commit-config.yaml` exists at the repo root, append the local hooks below; otherwise create it:

```yaml
repos:
  - repo: local
    hooks:
      - id: ruff
        name: ruff (lint + format)
        entry: bash -c 'cd frontend && poetry run ruff check --fix .'
        language: system
        files: ^frontend/.*\.py$
        pass_filenames: false

      - id: mypy-strict-mvm
        name: mypy --strict on models/ viewmodels/ core/ views/theme/
        entry: bash -c 'cd frontend && poetry run mypy --strict models viewmodels core views/theme'
        language: system
        files: ^frontend/.*\.py$
        pass_filenames: false

      - id: import-linter
        name: layer boundary contracts
        entry: bash -c 'cd frontend && poetry run lint-imports'
        language: system
        files: ^frontend/.*\.py$
        pass_filenames: false
```

Run `pre-commit install` from repo root if it isn't installed yet (`brew install pre-commit` if missing).

- [ ] **Step 6: Run import-linter to confirm it runs (will pass trivially — no `frontend.viewmodels` yet)**

```bash
cd frontend && poetry run lint-imports
```

Expected: prints contract names and "PASSED" (or "no broken contracts"). If it errors about not finding `frontend`, create `frontend/__init__.py` empty file.

- [ ] **Step 7: Commit**

```bash
git add frontend/pyproject.toml frontend/poetry.lock frontend/Dockerfile frontend/importlinter.toml .pre-commit-config.yaml
[ -f frontend/__init__.py ] && git add frontend/__init__.py
git commit -m "build(frontend): swap streamlit deps for nicegui+vmx; add lint enforcement"
```

---

## Task 0.3: Reorganize existing models/, schema/, services/ into models/{domain,schemas,services}/

**Files:**
- Move: `frontend/models/*.py` → `frontend/models/domain/`
- Move: `frontend/schema/*.py` → `frontend/models/schemas/`
- Move: `frontend/services/*.py` → `frontend/models/services/`
- Delete (after move): `frontend/schema/` directory

This is a structural move — file contents stay UNCHANGED in this task. We rewrite them to async/typed httpx clients in later phase tasks. Goal here is to lock in the new layout so later tasks can import from the right paths.

- [ ] **Step 1: Create the new directory skeleton**

```bash
cd frontend
mkdir -p models/domain models/schemas models/services
touch models/__init__.py models/domain/__init__.py models/schemas/__init__.py models/services/__init__.py
```

- [ ] **Step 2: Git-move domain files**

```bash
git mv models/embeddings.py        models/domain/embeddings.py
git mv models/llm.py               models/domain/llm.py
git mv models/persona.py           models/domain/persona.py
git mv models/polyglot_puzzle.py   models/domain/polyglot_puzzle.py
```

- [ ] **Step 3: Git-move schema files (top-level `schema/` → `models/schemas/`)**

```bash
for f in schema/*.py; do
  git mv "$f" "models/schemas/$(basename $f)"
done
rmdir schema
```

- [ ] **Step 4: Git-move service files**

```bash
for f in services/*.py; do
  git mv "$f" "models/services/$(basename $f)"
done
rmdir services
```

- [ ] **Step 5: Fix all imports throughout the codebase**

Find every `from models.X` / `from schema.X` / `from services.X` and rewrite:

```bash
cd frontend
# from models.X import → from models.domain.X import
grep -rln 'from models\.' --include='*.py' . | xargs sed -i '' -E 's/from models\.([a-z_]+) import/from models.domain.\1 import/g'
# from schema.X import → from models.schemas.X import
grep -rln 'from schema\.' --include='*.py' . | xargs sed -i '' -E 's/from schema\.([a-z_]+) import/from models.schemas.\1 import/g'
# from services.X import → from models.services.X import
grep -rln 'from services\.' --include='*.py' . | xargs sed -i '' -E 's/from services\.([a-z_]+) import/from models.services.\1 import/g'
```

If on Linux (no BSD sed), drop the `''` after `-i`.

- [ ] **Step 6: Verify Streamlit app still imports cleanly (will get deleted later, but should compile now)**

```bash
cd frontend && poetry run python -c "
import importlib, pkgutil, models, models.domain, models.schemas, models.services
for mod in pkgutil.walk_packages(models.__path__, prefix='models.'):
    importlib.import_module(mod.name)
print('all imports OK')
"
```

Expected: prints `all imports OK`. If any import fails (typically because a service imports from `schema.X` that the sed missed, or a circular import surfaces), grep and fix.

- [ ] **Step 7: Commit**

```bash
git add -A frontend/
git commit -m "refactor(frontend): regroup models/ schema/ services/ under models/{domain,schemas,services}/"
```

---

## Task 0.4: Build `core/` (config, logger, http)

**Files:**
- Create: `frontend/core/__init__.py` (empty)
- Create: `frontend/core/config.py`
- Create: `frontend/core/logger.py`
- Create: `frontend/core/http.py`
- Move: `frontend/utils/logger_config.py` → use replaced by `frontend/core/logger.py` (delete after)
- Test: `frontend/tests/core/test_config.py`

- [ ] **Step 1: Create core package**

```bash
cd frontend
mkdir -p core tests/core
touch core/__init__.py tests/__init__.py tests/core/__init__.py
```

- [ ] **Step 2: Write the failing test for AppConfig**

`frontend/tests/core/test_config.py`:

```python
import os
from core.config import AppConfig


def test_app_config_reads_env(monkeypatch):
    monkeypatch.setenv("BACKEND_ENDPOINT", "http://example.test:9000")
    monkeypatch.setenv("FRONTEND_LOG_LEVEL", "DEBUG")
    cfg = AppConfig()
    assert cfg.backend_endpoint == "http://example.test:9000"
    assert cfg.frontend_log_level == "DEBUG"


def test_app_config_defaults(monkeypatch):
    monkeypatch.delenv("BACKEND_ENDPOINT", raising=False)
    monkeypatch.delenv("FRONTEND_LOG_LEVEL", raising=False)
    cfg = AppConfig()
    assert cfg.backend_endpoint == "http://backend:8000"
    assert cfg.frontend_log_level == "INFO"
```

- [ ] **Step 3: Run the test to confirm failure**

```bash
cd frontend && poetry run pytest tests/core/test_config.py -q
```

Expected: ImportError or ModuleNotFoundError for `core.config`.

- [ ] **Step 4: Implement `core/config.py`**

```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Process-wide configuration sourced from environment variables."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    backend_endpoint: str = Field(default="http://backend:8000")
    frontend_port: int = Field(default=8080)
    frontend_log_level: str = Field(default="INFO")
    frontend_log_file: str = Field(default="/app/logs/frontend.log")
    frontend_logger_name: str = Field(default="linguai.frontend")
    http_connect_timeout_s: float = Field(default=5.0)
    http_read_timeout_s: float = Field(default=15.0)
```

- [ ] **Step 5: Run the test**

```bash
poetry run pytest tests/core/test_config.py -q
```

Expected: 2 passed.

- [ ] **Step 6: Implement `core/logger.py`**

Re-home and trim the existing `frontend/utils/logger_config.py`:

```python
import logging
import sys


def setup_logging(logger_name: str, log_level: str = "INFO", log_file: str | None = None) -> logging.Logger:
    """Configure a named logger with a stdout handler (and optional file handler)."""
    logger = logging.getLogger(logger_name)
    logger.setLevel(log_level)
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s — %(message)s")
    stdout = logging.StreamHandler(sys.stdout)
    stdout.setFormatter(fmt)
    logger.addHandler(stdout)

    if log_file:
        try:
            fh = logging.FileHandler(log_file)
            fh.setFormatter(fmt)
            logger.addHandler(fh)
        except OSError:
            logger.warning("Could not open log file %s; continuing with stdout only", log_file)

    logger.propagate = False
    return logger
```

- [ ] **Step 7: Implement `core/http.py`**

```python
from __future__ import annotations
from typing import Optional

import httpx

from core.config import AppConfig


def build_http_client(cfg: AppConfig) -> httpx.AsyncClient:
    """Construct the shared httpx.AsyncClient. Auth header is injected per-request by UserSessionVM."""
    return httpx.AsyncClient(
        base_url=cfg.backend_endpoint,
        timeout=httpx.Timeout(
            connect=cfg.http_connect_timeout_s,
            read=cfg.http_read_timeout_s,
            write=cfg.http_read_timeout_s,
            pool=cfg.http_read_timeout_s,
        ),
        transport=httpx.AsyncHTTPTransport(retries=2),
    )


def set_bearer_token(client: httpx.AsyncClient, token: Optional[str]) -> None:
    """Set or clear the Authorization header on the shared client."""
    if token:
        client.headers["Authorization"] = f"Bearer {token}"
    else:
        client.headers.pop("Authorization", None)
```

- [ ] **Step 8: Delete the old logger location and any utils that core supersedes**

```bash
git rm frontend/utils/logger_config.py
# keep utils/logger.py (log_decorator) and utils/http_utils.py / image_utils.py for now;
# they get deleted in phase 7 when their last caller dies.
```

- [ ] **Step 9: Commit**

```bash
git add -A frontend/core frontend/tests
git rm frontend/utils/logger_config.py  # if not already staged
git commit -m "feat(core): add AppConfig, logger setup, shared httpx client"
```

---

## Task 0.5: Build `views/theme/` (tokens, palette, typography, components)

**Files:**
- Create: `frontend/views/__init__.py`
- Create: `frontend/views/theme/__init__.py`
- Create: `frontend/views/theme/tokens.py`
- Create: `frontend/views/theme/palette.py`
- Create: `frontend/views/theme/typography.py`
- Create: `frontend/views/theme/components.py`
- Test: `frontend/tests/views/theme/test_palette.py`

This task may import `nicegui`; that's expected — `views/` is the only layer allowed to.

- [ ] **Step 1: Create directories**

```bash
cd frontend
mkdir -p views/theme tests/views/theme
touch views/__init__.py views/theme/__init__.py tests/views/__init__.py tests/views/theme/__init__.py
```

- [ ] **Step 2: Write `views/theme/tokens.py`**

```python
"""Design tokens — single source of truth for spacing, radius, shadow, motion."""

SPACING = {"xs": 4, "sm": 8, "md": 12, "lg": 16, "xl": 24, "2xl": 32}
RADIUS  = {"sm": 8, "md": 12, "lg": 14}
SHADOW  = {
    "xs": "0 1px 2px rgba(0,0,0,0.20)",
    "sm": "0 2px 6px rgba(0,0,0,0.25)",
    "md": "0 8px 24px rgba(0,0,0,0.35), 0 1px 2px rgba(0,0,0,0.40)",
}
MOTION  = {"fast_ms": 120, "slow_ms": 240}
```

- [ ] **Step 3: Write failing test for palette resolution**

`frontend/tests/views/theme/test_palette.py`:

```python
from views.theme.palette import BRAND_ORANGE, LIGHT, DARK, palette_for


def test_brand_orange_is_constant_across_modes():
    assert LIGHT.brand == BRAND_ORANGE
    assert DARK.brand == BRAND_ORANGE


def test_palette_for_returns_matching_palette():
    assert palette_for("light") is LIGHT
    assert palette_for("dark") is DARK


def test_palette_for_unknown_defaults_to_dark():
    assert palette_for("system") is DARK  # system→dark until OS detection lands
```

- [ ] **Step 4: Run to confirm failure**

```bash
poetry run pytest tests/views/theme/test_palette.py -q
```

Expected: ImportError.

- [ ] **Step 5: Write `views/theme/palette.py`**

```python
from dataclasses import dataclass
from typing import Literal

BRAND_ORANGE = "#F97316"

ThemeMode = Literal["system", "light", "dark"]


@dataclass(frozen=True)
class ColorPalette:
    brand: str
    surface_0: str   # page background
    surface_1: str   # default card
    surface_2: str   # elevated surface
    border: str
    text_1: str      # primary
    text_2: str      # secondary
    text_3: str      # tertiary / disabled
    success: str
    warning: str
    danger: str
    info: str


LIGHT = ColorPalette(
    brand=BRAND_ORANGE,
    surface_0="#FFFFFF",
    surface_1="#F8FAFC",
    surface_2="#F1F5F9",
    border="#E2E8F0",
    text_1="#0F172A",
    text_2="#475569",
    text_3="#94A3B8",
    success="#10B981",
    warning="#F59E0B",
    danger="#EF4444",
    info="#22D3EE",
)

DARK = ColorPalette(
    brand=BRAND_ORANGE,
    surface_0="#0A0E1A",
    surface_1="#0F1421",
    surface_2="#141A2A",
    border="#1F2937",
    text_1="#E6EAF2",
    text_2="#9CA6BC",
    text_3="#5B6478",
    success="#10B981",
    warning="#FBBF24",
    danger="#F87171",
    info="#22D3EE",
)


def palette_for(mode: ThemeMode) -> ColorPalette:
    if mode == "light":
        return LIGHT
    return DARK  # "dark" or "system" (until OS detection added)
```

- [ ] **Step 6: Run test, expect green**

```bash
poetry run pytest tests/views/theme/test_palette.py -q
```

Expected: 3 passed.

- [ ] **Step 7: Write `views/theme/typography.py`**

```python
from nicegui import ui


def install_fonts() -> None:
    """Inject Google-hosted Inter + JetBrains Mono into the document head. Idempotent."""
    ui.add_head_html(
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?'
        'family=Inter:wght@400;500;600;700&'
        'family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">'
        '<style>'
        'html,body{font-family:"Inter",-apple-system,sans-serif;'
        '-webkit-font-smoothing:antialiased;font-feature-settings:"cv11","ss01"}'
        'code,pre,.mono{font-family:"JetBrains Mono",ui-monospace,monospace}'
        '</style>'
    )
```

- [ ] **Step 8: Write `views/theme/components.py`**

Helpers that wrap NiceGUI primitives with theme tokens applied. Used everywhere in `views/*`.

```python
from typing import Callable, Optional
from nicegui import ui


def card():
    """Return a card container — use inside a `with` block."""
    return ui.card().classes("w-full rounded-xl border border-white/5 bg-[var(--surface-1)]").tight()


def section_header(title: str, subtitle: Optional[str] = None) -> None:
    with ui.row().classes("items-baseline gap-3 mb-3"):
        ui.label(title).classes("text-lg font-semibold tracking-tight")
        if subtitle:
            ui.label(subtitle).classes("text-xs text-[var(--text-3)] uppercase tracking-wider")


def pill_button(
    label: str,
    *,
    on_click: Optional[Callable] = None,
    variant: str = "default",
    icon: Optional[str] = None,
):
    """`variant`: 'default' | 'primary'."""
    cls = "rounded-lg text-sm font-medium px-3 py-1.5"
    if variant == "primary":
        cls += " bg-[var(--brand)] text-[var(--surface-0)]"
    else:
        cls += " bg-white/5 text-[var(--text-1)] hover:bg-white/10"
    btn = ui.button(label, on_click=on_click).props("flat" if variant != "primary" else "unelevated").classes(cls)
    if icon:
        btn.props(f"icon={icon}")
    return btn


def chip(text: str, *, tone: str = "neutral"):
    tones = {
        "neutral": "bg-white/5 text-[var(--text-2)]",
        "brand":   "bg-[var(--brand)]/10 text-[var(--brand)]",
        "success": "bg-emerald-500/10 text-emerald-300",
        "info":    "bg-cyan-500/10 text-cyan-300",
        "warning": "bg-amber-500/10 text-amber-300",
        "danger":  "bg-red-500/10 text-red-300",
    }
    return ui.element("span").classes(f"inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs {tones[tone]}").default_slot
```

Note: `pill_button` and `chip` use Tailwind utility classes via NiceGUI's `.classes()`; Quasar accepts these because NiceGUI ships with Tailwind. The CSS vars (`var(--brand)`, `var(--surface-1)`) are injected by `apply_theme()` in the next task.

- [ ] **Step 9: Add `apply_theme(mode)` helper to `views/theme/palette.py`**

Append to `views/theme/palette.py`:

```python
from nicegui import ui  # noqa: E402  (deliberately imported late — only views/theme/ touches nicegui)


def apply_theme(mode: ThemeMode) -> None:
    """Apply the palette to the current NiceGUI page by setting CSS variables + dark-mode toggle."""
    p = palette_for(mode)
    ui.colors(primary=p.brand, secondary=p.info, accent=p.brand, dark=p.surface_0)
    ui.dark_mode(mode != "light")
    ui.add_head_html(
        f"<style>:root{{"
        f"--brand:{p.brand};"
        f"--surface-0:{p.surface_0};--surface-1:{p.surface_1};--surface-2:{p.surface_2};"
        f"--border:{p.border};"
        f"--text-1:{p.text_1};--text-2:{p.text_2};--text-3:{p.text_3};"
        f"--success:{p.success};--warning:{p.warning};--danger:{p.danger};--info:{p.info};"
        f"}}</style>"
    )
```

(`views/theme/palette.py` imports nicegui only because the `apply_theme` helper needs it. This is allowed — `views/theme/` is part of `views/`.)

- [ ] **Step 10: Commit**

```bash
git add frontend/views frontend/tests/views
git commit -m "feat(theme): tokens, dual-mode palette, typography, component helpers"
```

---

## Task 0.6: Stub `models/services/auth_service.py`

**Files:**
- Create: `frontend/models/services/auth_service.py`

The full implementation lands in Phase 2. We need a callable stub now so `UserSessionVM` (Task 0.7) can be constructed in `core/di.py` (Task 0.9).

- [ ] **Step 1: Write the stub**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import httpx

from models.schemas.authentication import AuthenticationRequest


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    username: Optional[str] = None
    token: Optional[str] = None
    message: str = ""


class AuthService:
    """Async gateway to the backend's authentication endpoints."""

    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def authenticate(self, req: AuthenticationRequest) -> AuthResult:
        # Real implementation in Phase 2 (Task 2.1).
        raise NotImplementedError("AuthService.authenticate — implemented in Phase 2 Task 2.1")

    async def logout(self) -> None:
        # Best-effort; real impl may hit /logout endpoint.
        return None
```

- [ ] **Step 2: Commit**

```bash
git add frontend/models/services/auth_service.py
git commit -m "feat(services): stub AuthService (filled in phase 2)"
```

---

## Task 0.7: Build `viewmodels/shell/` aggregates

**Files:**
- Create: `frontend/viewmodels/__init__.py`
- Create: `frontend/viewmodels/shell/__init__.py`
- Create: `frontend/viewmodels/shell/notification_center_vm.py`
- Create: `frontend/viewmodels/shell/settings_vm.py`
- Create: `frontend/viewmodels/shell/navigation_vm.py`
- Create: `frontend/viewmodels/shell/user_session_vm.py`
- Test: `frontend/tests/viewmodels/shell/test_navigation_vm.py`
- Test: `frontend/tests/viewmodels/shell/test_settings_vm.py`

**Reference `docs/superpowers/notes/vmx-api-quickref.md` for exact VMx class/method names. Pseudocode below uses `from vmx.components import ComponentVMOf, GroupVM` — adjust to your quickref's actual import paths.**

- [ ] **Step 1: Create dirs**

```bash
cd frontend
mkdir -p viewmodels/shell tests/viewmodels/shell
touch viewmodels/__init__.py viewmodels/shell/__init__.py
touch tests/viewmodels/__init__.py tests/viewmodels/shell/__init__.py
```

- [ ] **Step 2: Write `notification_center_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from vmx.components import GroupVM, ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


Severity = Literal["success", "info", "warning", "error"]


@dataclass(frozen=True)
class Toast:
    severity: Severity
    message: str


class ToastVM(ComponentVMOf[Toast]):
    """Single toast — children of NotificationCenterVM."""


class NotificationCenterVM(GroupVM[ToastVM]):
    """Peer collection of toast VMs. Views subscribe to children_changed and render via ui.notify."""

    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="notifications", services=(hub, dispatcher))

    def _push(self, severity: Severity, message: str) -> None:
        toast = Toast(severity=severity, message=message)
        vm = ToastVM.builder().name(f"toast-{len(self.children)}").model(toast) \
            .services(self.message_hub, self.dispatcher).build()
        self.add_child(vm)

    def push_success(self, message: str) -> None: self._push("success", message)
    def push_info(self, message: str)    -> None: self._push("info", message)
    def push_warning(self, message: str) -> None: self._push("warning", message)
    def push_error(self, message: str)   -> None: self._push("error", message)
```

- [ ] **Step 3: Write `settings_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


ThemeMode = Literal["system", "light", "dark"]


@dataclass(frozen=True)
class Settings:
    theme_mode: ThemeMode = "system"
    default_llm_id: Optional[str] = None
    default_persona_id: Optional[str] = None


class SettingsVM(ComponentVMOf[Settings]):
    """User-level preferences. Persistence (app.storage.user) is wired by the View layer."""

    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="settings", services=(hub, dispatcher),
                         model=Settings())

    def set_theme(self, mode: ThemeMode) -> None:
        self.model = replace(self.model, theme_mode=mode)

    def set_default_llm(self, llm_id: str) -> None:
        self.model = replace(self.model, default_llm_id=llm_id)

    def set_default_persona(self, persona_id: str) -> None:
        self.model = replace(self.model, default_persona_id=persona_id)
```

- [ ] **Step 4: Write `navigation_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


Route = Literal["home", "chat", "content_gen", "rewrite_content", "review_writing",
                "polyglot_puzzle", "profile", "assessment", "admin", "register", "login"]


@dataclass(frozen=True)
class NavigationState:
    current: Route = "home"
    drawer_open: bool = True


class NavigationVM(ComponentVMOf[NavigationState]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="navigation", services=(hub, dispatcher),
                         model=NavigationState())

    def go(self, route: Route) -> None:
        if route != self.model.current:
            self.model = replace(self.model, current=route)

    def toggle_drawer(self) -> None:
        self.model = replace(self.model, drawer_open=not self.model.drawer_open)
```

- [ ] **Step 5: Write `user_session_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional

import httpx

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher

from core.http import set_bearer_token
from models.services.auth_service import AuthService
from models.schemas.authentication import AuthenticationRequest


BackendStatus = Literal["online", "offline", "unknown"]


@dataclass(frozen=True)
class UserSession:
    username: Optional[str] = None
    user_type: Optional[str] = None   # e.g., "admin" / "user"
    token: Optional[str] = None
    backend_status: BackendStatus = "unknown"

    @property
    def is_authenticated(self) -> bool:
        return self.token is not None

    @property
    def is_admin(self) -> bool:
        return self.user_type == "admin"


class UserSessionVM(ComponentVMOf[UserSession]):
    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        auth_svc: AuthService,
        http: httpx.AsyncClient,
    ) -> None:
        super().__init__(name="user-session", services=(hub, dispatcher), model=UserSession())
        self._auth = auth_svc
        self._http = http

    async def log_in(self, username: str, password: str) -> bool:
        result = await self._auth.authenticate(AuthenticationRequest(username=username, password=password))
        if result.ok and result.token:
            set_bearer_token(self._http, result.token)
            self.model = replace(self.model, username=result.username, token=result.token, backend_status="online")
            return True
        return False

    async def log_out(self) -> None:
        await self._auth.logout()
        set_bearer_token(self._http, None)
        self.model = UserSession()

    def rehydrate(self, token: Optional[str], username: Optional[str]) -> None:
        """Called once on app startup if app.storage.user holds a saved token."""
        if token:
            set_bearer_token(self._http, token)
            self.model = replace(self.model, token=token, username=username)
```

- [ ] **Step 6: Write VM unit test for `NavigationVM`**

`frontend/tests/viewmodels/shell/test_navigation_vm.py`:

```python
import pytest

from vmx.services import MessageHub, RxDispatcher
from viewmodels.shell.navigation_vm import NavigationVM


@pytest.fixture
def hub() -> MessageHub:
    return MessageHub()


@pytest.fixture
def dispatcher() -> RxDispatcher:
    return RxDispatcher.immediate()


def test_navigation_starts_at_home(hub, dispatcher):
    vm = NavigationVM(hub, dispatcher)
    assert vm.model.current == "home"
    assert vm.model.drawer_open is True


def test_go_updates_route(hub, dispatcher):
    vm = NavigationVM(hub, dispatcher)
    vm.go("chat")
    assert vm.model.current == "chat"


def test_toggle_drawer_flips_state(hub, dispatcher):
    vm = NavigationVM(hub, dispatcher)
    vm.toggle_drawer()
    assert vm.model.drawer_open is False
    vm.toggle_drawer()
    assert vm.model.drawer_open is True
```

- [ ] **Step 7: Write VM unit test for `SettingsVM`**

`frontend/tests/viewmodels/shell/test_settings_vm.py`:

```python
import pytest
from vmx.services import MessageHub, RxDispatcher
from viewmodels.shell.settings_vm import SettingsVM


@pytest.fixture
def services():
    return MessageHub(), RxDispatcher.immediate()


def test_settings_default_theme_is_system(services):
    vm = SettingsVM(*services)
    assert vm.model.theme_mode == "system"


def test_set_theme_updates_model(services):
    vm = SettingsVM(*services)
    vm.set_theme("dark")
    assert vm.model.theme_mode == "dark"
```

- [ ] **Step 8: Add a shared `conftest.py`**

`frontend/tests/conftest.py`:

```python
import pytest

from vmx.services import MessageHub, RxDispatcher


@pytest.fixture
def hub() -> MessageHub:
    return MessageHub()


@pytest.fixture
def dispatcher() -> RxDispatcher:
    return RxDispatcher.immediate()
```

(Per-test files can still create their own fixtures with `def services():` etc.; conftest just provides defaults.)

- [ ] **Step 9: Run the VM tests**

```bash
cd frontend && poetry run pytest tests/viewmodels/shell -q
```

Expected: 5 passed. If a test errors with `AttributeError: ComponentVMOf.builder` or similar, consult `docs/superpowers/notes/vmx-api-quickref.md` and adjust constructor calls.

- [ ] **Step 10: Run import-linter**

```bash
poetry run lint-imports
```

Expected: PASSED. If "viewmodels are UI-free" fails, search `viewmodels/` for stray `nicegui` imports.

- [ ] **Step 11: Commit**

```bash
git add frontend/viewmodels frontend/tests
git commit -m "feat(viewmodels): shell aggregates (Notification, Settings, Navigation, UserSession)"
```

---

## Task 0.8: Build `viewmodels/app_shell_vm.py`

**Files:**
- Create: `frontend/viewmodels/app_shell_vm.py`
- Test: `frontend/tests/viewmodels/test_app_shell_vm.py`

The root composite. Children are page VMs (one selected at a time); aggregates are the four shell VMs from Task 0.7.

- [ ] **Step 1: Write `app_shell_vm.py`**

```python
from __future__ import annotations
from typing import Iterable

from vmx.components import CompositeVM, ComponentVM
from vmx.services import MessageHub, RxDispatcher

from viewmodels.shell.navigation_vm import NavigationVM, Route
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM
from viewmodels.shell.user_session_vm import UserSessionVM


class PageVM(ComponentVM):
    """Marker base for top-level page view-models. Pages override .route to a Route literal."""
    route: Route = "home"


class AppShellVM(CompositeVM[PageVM]):
    """
    Root VM. Holds shell aggregates and the selected page VM. Constructed once per NiceGUI client
    inside the @ui.page handler — services (hub/dispatcher/http) are process-scoped, this is per-client.
    """

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        *,
        session: UserSessionVM,
        settings: SettingsVM,
        navigation: NavigationVM,
        notifications: NotificationCenterVM,
        pages: Iterable[PageVM],
    ) -> None:
        super().__init__(name="app-shell", services=(hub, dispatcher))
        self.session = session
        self.settings = settings
        self.navigation = navigation
        self.notifications = notifications
        for p in pages:
            self.add_child(p)
        self._route_to_page = {p.route: p for p in self.children}
        # When NavigationVM.current changes, update CompositeVM selection.
        self.navigation.model_changed.subscribe(lambda _: self._sync_selection())
        self._sync_selection()

    def _sync_selection(self) -> None:
        target = self._route_to_page.get(self.navigation.model.current)
        if target is not None and self.selected is not target:
            self.selected = target
```

- [ ] **Step 2: Write a minimal test**

`frontend/tests/viewmodels/test_app_shell_vm.py`:

```python
import pytest
from dataclasses import dataclass

from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import AppShellVM, PageVM
from viewmodels.shell.navigation_vm import NavigationVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM
from viewmodels.shell.user_session_vm import UserSessionVM


class FakePage(PageVM):
    def __init__(self, hub, dispatcher, route: str) -> None:
        super().__init__(name=f"page-{route}", services=(hub, dispatcher))
        self.route = route  # type: ignore[assignment]


@pytest.fixture
def services():
    return MessageHub(), RxDispatcher.immediate()


@pytest.fixture
def shell(services, monkeypatch):
    hub, disp = services
    class _NullAuth:
        async def authenticate(self, *_): ...
        async def logout(self): ...
    import httpx
    http = httpx.AsyncClient(base_url="http://example.test")
    session = UserSessionVM(hub, disp, _NullAuth(), http)
    settings = SettingsVM(hub, disp)
    navigation = NavigationVM(hub, disp)
    notifications = NotificationCenterVM(hub, disp)
    pages = [FakePage(hub, disp, "home"), FakePage(hub, disp, "chat")]
    return AppShellVM(hub, disp, session=session, settings=settings,
                     navigation=navigation, notifications=notifications, pages=pages)


def test_initial_selection_matches_navigation(shell):
    assert shell.selected.route == "home"


def test_navigation_change_updates_selection(shell):
    shell.navigation.go("chat")
    assert shell.selected.route == "chat"
```

- [ ] **Step 3: Run tests**

```bash
cd frontend && poetry run pytest tests/viewmodels/test_app_shell_vm.py -q
```

Expected: 2 passed. (If VMx's actual API for `selected` differs from `self.selected = ...`, consult the quickref and adjust.)

- [ ] **Step 4: Run import-linter**

```bash
poetry run lint-imports
```

Expected: PASSED.

- [ ] **Step 5: Commit**

```bash
git add frontend/viewmodels/app_shell_vm.py frontend/tests/viewmodels/test_app_shell_vm.py
git commit -m "feat(viewmodels): AppShellVM root composite"
```

---

## Task 0.9: Build `core/di.py` (composition root)

**Files:**
- Create: `frontend/core/di.py`

- [ ] **Step 1: Write `di.py` stub-pages version**

For Phase 0 we don't have page VMs yet. Use a placeholder `HomePagePlaceholder` (replaced in Phase 2 Task 2.7 with the real `HomeVM`).

```python
from __future__ import annotations
import asyncio

import httpx

from vmx.services import MessageHub, RxDispatcher

from core.config import AppConfig
from core.http import build_http_client

from models.services.auth_service import AuthService

from viewmodels.app_shell_vm import AppShellVM, PageVM
from viewmodels.shell.navigation_vm import NavigationVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM
from viewmodels.shell.user_session_vm import UserSessionVM


class HomePagePlaceholder(PageVM):
    """Placeholder until Phase 2 Task 2.7 implements HomeVM."""
    route = "home"

    def __init__(self, hub, dispatcher) -> None:
        super().__init__(name="home-placeholder", services=(hub, dispatcher))


def build_process_scoped(cfg: AppConfig) -> tuple[MessageHub, RxDispatcher, httpx.AsyncClient, AuthService]:
    """Build the things that outlive any single NiceGUI client."""
    hub = MessageHub()
    # Late-bind the asyncio loop when first used (main.py calls into this from inside ui.run's loop).
    dispatcher = RxDispatcher.asyncio(asyncio.get_event_loop())
    http = build_http_client(cfg)
    auth_svc = AuthService(http)
    return hub, dispatcher, http, auth_svc


def build_app_shell(
    cfg: AppConfig,
    hub: MessageHub,
    dispatcher: RxDispatcher,
    http: httpx.AsyncClient,
    auth_svc: AuthService,
) -> AppShellVM:
    """Build one AppShellVM per NiceGUI client. Process-scoped objects passed in."""
    notifications = NotificationCenterVM(hub, dispatcher)
    settings = SettingsVM(hub, dispatcher)
    navigation = NavigationVM(hub, dispatcher)
    session = UserSessionVM(hub, dispatcher, auth_svc, http)
    pages = [HomePagePlaceholder(hub, dispatcher)]
    return AppShellVM(
        hub, dispatcher,
        session=session, settings=settings, navigation=navigation, notifications=notifications,
        pages=pages,
    )
```

- [ ] **Step 2: Run import-linter**

```bash
cd frontend && poetry run lint-imports
```

Expected: PASSED.

- [ ] **Step 3: Commit**

```bash
git add frontend/core/di.py
git commit -m "feat(core): DI composition root (placeholder home page)"
```

---

## Task 0.10: Build `views/shell/` (header, sidebar, footer, login_panel, toast_host)

**Files:**
- Create: `frontend/views/shell/__init__.py`
- Create: `frontend/views/shell/header.py`
- Create: `frontend/views/shell/sidebar.py`
- Create: `frontend/views/shell/footer.py`
- Create: `frontend/views/shell/login_panel.py`
- Create: `frontend/views/shell/toast_host.py`

These match the chrome from the polish-v2 mockup (dark by default, brand-orange accent).

- [ ] **Step 1: Create dir**

```bash
cd frontend && mkdir -p views/shell && touch views/shell/__init__.py
```

- [ ] **Step 2: Write `header.py`**

```python
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM


def render(shell: AppShellVM) -> None:
    with ui.header(elevated=False).classes(
        "items-center px-4 py-2 gap-3 bg-[var(--surface-0)]/70 backdrop-blur "
        "border-b border-white/5"
    ):
        ui.icon("menu").on("click", shell.navigation.toggle_drawer).classes("text-[var(--text-2)] cursor-pointer")
        ui.element("div").classes(
            "w-6 h-6 rounded-md"
        ).style("background:linear-gradient(135deg,#F97316,#FB923C,#FBBF24);box-shadow:0 0 12px rgba(249,115,22,0.4)")
        ui.label("LinguAI").classes("text-sm font-semibold tracking-tight")
        ui.label("/").classes("text-[var(--text-3)] mx-1")
        ui.label().bind_text_from(shell.navigation, "model", backward=lambda m: m.current.replace("_", " ").title()) \
            .classes("text-sm text-[var(--text-1)]")
        ui.space()
        # Backend status dot
        with ui.row().classes("items-center gap-1.5 text-xs text-[var(--text-2)]"):
            ui.element("span").bind_classes_from(
                shell.session, "model",
                backward=lambda m: "w-1.5 h-1.5 rounded-full "
                                   + ("bg-emerald-400" if m.backend_status == "online" else
                                      "bg-red-400" if m.backend_status == "offline" else "bg-slate-500"),
            )
            ui.label("Backend")
        # Theme toggle
        ui.icon("dark_mode").on("click", _toggle_theme(shell)).classes("text-[var(--text-2)] cursor-pointer")
        # User avatar (or initials)
        with ui.row().classes("items-center gap-2 pl-2 border-l border-white/5"):
            ui.label().bind_text_from(shell.session, "model",
                                      backward=lambda m: (m.username or "?")[:2].upper()) \
                .classes("w-7 h-7 rounded-full bg-violet-500 text-white text-xs font-semibold "
                         "flex items-center justify-center")


def _toggle_theme(shell: AppShellVM):
    def _cb() -> None:
        nxt = {"system": "light", "light": "dark", "dark": "system"}[shell.settings.model.theme_mode]
        shell.settings.set_theme(nxt)
        from views.theme.palette import apply_theme
        apply_theme(nxt)
        # Persist
        from nicegui import app as nicegui_app
        nicegui_app.storage.user["theme_mode"] = nxt
    return _cb
```

- [ ] **Step 3: Write `sidebar.py`**

```python
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM


_LEARN = [("home", "home", "Home"),
          ("chat", "chat_bubble", "Chat"),
          ("content_gen", "auto_stories", "Content"),
          ("rewrite_content", "edit", "Rewrite"),
          ("review_writing", "rate_review", "Review"),
          ("polyglot_puzzle", "extension", "Polyglot")]
_YOU = [("profile", "person", "Profile"),
        ("assessment", "insights", "Assessment")]
_SYSTEM = [("admin", "tune", "Admin")]


def render(shell: AppShellVM) -> None:
    with ui.left_drawer(value=shell.navigation.model.drawer_open, fixed=False).classes(
        "bg-[var(--surface-0)] border-r border-white/5 p-3 gap-1"
    ) as drawer:
        # Two-way bind drawer visibility to NavigationVM.drawer_open
        shell.navigation.model_changed.subscribe(lambda _: drawer.set_value(shell.navigation.model.drawer_open))

        _section("LEARN", _LEARN, shell)
        _section("YOU", _YOU, shell)
        if shell.session.model.is_admin:
            _section("SYSTEM", _SYSTEM, shell)


def _section(label: str, items, shell: AppShellVM) -> None:
    ui.label(label).classes("text-[10px] tracking-widest text-[var(--text-3)] mt-3 mb-1 px-2 font-semibold")
    for route, icon, text in items:
        with ui.row().classes("items-center gap-2 px-2 py-1.5 rounded-md cursor-pointer text-sm text-[var(--text-2)] "
                              "hover:bg-white/5") \
                .on("click", _goto(shell, route)):
            ui.icon(icon).classes("text-base")
            ui.label(text)
```

```python
def _goto(shell: AppShellVM, route: str):
    def _cb() -> None:
        shell.navigation.go(route)  # type: ignore[arg-type]
    return _cb
```

- [ ] **Step 4: Write `footer.py`**

```python
from nicegui import ui


def render() -> None:
    with ui.footer(fixed=False).classes("bg-[var(--surface-0)] border-t border-white/5 px-4 py-2"):
        ui.label("LinguAI · learning with AI").classes("text-[11px] text-[var(--text-3)]")
```

- [ ] **Step 5: Write `login_panel.py`**

A minimal panel rendered into the content slot when logged out. Real `LoginView` arrives in Phase 2.

```python
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM


def render(shell: AppShellVM) -> None:
    with ui.column().classes("max-w-sm mx-auto mt-20 gap-3"):
        ui.label("Sign in to LinguAI").classes("text-xl font-semibold tracking-tight")
        username = ui.input("Username").props("outlined dense").classes("w-full")
        password = ui.input("Password", password=True).props("outlined dense").classes("w-full")
        msg = ui.label().classes("text-xs text-[var(--danger)]")

        async def submit() -> None:
            ok = await shell.session.log_in(username.value, password.value)
            if not ok:
                msg.text = "Login failed."

        ui.button("Sign in", on_click=submit).props("unelevated color=primary").classes("w-full mt-1")
```

- [ ] **Step 6: Write `toast_host.py`**

```python
from nicegui import ui

from viewmodels.shell.notification_center_vm import NotificationCenterVM


def attach(notifications: NotificationCenterVM) -> None:
    """Subscribe to toast adds and fan out to ui.notify."""
    def _on_add(_) -> None:
        if not notifications.children:
            return
        latest = notifications.children[-1].model
        ui.notify(latest.message, type={"success": "positive", "info": "info",
                                       "warning": "warning", "error": "negative"}[latest.severity])
    notifications.children_changed.subscribe(_on_add)
```

- [ ] **Step 7: Commit**

```bash
git add frontend/views/shell
git commit -m "feat(views/shell): header, sidebar, footer, login panel, toast host"
```

---

## Task 0.11: Build `views/app_shell.py` and `main.py`

**Files:**
- Create: `frontend/views/app_shell.py`
- Create: `frontend/main.py`
- Modify: `docker-compose.yml` (repo root) — change FRONTEND_PORT mapping to `:8080`

- [ ] **Step 1: Write `views/app_shell.py`**

```python
from nicegui import ui, app

from viewmodels.app_shell_vm import AppShellVM
from views.theme.palette import apply_theme
from views.theme.typography import install_fonts
from views.shell import header as _header, sidebar as _sidebar, footer as _footer, \
    login_panel as _login_panel, toast_host as _toast_host

# Page-VM renderers register themselves here in later phases:
PAGE_RENDERERS: dict[str, "callable"] = {}


def register_page_renderer(route: str, fn) -> None:
    PAGE_RENDERERS[route] = fn


def mount(shell: AppShellVM) -> None:
    """Build the chrome and a content slot that swaps when navigation changes."""
    install_fonts()
    saved_mode = app.storage.user.get("theme_mode", "system")
    shell.settings.set_theme(saved_mode)
    apply_theme(saved_mode)

    _header.render(shell)
    _sidebar.render(shell)
    _footer.render()
    _toast_host.attach(shell.notifications)

    content_slot = ui.column().classes("w-full max-w-6xl mx-auto px-6 py-6")

    def _rerender() -> None:
        content_slot.clear()
        with content_slot:
            if not shell.session.model.is_authenticated:
                _login_panel.render(shell)
                return
            renderer = PAGE_RENDERERS.get(shell.navigation.model.current)
            if renderer is None:
                ui.label(f"(no renderer for '{shell.navigation.model.current}')") \
                    .classes("text-[var(--text-3)] text-sm italic")
                return
            renderer(shell)

    shell.navigation.model_changed.subscribe(lambda _: _rerender())
    shell.session.model_changed.subscribe(lambda _: _rerender())
    _rerender()
```

- [ ] **Step 2: Write `main.py`**

```python
from __future__ import annotations
import asyncio

from nicegui import ui, app

from core.config import AppConfig
from core.logger import setup_logging
from core.di import build_process_scoped, build_app_shell
from views.app_shell import mount


def _bootstrap() -> tuple[AppConfig, object]:
    cfg = AppConfig()
    setup_logging(cfg.frontend_logger_name, cfg.frontend_log_level, cfg.frontend_log_file)
    return cfg, build_process_scoped(cfg)


CFG, PROCESS = _bootstrap()
HUB, DISPATCHER, HTTP, AUTH = PROCESS  # unpack


@ui.page("/")
def index_page() -> None:
    shell = build_app_shell(CFG, HUB, DISPATCHER, HTTP, AUTH)
    # Rehydrate session from storage if present.
    saved_token = app.storage.user.get("auth_token")
    saved_user = app.storage.user.get("username")
    if saved_token:
        shell.session.rehydrate(saved_token, saved_user)
    mount(shell)


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        host="0.0.0.0",
        port=CFG.frontend_port,
        title="LinguAI",
        dark=True,
        storage_secret="linguai-frontend-dev-secret",  # production: env-injected
        show=False,
        reload=False,
    )
```

- [ ] **Step 3: Update docker-compose.yml frontend service port**

In the repo-root `docker-compose.yml`, the `frontend` service maps `"${FRONTEND_PORT}:8501"`. Change to `"${FRONTEND_PORT}:8080"`:

```yaml
  frontend:
    build: ./frontend
    container_name: frontend
    restart: unless-stopped
    ports:
      - "${FRONTEND_PORT}:8080"
```

(NiceGUI's default port is 8080; `main.py` uses `cfg.frontend_port=8080` for the in-container port.)

- [ ] **Step 4: Commit**

```bash
git add frontend/views/app_shell.py frontend/main.py docker-compose.yml
git commit -m "feat(frontend): NiceGUI entry, app shell mount, content-slot rerender"
```

---

## Task 0.12: Phase 0 gate — boot and verify

- [ ] **Step 1: Build the Docker image**

From repo root:

```bash
docker compose build frontend
```

Expected: builds cleanly. If pip fails to find `nicegui` or `vmx`, check the lockfile in the image (rebuild after `poetry lock`).

- [ ] **Step 2: Bring up the stack (backend + db needed for later phases; frontend alone for now)**

```bash
docker compose up -d frontend
docker compose logs -f frontend
```

Expected logs: `NiceGUI ready to go on http://...:8080`.

- [ ] **Step 3: Hit the URL**

Open `http://localhost:${FRONTEND_PORT}` in a browser.

Expected:
- Dark-mode shell with header (logo + breadcrumb + status dot + theme + avatar), left drawer (sections Learn / You; Admin hidden until logged in as admin), footer.
- Content slot shows the login panel (we're not authenticated).
- Theme toggle in header cycles `system → light → dark → system` and persists across reload.

- [ ] **Step 4: Run all linters / tests**

```bash
cd frontend
poetry run pytest -q
poetry run lint-imports
poetry run mypy --strict models viewmodels core views/theme
```

Expected:
- Tests: existing test count (5 from settings/nav, 2 from shell, 2 from config, 3 from palette) all pass.
- lint-imports: all 4 contracts PASSED.
- mypy: clean (or a small number of fixable findings — fix them before proceeding).

- [ ] **Step 5: Commit gate marker**

```bash
git commit --allow-empty -m "chore: phase 0 gate — shell boots, theme persists, lint+types green"
```

---

# Phase 1 — Smoke validation

**Goal of this phase:** prove the VMx ↔ NiceGUI ↔ httpx pipeline end-to-end on the lowest-risk surface. One throwaway "ping" page wired to the backend's existing health endpoint (`GET /` returns `{"message": "..."}` in the current backend). After this phase, we know the pattern works and every later page just applies the same template.

**Phase 1 gate:** clicking the "Ping" button on `/ping` causes the bound text to update with the backend response; `RelayCommand.can_execute` toggles the button off during in-flight requests; no `asyncio.run()` in the call chain; VM unit test passes.

---

## Task 1.1: Build the smoke page (PingVM + PingView)

**Files:**
- Create: `frontend/viewmodels/ping/__init__.py`
- Create: `frontend/viewmodels/ping/ping_vm.py`
- Create: `frontend/views/ping/__init__.py`
- Create: `frontend/views/ping/ping_view.py`
- Create: `frontend/models/services/ping_service.py`
- Modify: `frontend/main.py` (register a `/ping` route)
- Modify: `frontend/views/app_shell.py` (register ping renderer — not strictly needed since the smoke uses a separate `@ui.page` route)
- Test: `frontend/tests/viewmodels/ping/test_ping_vm.py`

For phase 1 we mount the ping at its own NiceGUI route `/ping` rather than as a child of `AppShellVM`. This avoids polluting the page registry with throwaway code — we delete the entire smoke artifact at the end of Phase 7.

- [ ] **Step 1: Write `models/services/ping_service.py`**

```python
from __future__ import annotations
from dataclasses import dataclass
import httpx


@dataclass(frozen=True)
class PingResult:
    ok: bool
    message: str


class PingService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def ping(self) -> PingResult:
        try:
            r = await self._http.get("/")
            r.raise_for_status()
            payload = r.json()
            return PingResult(ok=True, message=str(payload.get("message", payload)))
        except httpx.HTTPError as e:
            return PingResult(ok=False, message=f"http error: {e}")
```

- [ ] **Step 2: Write `viewmodels/ping/ping_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace

from vmx.components import ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from models.services.ping_service import PingService


@dataclass(frozen=True)
class PingState:
    last_message: str = "(no ping yet)"
    in_flight: bool = False


class PingVM(ComponentVMOf[PingState]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, svc: PingService) -> None:
        super().__init__(name="ping", services=(hub, dispatcher), model=PingState())
        self._svc = svc
        self.ping_command = RelayCommand(
            execute=self._ping,
            can_execute=lambda: not self.model.in_flight,
        )

    async def _ping(self) -> None:
        self.model = replace(self.model, in_flight=True)
        try:
            result = await self._svc.ping()
            self.model = replace(self.model, last_message=result.message, in_flight=False)
        except Exception as e:  # defensive — service swallows httpx errors but be safe
            self.model = replace(self.model, last_message=f"unexpected: {e}", in_flight=False)
```

- [ ] **Step 3: Write VM unit test**

`frontend/tests/viewmodels/ping/test_ping_vm.py`:

```python
import pytest
from unittest.mock import AsyncMock

from vmx.services import MessageHub, RxDispatcher

from viewmodels.ping.ping_vm import PingVM
from models.services.ping_service import PingResult


@pytest.fixture
def services():
    return MessageHub(), RxDispatcher.immediate()


@pytest.mark.asyncio
async def test_ping_updates_model_on_success(services):
    hub, disp = services
    svc = AsyncMock()
    svc.ping = AsyncMock(return_value=PingResult(ok=True, message="LinguAI backend up"))
    vm = PingVM(hub, disp, svc)
    assert vm.model.last_message == "(no ping yet)"

    await vm.ping_command.execute_async()
    assert vm.model.last_message == "LinguAI backend up"
    assert vm.model.in_flight is False


@pytest.mark.asyncio
async def test_ping_command_disables_during_flight(services):
    hub, disp = services
    svc = AsyncMock()

    async def slow_ping() -> PingResult:
        # Simulate slow request — model should be in_flight here.
        assert vm.model.in_flight is True
        assert vm.ping_command.can_execute() is False
        return PingResult(ok=True, message="ok")

    svc.ping = slow_ping
    vm = PingVM(*services, svc)
    await vm.ping_command.execute_async()
    assert vm.ping_command.can_execute() is True
```

Note: the assertion inside `slow_ping` only fires if the model update happens *before* the awaited service call returns. If your VMx `RelayCommand.execute_async` schedules differently, the assertion may need to move into an explicit `asyncio.sleep(0)` after triggering the command. Consult the quickref.

- [ ] **Step 4: Add `pytest-asyncio` config**

Append to `frontend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"
```

- [ ] **Step 5: Run VM test**

```bash
cd frontend && poetry run pytest tests/viewmodels/ping -q
```

Expected: 2 passed. (`execute_async` is the name from the spec; substitute if quickref says otherwise.)

- [ ] **Step 6: Write `views/ping/ping_view.py`**

```python
from nicegui import ui

from viewmodels.ping.ping_vm import PingVM
from views.theme.components import card, pill_button, section_header
from views.theme.palette import apply_theme
from views.theme.typography import install_fonts


def render(vm: PingVM) -> None:
    install_fonts()
    apply_theme("dark")
    with ui.column().classes("max-w-xl mx-auto mt-16 gap-4"):
        with card():
            section_header("Ping", subtitle="VMx + NiceGUI + httpx smoke")
            ui.label().bind_text_from(vm, "model", backward=lambda m: m.last_message) \
                .classes("text-sm text-[var(--text-1)]")
            with ui.row().classes("gap-2 mt-3"):
                btn = pill_button("Ping backend", variant="primary",
                                   on_click=vm.ping_command.execute_async)
                btn.bind_enabled_from(vm, "model", backward=lambda m: not m.in_flight)
                ui.label("…").bind_visibility_from(vm, "model", backward=lambda m: m.in_flight) \
                    .classes("text-xs text-[var(--text-3)] self-center")
```

- [ ] **Step 7: Register the `/ping` route in `main.py`**

Append below the existing `@ui.page("/")` in `frontend/main.py`:

```python
@ui.page("/ping")
def ping_page() -> None:
    from viewmodels.ping.ping_vm import PingVM
    from models.services.ping_service import PingService
    from views.ping.ping_view import render as render_ping
    svc = PingService(HTTP)
    vm = PingVM(HUB, DISPATCHER, svc)
    render_ping(vm)
```

- [ ] **Step 8: Boot, hit `/ping`, click button, observe**

```bash
docker compose up -d frontend backend db
open "http://localhost:${FRONTEND_PORT}/ping"
```

Expected: button text "Ping backend"; clicking it updates the bound label to "LinguAI backend up" (or whatever your backend's root endpoint returns); button momentarily disables during flight.

- [ ] **Step 9: Commit + gate**

```bash
git add frontend/models/services/ping_service.py frontend/viewmodels/ping \
        frontend/views/ping frontend/tests/viewmodels/ping frontend/main.py \
        frontend/pyproject.toml
git commit -m "feat(smoke): /ping page exercises VMx+NiceGUI+httpx end-to-end"
git commit --allow-empty -m "chore: phase 1 gate — smoke proves pattern works"
```

---

# Phase 2 — Auth + Home

**Goal of this phase:** real `AuthService`, `LoginVM/View`, `RegisterVM` wizard (`AggregateVM3`-shaped), `HomeVM/View` matching the polish-v2 dashboard. `UserSessionVM` persists across reload via `app.storage.user`. Drop the `HomePagePlaceholder` from `core/di.py`.

**Phase 2 gate:** register → log in → see home dashboard → log out (lifecycle reconstruct verified — VMs reset cleanly). Token survives page reload. Failed login surfaces an inline error.

---

## Task 2.1: Implement `models/services/auth_service.py` (real)

**Files:**
- Modify: `frontend/models/services/auth_service.py`
- Test: `frontend/tests/models/services/test_auth_service.py`

**Confirm against backend first:** look at `backend/routers/` or equivalent for the auth endpoints' actual paths, request bodies, and response shapes. The current Streamlit code calls `await UserService.authenticate(AuthenticationRequest(...))` — find the corresponding backend endpoint and copy its contract.

- [ ] **Step 1: Confirm backend auth contract**

```bash
cd /Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul/backend
grep -rln 'authenticat\|login' --include='*.py' . | head
```

Note: endpoint path (e.g., `/auth/login`), HTTP method (POST), request schema (`{username, password}` likely), response schema (likely `{status: bool, username: str, message: str, token?: str}`). If the backend doesn't already emit a token, see note in Step 2.

- [ ] **Step 2: Implement `AuthService.authenticate`**

Replace `frontend/models/services/auth_service.py`:

```python
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional

import httpx

from models.schemas.authentication import AuthenticationRequest


@dataclass(frozen=True)
class AuthResult:
    ok: bool
    username: Optional[str] = None
    user_type: Optional[str] = None
    token: Optional[str] = None
    message: str = ""


class AuthService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def authenticate(self, req: AuthenticationRequest) -> AuthResult:
        try:
            r = await self._http.post("/auth/login", json=req.model_dump())
            r.raise_for_status()
            data = r.json()
            return AuthResult(
                ok=bool(data.get("status", False)),
                username=data.get("username"),
                user_type=data.get("user_type"),
                token=data.get("token", data.get("session_id", "")) or None,
                message=str(data.get("message", "")),
            )
        except httpx.HTTPStatusError as e:
            return AuthResult(ok=False, message=f"auth failed ({e.response.status_code})")
        except httpx.HTTPError as e:
            return AuthResult(ok=False, message=f"network error: {e}")

    async def logout(self) -> None:
        try:
            await self._http.post("/auth/logout")
        except httpx.HTTPError:
            pass  # best-effort
```

**If the backend doesn't issue a token today:** until phase 7, use the username as the bearer token (the current Streamlit code already trusts username after authentication). Note this in the file as a `# TODO(phase-7-backend): real token issuance` comment if you take this shortcut.

- [ ] **Step 3: Write service test with respx**

`frontend/tests/models/services/__init__.py` (empty) + `frontend/tests/models/services/test_auth_service.py`:

```python
import httpx
import pytest
import respx

from models.services.auth_service import AuthService
from models.schemas.authentication import AuthenticationRequest


@pytest.mark.asyncio
async def test_authenticate_success():
    async with httpx.AsyncClient(base_url="http://test") as http:
        with respx.mock(assert_all_called=True) as router:
            router.post("http://test/auth/login").mock(
                return_value=httpx.Response(200, json={
                    "status": True, "username": "alice", "user_type": "user",
                    "token": "tok-abc", "message": "ok",
                })
            )
            svc = AuthService(http)
            r = await svc.authenticate(AuthenticationRequest(username="alice", password="x"))
            assert r.ok and r.token == "tok-abc" and r.username == "alice"


@pytest.mark.asyncio
async def test_authenticate_failure():
    async with httpx.AsyncClient(base_url="http://test") as http:
        with respx.mock() as router:
            router.post("http://test/auth/login").mock(return_value=httpx.Response(401))
            svc = AuthService(http)
            r = await svc.authenticate(AuthenticationRequest(username="alice", password="x"))
            assert not r.ok
```

- [ ] **Step 4: Run tests**

```bash
cd frontend && poetry run pytest tests/models/services -q
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/models/services/auth_service.py frontend/tests/models/services
git commit -m "feat(services): real AuthService against /auth/login"
```

---

## Task 2.2: Build `viewmodels/auth/login_vm.py`

**Files:**
- Create: `frontend/viewmodels/auth/__init__.py`
- Create: `frontend/viewmodels/auth/login_vm.py`
- Test: `frontend/tests/viewmodels/auth/test_login_vm.py`

- [ ] **Step 1: Create dir, write `login_vm.py`**

```bash
cd frontend && mkdir -p viewmodels/auth tests/viewmodels/auth
touch viewmodels/auth/__init__.py tests/viewmodels/auth/__init__.py
```

```python
# viewmodels/auth/login_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace

from vmx.components import ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM


@dataclass(frozen=True)
class LoginForm:
    username: str = ""
    password: str = ""
    error: str = ""
    in_flight: bool = False


class LoginVM(ComponentVMOf[LoginForm]):
    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
    ) -> None:
        super().__init__(name="login", services=(hub, dispatcher), model=LoginForm())
        self._session = session
        self._notify = notifications
        self.login_command = RelayCommand(
            execute=self._login,
            can_execute=self._can_login,
        )

    def _can_login(self) -> bool:
        return bool(self.model.username and self.model.password and not self.model.in_flight)

    async def _login(self) -> None:
        self.model = replace(self.model, in_flight=True, error="")
        ok = await self._session.log_in(self.model.username, self.model.password)
        if ok:
            self._notify.push_success(f"Welcome, {self.model.username}")
            self.model = LoginForm()  # clear
        else:
            self.model = replace(self.model, in_flight=False, error="Login failed.")
```

- [ ] **Step 2: Write VM test**

`frontend/tests/viewmodels/auth/test_login_vm.py`:

```python
import pytest
from unittest.mock import AsyncMock
from dataclasses import replace

import httpx
from vmx.services import MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.auth.login_vm import LoginVM
from models.services.auth_service import AuthResult


@pytest.fixture
def vms():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    auth = AsyncMock()
    auth.authenticate = AsyncMock(return_value=AuthResult(ok=True, username="alice", token="t"))
    http = httpx.AsyncClient(base_url="http://test")
    session = UserSessionVM(hub, disp, auth, http)
    notifications = NotificationCenterVM(hub, disp)
    vm = LoginVM(hub, disp, session, notifications)
    return vm, session, notifications, auth


def test_command_disabled_when_fields_empty(vms):
    vm, *_ = vms
    assert not vm.login_command.can_execute()


def test_command_enabled_when_fields_present(vms):
    vm, *_ = vms
    vm.model = replace(vm.model, username="alice", password="x")
    assert vm.login_command.can_execute()


@pytest.mark.asyncio
async def test_login_success_clears_form_and_notifies(vms):
    vm, session, notifications, auth = vms
    vm.model = replace(vm.model, username="alice", password="x")
    await vm.login_command.execute_async()
    assert vm.model.username == ""  # cleared
    assert session.model.is_authenticated
    assert len(notifications.children) == 1


@pytest.mark.asyncio
async def test_login_failure_surfaces_error(vms):
    vm, session, notifications, auth = vms
    auth.authenticate = AsyncMock(return_value=AuthResult(ok=False, message="bad"))
    vm.model = replace(vm.model, username="alice", password="x")
    await vm.login_command.execute_async()
    assert vm.model.error == "Login failed."
    assert not session.model.is_authenticated
```

- [ ] **Step 3: Run, expect green**

```bash
cd frontend && poetry run pytest tests/viewmodels/auth -q
```

Expected: 4 passed.

- [ ] **Step 4: Commit**

```bash
git add frontend/viewmodels/auth/login_vm.py frontend/tests/viewmodels/auth
git commit -m "feat(viewmodels): LoginVM with command guards and notification side-effect"
```

---

## Task 2.3: Build `views/auth/login_view.py` and wire into shell

**Files:**
- Create: `frontend/views/auth/__init__.py`
- Create: `frontend/views/auth/login_view.py`
- Modify: `frontend/views/app_shell.py` (route the login form through `LoginView` when unauth'd, instead of the placeholder `login_panel`)
- Modify: `frontend/views/shell/login_panel.py` (delete — replaced by `LoginView`)

- [ ] **Step 1: Create dir + view**

```bash
cd frontend && mkdir -p views/auth && touch views/auth/__init__.py
```

```python
# views/auth/login_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.auth.login_vm import LoginVM, LoginForm
from views.theme.components import card, pill_button, section_header


def render(vm: LoginVM) -> None:
    with ui.column().classes("max-w-sm mx-auto mt-16 gap-4 w-full"):
        with card():
            section_header("Sign in to LinguAI")
            user_input = ui.input("Username").props("outlined dense").classes("w-full")
            pass_input = ui.input("Password", password=True, password_toggle_button=True) \
                .props("outlined dense").classes("w-full mt-2")

            # Bind inputs to model fields (manual because dataclass is frozen).
            def _set(field: str):
                def _cb(e) -> None:
                    vm.model = replace(vm.model, **{field: e.value or ""})
                return _cb
            user_input.on_value_change(_set("username"))
            pass_input.on_value_change(_set("password"))

            err = ui.label().classes("text-xs text-[var(--danger)] mt-2") \
                .bind_text_from(vm, "model", backward=lambda m: m.error)

            btn = pill_button("Sign in", variant="primary",
                               on_click=vm.login_command.execute_async)
            btn.bind_enabled_from(vm, "model", backward=lambda m: bool(m.username and m.password and not m.in_flight))
            btn.classes("w-full mt-3")

        with ui.row().classes("justify-center w-full text-xs text-[var(--text-2)] gap-1"):
            ui.label("New here?")
            ui.link("Create an account", "/register").classes("text-[var(--brand)]")
```

- [ ] **Step 2: Replace the `login_panel.render` call in `views/app_shell.py`**

Open `frontend/views/app_shell.py` and modify the `_rerender` function. Change:

```python
if not shell.session.model.is_authenticated:
    _login_panel.render(shell)
    return
```

to:

```python
if not shell.session.model.is_authenticated:
    from viewmodels.auth.login_vm import LoginVM
    from views.auth.login_view import render as render_login
    if not hasattr(shell, "_login_vm"):
        shell._login_vm = LoginVM(shell.message_hub, shell.dispatcher, shell.session, shell.notifications)
    render_login(shell._login_vm)
    return
```

(Lazy-construct LoginVM on the shell to keep DI minimal — we don't want every authenticated session to carry a login VM.)

- [ ] **Step 3: Delete the old `login_panel.py`**

```bash
git rm frontend/views/shell/login_panel.py
```

Remove the corresponding import line in `frontend/views/app_shell.py`.

- [ ] **Step 4: Boot, log in with a valid backend user**

```bash
docker compose up -d frontend backend db
open "http://localhost:${FRONTEND_PORT}"
```

Expected: enter creds, click "Sign in", shell content slot rerenders (still empty / placeholder Home).

- [ ] **Step 5: Commit**

```bash
git add frontend/views/auth frontend/views/app_shell.py
git rm frontend/views/shell/login_panel.py
git commit -m "feat(views/auth): LoginView wired into app shell content slot"
```

---

## Task 2.4: Persist `UserSession` to `app.storage.user`

**Files:**
- Modify: `frontend/viewmodels/shell/user_session_vm.py` (no — keep it pure)
- Modify: `frontend/main.py` (already rehydrates; verify writeback)
- Modify: `frontend/views/app_shell.py` (subscribe to session changes; write to storage)

Strict rule: VMs don't know about `app.storage.user`. The View layer subscribes to `session.model_changed` and writes through to storage.

- [ ] **Step 1: Add a session-persistence subscriber in `app_shell.py`**

Insert near the top of `mount(shell)`:

```python
def _persist_session(_) -> None:
    s = shell.session.model
    if s.token:
        app.storage.user["auth_token"] = s.token
        app.storage.user["username"] = s.username
    else:
        app.storage.user.pop("auth_token", None)
        app.storage.user.pop("username", None)

shell.session.model_changed.subscribe(_persist_session)
```

- [ ] **Step 2: Boot, log in, reload page**

```bash
docker compose restart frontend
open "http://localhost:${FRONTEND_PORT}"
```

Log in, then hard-reload the browser. Expected: still logged in (session rehydrated from cookie).

- [ ] **Step 3: Commit**

```bash
git add frontend/views/app_shell.py
git commit -m "feat(app_shell): persist UserSession token to app.storage.user across reloads"
```

---

## Task 2.5: Build `viewmodels/auth/register_vm.py` (wizard)

**Files:**
- Create: `frontend/viewmodels/auth/register_vm.py`
- Create: `frontend/viewmodels/auth/register_steps.py` (the three step VMs)
- Test: `frontend/tests/viewmodels/auth/test_register_vm.py`

Three steps:
1. **Account** — username, password, confirm-password, email
2. **Profile** — preferred name, first/last name
3. **Languages** — native language + at least one learning language

- [ ] **Step 1: Write the step VMs**

`frontend/viewmodels/auth/register_steps.py`:

```python
from __future__ import annotations
from dataclasses import dataclass, replace

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


@dataclass(frozen=True)
class AccountStep:
    username: str = ""
    password: str = ""
    confirm: str = ""
    email: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.username) and bool(self.email) \
               and len(self.password) >= 6 and self.password == self.confirm


@dataclass(frozen=True)
class ProfileStep:
    preferred_name: str = ""
    first_name: str = ""
    last_name: str = ""

    @property
    def is_valid(self) -> bool:
        return bool(self.first_name)  # other fields optional


@dataclass(frozen=True)
class LanguagesStep:
    native: str = ""
    learning: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return bool(self.native) and len(self.learning) >= 1


class AccountStepVM(ComponentVMOf[AccountStep]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="register-step-account", services=(hub, dispatcher), model=AccountStep())


class ProfileStepVM(ComponentVMOf[ProfileStep]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="register-step-profile", services=(hub, dispatcher), model=ProfileStep())


class LanguagesStepVM(ComponentVMOf[LanguagesStep]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="register-step-languages", services=(hub, dispatcher), model=LanguagesStep())
```

- [ ] **Step 2: Write `register_vm.py` using `AggregateVM3`**

```python
# viewmodels/auth/register_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace

from vmx.components import AggregateVM3
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from models.services.user_service import UserService
from viewmodels.auth.register_steps import (
    AccountStepVM, ProfileStepVM, LanguagesStepVM,
)
from viewmodels.shell.notification_center_vm import NotificationCenterVM


@dataclass
class RegisterState:
    current_step: int = 0   # 0=account, 1=profile, 2=languages
    in_flight: bool = False
    error: str = ""


class RegisterVM(AggregateVM3[AccountStepVM, ProfileStepVM, LanguagesStepVM]):
    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        user_svc: UserService,
        notifications: NotificationCenterVM,
    ) -> None:
        super().__init__(
            name="register",
            services=(hub, dispatcher),
            first=AccountStepVM(hub, dispatcher),
            second=ProfileStepVM(hub, dispatcher),
            third=LanguagesStepVM(hub, dispatcher),
        )
        self._user_svc = user_svc
        self._notify = notifications
        self.state = RegisterState()

        self.next_command = RelayCommand(execute=self._next, can_execute=self._can_next)
        self.back_command = RelayCommand(execute=self._back, can_execute=lambda: self.state.current_step > 0)
        self.submit_command = RelayCommand(execute=self._submit, can_execute=self._can_submit)

    @property
    def account(self) -> AccountStepVM: return self.first
    @property
    def profile(self) -> ProfileStepVM: return self.second
    @property
    def languages(self) -> LanguagesStepVM: return self.third

    def _current_valid(self) -> bool:
        return [self.account.model.is_valid, self.profile.model.is_valid, self.languages.model.is_valid][self.state.current_step]

    def _can_next(self) -> bool:
        return self.state.current_step < 2 and self._current_valid()

    def _can_submit(self) -> bool:
        return self.state.current_step == 2 and self._current_valid() and not self.state.in_flight

    def _next(self) -> None:
        self.state = replace(self.state, current_step=self.state.current_step + 1)

    def _back(self) -> None:
        self.state = replace(self.state, current_step=self.state.current_step - 1)

    async def _submit(self) -> None:
        self.state = replace(self.state, in_flight=True, error="")
        try:
            await self._user_svc.create_user(
                account=self.account.model,
                profile=self.profile.model,
                languages=self.languages.model,
            )
            self._notify.push_success("Account created. Please sign in.")
            # Caller (view) navigates back to /
        except Exception as e:
            self.state = replace(self.state, in_flight=False, error=f"Registration failed: {e}")
```

(`UserService.create_user` doesn't exist yet with this signature — Task 4.x fully reworks the user service. For Phase 2, add a thin `create_user` wrapper that calls the existing endpoint with a `UserCreate` schema. Find the current call site in `frontend/components/register.py` and mirror its payload.)

- [ ] **Step 3: Add `UserService.create_user` shim**

Open `frontend/models/services/user_service.py`. The existing class is sync-blocking. Add (don't replace yet) an async method:

```python
import httpx
from models.schemas.user import UserCreate

class UserService:  # existing class
    ...

    @classmethod
    async def create_user_async(cls, http: httpx.AsyncClient, payload: UserCreate) -> dict:
        r = await http.post("/users", json=payload.model_dump())
        r.raise_for_status()
        return r.json()
```

Then in `register_vm.py` `_submit`, replace the `await self._user_svc.create_user(...)` call with the inline shim wiring — for now construct a `UserCreate` from the three step models and call `UserService.create_user_async(http_client, payload)`. We finalize this in Phase 4 when the full async UserService lands.

(If `UserCreate` schema mismatches our three-step decomposition, write a small mapper function `_to_user_create(account, profile, languages) -> UserCreate` at top of `register_vm.py`.)

- [ ] **Step 4: Write a minimal RegisterVM step test**

`frontend/tests/viewmodels/auth/test_register_vm.py`:

```python
import pytest
from dataclasses import replace
from unittest.mock import AsyncMock

from vmx.services import MessageHub, RxDispatcher

from viewmodels.auth.register_vm import RegisterVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.auth.register_steps import AccountStep


@pytest.fixture
def vm():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    user_svc = AsyncMock()
    notifications = NotificationCenterVM(hub, disp)
    return RegisterVM(hub, disp, user_svc, notifications)


def test_next_disabled_until_account_valid(vm):
    assert not vm.next_command.can_execute()
    vm.account.model = AccountStep(username="alice", password="secret1", confirm="secret1", email="a@b.c")
    assert vm.next_command.can_execute()
    vm.next_command.execute()
    assert vm.state.current_step == 1
```

- [ ] **Step 5: Run, expect green**

```bash
cd frontend && poetry run pytest tests/viewmodels/auth/test_register_vm.py -q
```

Expected: 1 passed.

- [ ] **Step 6: Commit**

```bash
git add frontend/viewmodels/auth/register_vm.py frontend/viewmodels/auth/register_steps.py \
        frontend/models/services/user_service.py frontend/tests/viewmodels/auth/test_register_vm.py
git commit -m "feat(viewmodels): RegisterVM wizard (AggregateVM3 of step VMs)"
```

---

## Task 2.6: Build `views/auth/register_view.py`

**Files:**
- Create: `frontend/views/auth/register_view.py`
- Modify: `frontend/main.py` (add `@ui.page("/register")` route)

- [ ] **Step 1: Write the view**

```python
# views/auth/register_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.auth.register_vm import RegisterVM
from views.theme.components import card, pill_button, section_header


def render(vm: RegisterVM) -> None:
    with ui.column().classes("max-w-md mx-auto mt-12 gap-3 w-full"):
        with card():
            section_header("Create your LinguAI account")
            ui.label().bind_text_from(vm, "state", backward=lambda s: f"Step {s.current_step+1} of 3") \
                .classes("text-xs text-[var(--text-3)] uppercase tracking-wider")

            stepper = ui.stepper().props("flat header-nav").classes("w-full mt-2")
            with stepper:
                with ui.step("Account"):
                    _account_inputs(vm)
                with ui.step("Profile"):
                    _profile_inputs(vm)
                with ui.step("Languages"):
                    _language_inputs(vm)

            # Bind stepper.value to current_step
            stepper.bind_value_from(vm, "state", backward=lambda s: ["Account", "Profile", "Languages"][s.current_step])

            ui.label().bind_text_from(vm, "state", backward=lambda s: s.error) \
                .classes("text-xs text-[var(--danger)] mt-2")

            with ui.row().classes("gap-2 justify-end mt-3 w-full"):
                back = pill_button("Back", on_click=vm.back_command.execute)
                back.bind_enabled_from(vm, "state", backward=lambda s: s.current_step > 0)

                next_btn = pill_button("Next", variant="primary", on_click=vm.next_command.execute)
                next_btn.bind_enabled_from(vm, "state", backward=lambda s: s.current_step < 2 and _is_step_valid(vm, s.current_step))
                next_btn.bind_visibility_from(vm, "state", backward=lambda s: s.current_step < 2)

                submit = pill_button("Create account", variant="primary", on_click=vm.submit_command.execute_async)
                submit.bind_enabled_from(vm, "state", backward=lambda s: s.current_step == 2 and _is_step_valid(vm, 2) and not s.in_flight)
                submit.bind_visibility_from(vm, "state", backward=lambda s: s.current_step == 2)


def _is_step_valid(vm: RegisterVM, idx: int) -> bool:
    return [vm.account.model.is_valid, vm.profile.model.is_valid, vm.languages.model.is_valid][idx]


def _account_inputs(vm: RegisterVM) -> None:
    a = vm.account
    ui.input("Username").props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: setattr(a, "model", replace(a.model, username=e.value or "")))
    ui.input("Email").props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(a, "model", replace(a.model, email=e.value or "")))
    ui.input("Password", password=True, password_toggle_button=True).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(a, "model", replace(a.model, password=e.value or "")))
    ui.input("Confirm password", password=True).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(a, "model", replace(a.model, confirm=e.value or "")))


def _profile_inputs(vm: RegisterVM) -> None:
    p = vm.profile
    ui.input("Preferred name (optional)").props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: setattr(p, "model", replace(p.model, preferred_name=e.value or "")))
    ui.input("First name").props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(p, "model", replace(p.model, first_name=e.value or "")))
    ui.input("Last name (optional)").props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(p, "model", replace(p.model, last_name=e.value or "")))


def _language_inputs(vm: RegisterVM) -> None:
    L = vm.languages
    # Hard-coded list of common languages for the wizard; richer list comes from LanguageService in Phase 4.
    languages = ["Spanish", "French", "German", "Italian", "Japanese", "Mandarin", "Portuguese", "English"]
    ui.select(languages, label="Native language").props("outlined dense").classes("w-full") \
        .on_value_change(lambda e: setattr(L, "model", replace(L.model, native=e.value or "")))
    ui.select(languages, label="Languages to learn", multiple=True).props("outlined dense").classes("w-full mt-2") \
        .on_value_change(lambda e: setattr(L, "model", replace(L.model, learning=tuple(e.value or ()))))
```

- [ ] **Step 2: Register `/register` route in `main.py`**

Append to `frontend/main.py`:

```python
@ui.page("/register")
def register_page() -> None:
    from viewmodels.auth.register_vm import RegisterVM
    from models.services.user_service import UserService
    from viewmodels.shell.notification_center_vm import NotificationCenterVM
    from views.auth.register_view import render as render_register
    from views.theme.palette import apply_theme
    from views.theme.typography import install_fonts
    install_fonts()
    apply_theme(app.storage.user.get("theme_mode", "system"))

    notifications = NotificationCenterVM(HUB, DISPATCHER)
    # UserService is class-method based for now; pass a tiny adapter so RegisterVM.submit can call it.
    class _UserSvcAdapter:
        async def create_user(self, *, account, profile, languages) -> dict:
            from models.schemas.user import UserCreate
            payload = UserCreate(
                username=account.username, email=account.email, password=account.password,
                first_name=profile.first_name, last_name=profile.last_name,
                preferred_name=profile.preferred_name,
                # the existing UserCreate schema likely needs more fields — fill from defaults
            )
            return await UserService.create_user_async(HTTP, payload)
    vm = RegisterVM(HUB, DISPATCHER, _UserSvcAdapter(), notifications)
    render_register(vm)
```

- [ ] **Step 3: Boot, register a new user**

```bash
docker compose up -d frontend backend db
open "http://localhost:${FRONTEND_PORT}/register"
```

Expected: three-step stepper; next disabled until each step valid; submit creates user; toast notifies.

- [ ] **Step 4: Commit**

```bash
git add frontend/views/auth/register_view.py frontend/main.py
git commit -m "feat(views/auth): three-step RegisterView wizard"
```

---

## Task 2.7: Build `viewmodels/home/home_vm.py` and remove placeholder

**Files:**
- Create: `frontend/viewmodels/home/__init__.py`
- Create: `frontend/viewmodels/home/home_vm.py`
- Modify: `frontend/core/di.py` (replace `HomePagePlaceholder` with real `HomeVM`)
- Test: `frontend/tests/viewmodels/home/test_home_vm.py`

- [ ] **Step 1: Write `home_vm.py`**

```python
# viewmodels/home/home_vm.py
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional

from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.user_session_vm import UserSessionVM


@dataclass(frozen=True)
class SkillCard:
    language: str
    code_iso: str  # "ES", "FR", "JA"
    level: str     # "B2 · Intermediate"
    percent_to_next: int
    delta_label: str  # "↑ 4%", "+12 xp", "new"


@dataclass(frozen=True)
class HomeModel:
    greeting_time: str = "Friday morning"      # populated by view from `datetime`
    languages_in_progress: int = 0
    last_session_label: str = "(none yet)"
    skill_cards: tuple[SkillCard, ...] = field(default_factory=tuple)
    recent_activity: tuple[dict, ...] = field(default_factory=tuple)


class HomeVM(PageVM):
    route = "home"

    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, session: UserSessionVM) -> None:
        super().__init__(name="home", services=(hub, dispatcher))
        self._session = session
        self.model = HomeModel()
        # Re-derive on session change (e.g., user profile loads).
        session.model_changed.subscribe(lambda _: self._refresh_from_session())
        self._refresh_from_session()

    def _refresh_from_session(self) -> None:
        # Real wiring (skill cards from user_skill domain) lands in Phase 4 when ProfileVM exists.
        # For now we display a placeholder welcome row keyed off session.
        self.model = HomeModel(
            greeting_time=self.model.greeting_time,
            languages_in_progress=0,
            last_session_label="(connect skill data in phase 4)",
            skill_cards=(),
            recent_activity=(),
        )
```

- [ ] **Step 2: Replace `HomePagePlaceholder` in `core/di.py`**

In `frontend/core/di.py`, remove `class HomePagePlaceholder(...)` and its import; change `build_app_shell(...)` to:

```python
from viewmodels.home.home_vm import HomeVM
...
def build_app_shell(cfg, hub, dispatcher, http, auth_svc) -> AppShellVM:
    notifications = NotificationCenterVM(hub, dispatcher)
    settings = SettingsVM(hub, dispatcher)
    navigation = NavigationVM(hub, dispatcher)
    session = UserSessionVM(hub, dispatcher, auth_svc, http)

    home = HomeVM(hub, dispatcher, session)
    pages = [home]

    return AppShellVM(
        hub, dispatcher,
        session=session, settings=settings, navigation=navigation, notifications=notifications,
        pages=pages,
    )
```

- [ ] **Step 3: Test HomeVM has the right route**

`frontend/tests/viewmodels/home/test_home_vm.py`:

```python
import pytest
from unittest.mock import AsyncMock
import httpx

from vmx.services import MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.home.home_vm import HomeVM


@pytest.fixture
def home():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    auth = AsyncMock()
    http = httpx.AsyncClient(base_url="http://test")
    session = UserSessionVM(hub, disp, auth, http)
    return HomeVM(hub, disp, session)


def test_home_route(home):
    assert home.route == "home"


def test_home_model_is_initialized(home):
    assert home.model.last_session_label
```

- [ ] **Step 4: Run**

```bash
cd frontend && poetry run pytest tests/viewmodels/home -q
```

Expected: 2 passed.

- [ ] **Step 5: Commit**

```bash
git add frontend/viewmodels/home frontend/tests/viewmodels/home frontend/core/di.py
git commit -m "feat(viewmodels): HomeVM replaces placeholder in DI root"
```

---

## Task 2.8: Build `views/home/home_view.py` (matches polish-v2 dashboard)

**Files:**
- Create: `frontend/views/home/__init__.py`
- Create: `frontend/views/home/home_view.py`
- Modify: `frontend/views/app_shell.py` (register the home renderer)

- [ ] **Step 1: Write the view**

```python
# views/home/home_view.py
from datetime import datetime
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from views.theme.components import card, pill_button, section_header, chip


def _greeting() -> str:
    h = datetime.now().hour
    return ("Friday morning" if 5 <= h < 12 else
            "Friday afternoon" if 12 <= h < 18 else
            "Friday evening")  # day-of-week could be wired similarly


def render(shell: AppShellVM) -> None:
    home = next(p for p in shell.children if p.route == "home")
    session = shell.session

    # Greeting band
    with ui.row().classes("items-end justify-between mb-6 w-full"):
        with ui.column().classes("gap-1"):
            ui.label(_greeting()).classes("text-xs text-[var(--text-3)]")
            ui.label().bind_text_from(session, "model", backward=lambda s: f"Welcome back, {s.username or 'friend'}.") \
                .classes("text-2xl font-semibold tracking-tight")
            ui.label().bind_text_from(home, "model",
                                       backward=lambda m: f"{m.languages_in_progress} language(s) in progress · {m.last_session_label}") \
                .classes("text-sm text-[var(--text-2)]")
        pill_button("Start practice", variant="primary",
                    on_click=lambda: shell.navigation.go("chat"))

    # Skill cards row
    with ui.row().classes("gap-3 w-full") as skill_row:
        def _render_skills(_=None) -> None:
            skill_row.clear()
            with skill_row:
                cards = home.model.skill_cards
                if not cards:
                    with card().classes("w-full"):
                        ui.label("No skill data yet. Run an assessment to populate this dashboard.") \
                            .classes("text-sm text-[var(--text-2)]")
                    return
                for s in cards:
                    with card().classes("flex-1"):
                        with ui.row().classes("items-center gap-3"):
                            ui.label(s.code_iso).classes("w-7 h-7 rounded-md text-white text-xs font-bold flex items-center justify-center") \
                                .style(f"background:linear-gradient(135deg,#EF4444,#F59E0B)")
                            with ui.column().classes("gap-0"):
                                ui.label(s.language).classes("text-sm font-semibold")
                                ui.label(s.level).classes("text-xs text-[var(--text-3)]")
                        # progress
                        ui.linear_progress(s.percent_to_next / 100, show_value=False).props("color=primary instant-feedback") \
                            .classes("mt-3 h-1.5")
                        with ui.row().classes("justify-between mt-2"):
                            ui.label(f"{s.percent_to_next}% to next level").classes("text-xs text-[var(--text-3)]")
                            chip(s.delta_label, tone="success")
        home.model_changed.subscribe(_render_skills)
        _render_skills()

    # Two-column: quick actions + recent activity
    with ui.row().classes("gap-3 mt-6 w-full"):
        with ui.column().classes("flex-1 gap-2"):
            section_header("Quick actions", subtitle="curated for you")
            with ui.row().classes("gap-2 w-full"):
                with card().classes("flex-1").on("click", lambda: shell.navigation.go("chat")):
                    ui.icon("chat_bubble").classes("text-[var(--brand)]")
                    ui.label("Resume conversation").classes("font-semibold")
                with card().classes("flex-1").on("click", lambda: shell.navigation.go("polyglot_puzzle")):
                    ui.icon("extension").classes("text-[var(--brand)]")
                    ui.label("Today's polyglot puzzle").classes("font-semibold")
            with ui.row().classes("gap-2 w-full"):
                with card().classes("flex-1").on("click", lambda: shell.navigation.go("content_gen")):
                    ui.icon("auto_stories").classes("text-[var(--brand)]")
                    ui.label("Read an article").classes("font-semibold")
                with card().classes("flex-1").on("click", lambda: shell.navigation.go("rewrite_content")):
                    ui.icon("edit").classes("text-[var(--brand)]")
                    ui.label("Rewrite a passage").classes("font-semibold")
        with ui.column().classes("w-80 gap-2"):
            section_header("Recent activity")
            with card():
                ui.label("(activity feed wires up in phase 4)").classes("text-sm text-[var(--text-3)]")
```

- [ ] **Step 2: Register the renderer in `views/app_shell.py`**

At the top of `app_shell.py`, after `PAGE_RENDERERS = {}`:

```python
from views.home.home_view import render as render_home
PAGE_RENDERERS["home"] = render_home
```

- [ ] **Step 3: Boot, log in, view home**

```bash
docker compose restart frontend
open "http://localhost:${FRONTEND_PORT}"
```

Expected: after login, home dashboard renders with greeting band, empty skill cards placeholder, quick action cards (clicking navigates between routes — content slots will be empty for non-home routes until later phases).

- [ ] **Step 4: Commit**

```bash
git add frontend/views/home frontend/views/app_shell.py
git commit -m "feat(views/home): polish-v2 dashboard (skill cards stub, quick actions wired)"
```

---

## Task 2.9: Phase 2 gate — auth + home smoke

- [ ] **Step 1: Manual smoke**

1. Open `http://localhost:${FRONTEND_PORT}` — login form appears.
2. Click "Create an account" — register wizard works through 3 steps; clicking back/next respects validity gates.
3. Submit registration — toast confirms.
4. Sign in with the just-created user — home dashboard renders.
5. Click "Start practice" — navigation changes to `chat` (content empty placeholder).
6. Click theme toggle — light → dark → system → light cycles, persists across reload.
7. Click avatar / find logout (logout flow wired in shell? if not, add a logout `ui.menu_item` to header in this task as a 7a sub-step).
8. After logout, login form reappears; session removed from cookie.

- [ ] **Step 1a: If logout isn't yet wired into the header, add it**

In `frontend/views/shell/header.py`, replace the avatar block with a clickable menu:

```python
async def _logout(_=None) -> None:
    await shell.session.log_out()

with ui.row().classes("items-center gap-2 pl-2 border-l border-white/5"):
    avatar = ui.label().bind_text_from(shell.session, "model",
                                       backward=lambda m: (m.username or "?")[:2].upper()) \
        .classes("w-7 h-7 rounded-full bg-violet-500 text-white text-xs font-semibold "
                 "flex items-center justify-center cursor-pointer")
    with ui.menu().props("auto-close").parent(avatar):
        ui.menu_item("Sign out", on_click=_logout)
```

Then commit the change as part of this gate.

- [ ] **Step 2: Run full test/lint suite**

```bash
cd frontend
poetry run pytest -q
poetry run lint-imports
poetry run mypy --strict models viewmodels core views/theme
```

Expected all green.

- [ ] **Step 3: Phase 2 gate commit**

```bash
git add frontend/views/shell/header.py
git commit -m "feat(shell): user-menu logout from header avatar"
git commit --allow-empty -m "chore: phase 2 gate — register/login/home/logout end-to-end"
```

---

# Phase 3 — Polyglot Puzzle

**Goal of this phase:** the hardest VM shape (composite-of-children + aggregate + derived-properties + multiple commands + Plotly figure). The current `frontend/components/polyglot_puzzle.py` has a hand-rolled VM — we delete it after this phase. Doing this third deliberately stress-tests the pattern before phases 4–6 rely on it at scale.

**Phase 3 gate:** real working puzzle (generate → enter 2+ attempts → submit → embeddings 2D/3D plot renders); old `PolyglotPuzzleViewModel` deleted; VM unit test covers happy path and a derived-property edge case.

---

## Task 3.1: Refactor `polyglot_puzzle_service` + `embeddings_service` + `language_service` + `llm_service` to async httpx

**Files:**
- Modify: `frontend/models/services/polyglot_puzzle_service.py`
- Modify: `frontend/models/services/embeddings_service.py`
- Modify: `frontend/models/services/language_service.py`
- Modify: `frontend/models/services/llm_service.py`
- Test: `frontend/tests/models/services/test_polyglot_puzzle_service.py`

Current services use class-method patterns with `httpx` calls inside `async def` but also expose `_sync` shims. Refactor each to instance-based, constructor-injected `httpx.AsyncClient`. Keep the existing class-method signatures as thin wrappers around new instance methods *only if* a Streamlit caller still depends on them — Phase 7 will delete the wrappers along with the Streamlit code.

- [ ] **Step 1: Rewrite `polyglot_puzzle_service.py`**

```python
from __future__ import annotations
import httpx

from models.domain.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse


class PolyglotPuzzleService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def generate(self, request: PolyglotPuzzleRequest) -> PolyglotPuzzleResponse:
        r = await self._http.post("/polyglot-puzzle/generate", json=request.model_dump())
        r.raise_for_status()
        return PolyglotPuzzleResponse.model_validate(r.json())
```

Verify the path against the actual backend route (search `backend/routers/`). Adjust `/polyglot-puzzle/generate` if different.

- [ ] **Step 2: Rewrite `embeddings_service.py`**

```python
from __future__ import annotations
import httpx

from models.domain.embeddings import (
    EmbeddingsGetRequest, EmbeddingsGetResponse,
    EmbeddingsReduceRequest, EmbeddingsReduceResponse,
    EmbeddingsSimilaritiesRequest, EmbeddingsSimilaritiesResponse,
)


class EmbeddingsService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get(self, req: EmbeddingsGetRequest) -> EmbeddingsGetResponse:
        r = await self._http.post("/embeddings", json=req.model_dump()); r.raise_for_status()
        return EmbeddingsGetResponse.model_validate(r.json())

    async def reduce(self, req: EmbeddingsReduceRequest) -> EmbeddingsReduceResponse:
        r = await self._http.post("/embeddings/reduce", json=req.model_dump()); r.raise_for_status()
        return EmbeddingsReduceResponse.model_validate(r.json())

    async def similarities(self, req: EmbeddingsSimilaritiesRequest) -> EmbeddingsSimilaritiesResponse:
        r = await self._http.post("/embeddings/similarities", json=req.model_dump()); r.raise_for_status()
        return EmbeddingsSimilaritiesResponse.model_validate(r.json())
```

- [ ] **Step 3: Rewrite `language_service.py` + `llm_service.py`**

Mirror the same pattern. `LanguageService.list()` returns `list[Language]`; `LLMService.get_structured_content()` / `get_embeddings()` / `get_content()` / `get_vision()` are likely separate filtered endpoints — preserve the existing surface but make each `async` and take `http` in constructor. Delete `_sync` variants.

```python
# language_service.py
from __future__ import annotations
import httpx
from models.schemas.language import Language


class LanguageService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Language]:
        r = await self._http.get("/languages"); r.raise_for_status()
        return [Language.model_validate(x) for x in r.json()]

    async def get_by_name(self, name: str) -> Language:
        r = await self._http.get(f"/languages/{name}"); r.raise_for_status()
        return Language.model_validate(r.json())
```

```python
# llm_service.py
from __future__ import annotations
import httpx
from models.domain.llm import LLM


class LLMService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list_all(self) -> list[LLM]:
        r = await self._http.get("/llms"); r.raise_for_status()
        return [LLM.model_validate(x) for x in r.json()]

    async def get_structured_content(self) -> list[LLM]:
        return [m for m in await self.list_all() if "structured" in (m.capabilities or [])]

    async def get_embeddings(self) -> list[LLM]:
        return [m for m in await self.list_all() if "embeddings" in (m.capabilities or [])]

    async def get_content(self) -> list[LLM]:
        return [m for m in await self.list_all() if "content" in (m.capabilities or [])]

    async def get_vision(self) -> list[LLM]:
        return [m for m in await self.list_all() if "vision" in (m.capabilities or [])]
```

(If the backend's LLM schema doesn't have a `capabilities` field, look at the existing `LLMService` filtering logic in current code and copy its predicates.)

- [ ] **Step 4: Write a service test**

`frontend/tests/models/services/test_polyglot_puzzle_service.py`:

```python
import httpx
import pytest
import respx

from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.domain.polyglot_puzzle import PolyglotPuzzleRequest


@pytest.mark.asyncio
async def test_generate():
    async with httpx.AsyncClient(base_url="http://test") as http:
        with respx.mock() as router:
            router.post("http://test/polyglot-puzzle/generate").mock(
                return_value=httpx.Response(200, json={
                    "src_lang_question": "Hello",
                    "dst_lang_question": "Hola",
                })
            )
            svc = PolyglotPuzzleService(http)
            req = PolyglotPuzzleRequest(src_lang="English", dst_lang="Spanish",
                                        difficulty="Easy", llm_id="x", llm_temperature=0.0)
            r = await svc.generate(req)
            assert r.src_lang_question == "Hello"
```

(If the actual `PolyglotPuzzleResponse` schema has more required fields, add them to the test JSON.)

- [ ] **Step 5: Run + commit**

```bash
cd frontend && poetry run pytest tests/models/services -q
git add frontend/models/services/polyglot_puzzle_service.py \
        frontend/models/services/embeddings_service.py \
        frontend/models/services/language_service.py \
        frontend/models/services/llm_service.py \
        frontend/tests/models/services/test_polyglot_puzzle_service.py
git commit -m "refactor(services): async/instance-based puzzle/embeddings/language/llm services"
```

---

## Task 3.2: Enrich `models/domain/polyglot_puzzle.py`

**Files:**
- Modify: `frontend/models/domain/polyglot_puzzle.py`

Current file likely has `PolyglotPuzzleRequest` only. Add `PolyglotPuzzleResponse` + a top-level `PolyglotPuzzleModel` aggregate the VM holds.

- [ ] **Step 1: Inspect current contents and append/restructure**

```bash
cat frontend/models/domain/polyglot_puzzle.py
```

Decide whether to rewrite or extend. Below assumes a rewrite to make this canonical:

```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple
from pydantic import BaseModel


# --- wire DTOs (Pydantic) ---

class PolyglotPuzzleRequest(BaseModel):
    src_lang: str
    dst_lang: str
    difficulty: str
    llm_id: str
    llm_temperature: float = 0.0


class PolyglotPuzzleResponse(BaseModel):
    src_lang_question: str
    dst_lang_question: str
    # extend with any additional backend fields (hints, alternatives, etc.)


# --- VM-side aggregate model ---

@dataclass(frozen=True)
class PolyglotPuzzleModel:
    src_langs: Tuple[str, ...] = field(default_factory=tuple)
    dst_langs: Tuple[str, ...] = field(default_factory=tuple)
    difficulties: Tuple[str, ...] = ("Easy", "Medium", "Hard")
    request: Optional[PolyglotPuzzleRequest] = None
    response: Optional[PolyglotPuzzleResponse] = None
    embeddings_llm_id: Optional[str] = None

    @property
    def has_response(self) -> bool:
        return self.response is not None

    def with_response(self, r: PolyglotPuzzleResponse) -> "PolyglotPuzzleModel":
        return replace(self, response=r)

    def with_request(self, r: PolyglotPuzzleRequest) -> "PolyglotPuzzleModel":
        return replace(self, request=r)
```

If the existing module is imported by any *non-deleted* Streamlit page beyond polyglot, keep a compat shim re-exporting the old names. Otherwise rewrite freely.

- [ ] **Step 2: Verify imports still resolve**

```bash
cd frontend && poetry run python -c "from models.domain.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse, PolyglotPuzzleModel; print('ok')"
```

Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add frontend/models/domain/polyglot_puzzle.py
git commit -m "feat(models/domain): PolyglotPuzzleModel aggregate with derived has_response"
```

---

## Task 3.3: Build `viewmodels/polyglot_puzzle/attempt_vm.py`

**Files:**
- Create: `frontend/viewmodels/polyglot_puzzle/__init__.py`
- Create: `frontend/viewmodels/polyglot_puzzle/attempt_vm.py`

- [ ] **Step 1: Write the VM**

```bash
cd frontend && mkdir -p viewmodels/polyglot_puzzle tests/viewmodels/polyglot_puzzle
touch viewmodels/polyglot_puzzle/__init__.py tests/viewmodels/polyglot_puzzle/__init__.py
```

```python
# viewmodels/polyglot_puzzle/attempt_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


@dataclass(frozen=True)
class Attempt:
    text: str = ""
    similarity: Optional[float] = None  # populated after submit

    def with_text(self, t: str) -> "Attempt":
        return replace(self, text=t)

    def with_similarity(self, s: float) -> "Attempt":
        return replace(self, similarity=s)


class AttemptVM(ComponentVMOf[Attempt]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, name: str = "attempt") -> None:
        super().__init__(name=name, services=(hub, dispatcher), model=Attempt())
```

- [ ] **Step 2: Commit**

```bash
git add frontend/viewmodels/polyglot_puzzle/attempt_vm.py frontend/viewmodels/polyglot_puzzle/__init__.py
git commit -m "feat(viewmodels): AttemptVM (ComponentVMOf[Attempt])"
```

---

## Task 3.4: Build `viewmodels/polyglot_puzzle/embeddings_view_vm.py`

**Files:**
- Create: `frontend/viewmodels/polyglot_puzzle/embeddings_view_vm.py`

Aggregate VM that holds the 2D/3D-reduced embeddings data + current view mode. The View renders `ui.plotly` against `data_2d` or `data_3d`.

- [ ] **Step 1: Write the VM**

```python
# viewmodels/polyglot_puzzle/embeddings_view_vm.py
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Literal, Optional, Tuple, List

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


ViewMode = Literal["2d", "3d"]


@dataclass(frozen=True)
class EmbeddingsView:
    mode: ViewMode = "2d"
    labels: Tuple[str, ...] = field(default_factory=tuple)  # ["ideal", "attempt 1", "attempt 2", …]
    points_2d: Tuple[Tuple[float, float], ...] = field(default_factory=tuple)
    points_3d: Tuple[Tuple[float, float, float], ...] = field(default_factory=tuple)
    similarities: Tuple[float, ...] = field(default_factory=tuple)


class EmbeddingsViewVM(ComponentVMOf[EmbeddingsView]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="embeddings-view", services=(hub, dispatcher), model=EmbeddingsView())

    def set_mode(self, mode: ViewMode) -> None:
        if mode != self.model.mode:
            self.model = replace(self.model, mode=mode)

    def update(self, labels: List[str], points_2d, points_3d, similarities: List[float]) -> None:
        self.model = replace(
            self.model,
            labels=tuple(labels),
            points_2d=tuple((float(x), float(y)) for x, y in points_2d),
            points_3d=tuple((float(x), float(y), float(z)) for x, y, z in points_3d),
            similarities=tuple(float(s) for s in similarities),
        )

    def clear(self) -> None:
        self.model = EmbeddingsView(mode=self.model.mode)
```

- [ ] **Step 2: Commit**

```bash
git add frontend/viewmodels/polyglot_puzzle/embeddings_view_vm.py
git commit -m "feat(viewmodels): EmbeddingsViewVM aggregate (2D/3D points + similarities)"
```

---

## Task 3.5: Build `viewmodels/polyglot_puzzle/polyglot_puzzle_vm.py`

**Files:**
- Create: `frontend/viewmodels/polyglot_puzzle/polyglot_puzzle_vm.py`
- Test: `frontend/tests/viewmodels/polyglot_puzzle/test_polyglot_puzzle_vm.py`

Composite. Children are `AttemptVM`s; holds `PolyglotPuzzleModel` as its own model; aggregates `EmbeddingsViewVM`. Per spec open question #9: we use `CompositeVM[AttemptVM]` + model-as-attribute pattern (the most idiomatic primitive form).

- [ ] **Step 1: Write the VM**

```python
# viewmodels/polyglot_puzzle/polyglot_puzzle_vm.py
from __future__ import annotations
from dataclasses import replace
from typing import List, Optional

from vmx.components import CompositeVM
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.polyglot_puzzle.attempt_vm import AttemptVM, Attempt
from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.domain.polyglot_puzzle import (
    PolyglotPuzzleModel, PolyglotPuzzleRequest, PolyglotPuzzleResponse,
)
from models.schemas.language import Language
from models.domain.llm import LLM
from models.domain.embeddings import (
    EmbeddingsGetRequest, EmbeddingsReduceRequest, EmbeddingsSimilaritiesRequest,
)
from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.services.embeddings_service import EmbeddingsService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService


class PolyglotPuzzleVM(CompositeVM[AttemptVM], PageVM):  # type: ignore[misc]
    """
    Multiple-inheritance: CompositeVM provides children mechanics, PageVM provides the .route marker.
    If the quickref shows VMx's CompositeVM is not MI-friendly, instead make this a CompositeVM only and
    set `route = "polyglot_puzzle"` as a class attribute directly (PageVM is just a marker class).
    """
    route = "polyglot_puzzle"

    MIN_ATTEMPTS = 2
    MAX_ATTEMPTS = 10

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        puzzle_svc: PolyglotPuzzleService,
        embeddings_svc: EmbeddingsService,
        language_svc: LanguageService,
        llm_svc: LLMService,
        notifications: NotificationCenterVM,
        embeddings_vm: EmbeddingsViewVM,
    ) -> None:
        super().__init__(name="polyglot-puzzle", services=(hub, dispatcher))
        self._puzzle = puzzle_svc
        self._emb = embeddings_svc
        self._lang = language_svc
        self._llm = llm_svc
        self._notify = notifications
        self.embeddings = embeddings_vm
        self.model = PolyglotPuzzleModel()
        self._busy = False

        # start with two empty attempts (matches the legacy seed)
        for i in range(self.MIN_ATTEMPTS):
            self.add_child(AttemptVM(hub, dispatcher, name=f"attempt-{i}"))

        self.load_options_command = RelayCommand(execute=self._load_options)
        self.generate_command = RelayCommand(execute=self._generate, can_execute=self._can_generate)
        self.add_attempt_command = RelayCommand(execute=self._add_attempt, can_execute=self._can_add_attempt)
        self.submit_command = RelayCommand(execute=self._submit, can_execute=self._can_submit)
        self.clear_command = RelayCommand(execute=self._clear)

    # ---- predicates ----

    def _can_generate(self) -> bool:
        return self.model.request is not None and not self._busy

    def _can_add_attempt(self) -> bool:
        return (
            self.model.has_response
            and self.MIN_ATTEMPTS <= len(self.children) < self.MAX_ATTEMPTS
            and all(c.model.text.strip() for c in self.children)
        )

    def _can_submit(self) -> bool:
        return (
            self.model.has_response
            and len(self.children) >= self.MIN_ATTEMPTS
            and all(c.model.text.strip() for c in self.children)
            and not self._busy
        )

    # ---- commands ----

    async def _load_options(self) -> None:
        languages = [L.language_name for L in await self._lang.list()]
        structured = await self._llm.get_structured_content()
        embeddings = await self._llm.get_embeddings()
        if not (languages and structured and embeddings):
            self._notify.push_error("Could not load languages or LLMs from backend.")
            return
        req = PolyglotPuzzleRequest(
            src_lang=languages[0], dst_lang=languages[0],
            difficulty="Easy", llm_id=structured[0].id, llm_temperature=0.0,
        )
        self.model = replace(
            self.model,
            src_langs=tuple(languages), dst_langs=tuple(languages),
            request=req, embeddings_llm_id=embeddings[0].id,
        )

    async def _generate(self) -> None:
        assert self.model.request is not None
        self._busy = True
        try:
            self._clear_children()
            for i in range(self.MIN_ATTEMPTS):
                self.add_child(AttemptVM(self.message_hub, self.dispatcher, name=f"attempt-{i}"))
            response = await self._puzzle.generate(self.model.request)
            self.model = self.model.with_response(response)
            self.embeddings.clear()
        finally:
            self._busy = False

    def _add_attempt(self) -> None:
        self.add_child(AttemptVM(self.message_hub, self.dispatcher, name=f"attempt-{len(self.children)}"))

    async def _submit(self) -> None:
        assert self.model.response is not None and self.model.embeddings_llm_id is not None
        self._busy = True
        try:
            texts: List[str] = [self.model.response.dst_lang_question] + [c.model.text for c in self.children]
            # 1. embed
            embeds = await self._emb.get(EmbeddingsGetRequest(texts=texts, llm_id=self.model.embeddings_llm_id))
            # 2. similarities (ideal vs each attempt)
            sims = await self._emb.similarities(EmbeddingsSimilaritiesRequest(embeddings=embeds.embeddings))
            # sims.scores is expected shape: [(ideal,a1),(ideal,a2),...] — adjust per backend
            scores: List[float] = list(sims.scores) if hasattr(sims, "scores") else list(getattr(sims, "similarities", []))
            attempts_scores = scores[1:] if len(scores) > len(self.children) else scores
            for child, score in zip(self.children, attempts_scores):
                child.model = child.model.with_similarity(score)
            # 3. reduce 2D + 3D
            r2d = await self._emb.reduce(EmbeddingsReduceRequest(embeddings=embeds.embeddings, dims=2))
            r3d = await self._emb.reduce(EmbeddingsReduceRequest(embeddings=embeds.embeddings, dims=3))
            labels = ["ideal"] + [f"attempt {i+1}" for i in range(len(self.children))]
            self.embeddings.update(labels, getattr(r2d, "points", r2d), getattr(r3d, "points", r3d), attempts_scores)
        finally:
            self._busy = False

    def _clear(self) -> None:
        self._clear_children()
        for i in range(self.MIN_ATTEMPTS):
            self.add_child(AttemptVM(self.message_hub, self.dispatcher, name=f"attempt-{i}"))
        self.model = PolyglotPuzzleModel(
            src_langs=self.model.src_langs, dst_langs=self.model.dst_langs,
            request=self.model.request, embeddings_llm_id=self.model.embeddings_llm_id,
        )
        self.embeddings.clear()

    def _clear_children(self) -> None:
        # Iterate over a copy because remove_child mutates the list.
        for c in list(self.children):
            self.remove_child(c)
```

(Embeddings response field names — `embeddings`, `scores`, `points`, `similarities` — vary by backend. Inspect actual responses and adjust the four `getattr` / attribute reads accordingly. Add small `# NOTE:` lines where you do.)

- [ ] **Step 2: Write VM unit tests**

`frontend/tests/viewmodels/polyglot_puzzle/test_polyglot_puzzle_vm.py`:

```python
import pytest
from unittest.mock import AsyncMock
from dataclasses import replace

from vmx.services import MessageHub, RxDispatcher

from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import PolyglotPuzzleVM
from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.domain.polyglot_puzzle import PolyglotPuzzleRequest, PolyglotPuzzleResponse


@pytest.fixture
def vm():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    puzzle, emb, lang, llm, notif, ev = (
        AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock(),
        NotificationCenterVM(hub, disp), EmbeddingsViewVM(hub, disp),
    )
    return PolyglotPuzzleVM(hub, disp, puzzle, emb, lang, llm, notif, ev), puzzle


def test_starts_with_two_empty_attempts(vm):
    v, _ = vm
    assert len(v.children) == 2
    assert all(c.model.text == "" for c in v.children)


def test_generate_disabled_until_request_set(vm):
    v, _ = vm
    assert not v.generate_command.can_execute()


def test_add_attempt_disabled_until_response_and_filled(vm):
    v, puzzle = vm
    v.model = v.model.with_request(PolyglotPuzzleRequest(
        src_lang="EN", dst_lang="ES", difficulty="Easy", llm_id="x", llm_temperature=0.0))
    v.model = v.model.with_response(PolyglotPuzzleResponse(
        src_lang_question="Hello", dst_lang_question="Hola"))
    # children still empty → cannot add
    assert not v.add_attempt_command.can_execute()
    for c in v.children:
        c.model = c.model.with_text("nope")
    assert v.add_attempt_command.can_execute()


def test_submit_disabled_until_response_and_at_least_two_filled(vm):
    v, _ = vm
    v.model = v.model.with_request(PolyglotPuzzleRequest(
        src_lang="EN", dst_lang="ES", difficulty="Easy", llm_id="x", llm_temperature=0.0))
    v.model = v.model.with_response(PolyglotPuzzleResponse(
        src_lang_question="Hello", dst_lang_question="Hola"))
    assert not v.submit_command.can_execute()
    for c in v.children:
        c.model = c.model.with_text("hola")
    assert v.submit_command.can_execute()
```

- [ ] **Step 3: Run**

```bash
cd frontend && poetry run pytest tests/viewmodels/polyglot_puzzle -q
```

Expected: 4 passed. If `RelayCommand.can_execute` doesn't re-evaluate on attribute writes, the `can_execute` lambdas may need `can_execute_trigger=...` wired to a property-changed message — consult the VMx quickref.

- [ ] **Step 4: Commit**

```bash
git add frontend/viewmodels/polyglot_puzzle/polyglot_puzzle_vm.py \
        frontend/tests/viewmodels/polyglot_puzzle
git commit -m "feat(viewmodels): PolyglotPuzzleVM composite with derived guards + 4 commands"
```

---

## Task 3.6: Build `views/polyglot_puzzle/` (view + sub-elements)

**Files:**
- Create: `frontend/views/polyglot_puzzle/__init__.py`
- Create: `frontend/views/polyglot_puzzle/attempt_row.py`
- Create: `frontend/views/polyglot_puzzle/embeddings_plot.py`
- Create: `frontend/views/polyglot_puzzle/polyglot_puzzle_view.py`
- Modify: `frontend/views/app_shell.py` (register renderer)
- Modify: `frontend/core/di.py` (construct PolyglotPuzzleVM + EmbeddingsViewVM, add to pages)

- [ ] **Step 1: Write `attempt_row.py`**

```python
# views/polyglot_puzzle/attempt_row.py
from nicegui import ui
from dataclasses import replace

from viewmodels.polyglot_puzzle.attempt_vm import AttemptVM, Attempt


def render(vm: AttemptVM) -> None:
    with ui.row().classes("items-center gap-2 w-full"):
        inp = ui.input("Your translation").props("outlined dense").classes("flex-1")
        inp.bind_value_from(vm, "model", backward=lambda m: m.text)
        inp.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, text=e.value or "")))
        ui.label().bind_text_from(vm, "model",
                                   backward=lambda m: "" if m.similarity is None else f"{m.similarity*100:.0f}%") \
            .classes("text-xs text-[var(--text-3)] w-12 text-right")
```

- [ ] **Step 2: Write `embeddings_plot.py`**

```python
# views/polyglot_puzzle/embeddings_plot.py
import plotly.graph_objects as go
from nicegui import ui

from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM


def render(vm: EmbeddingsViewVM) -> None:
    with ui.column().classes("w-full mt-4 gap-2"):
        toggle = ui.toggle({"2d": "2D", "3d": "3D"}, value="2d") \
            .bind_value_from(vm, "model", backward=lambda m: m.mode) \
            .on_value_change(lambda e: vm.set_mode(e.value))
        chart = ui.plotly(_figure_for(vm.model)).classes("w-full h-72")

        def _rebuild(_=None) -> None:
            chart.update_figure(_figure_for(vm.model))

        vm.model_changed.subscribe(_rebuild)


def _figure_for(m) -> go.Figure:
    if m.mode == "3d" and m.points_3d:
        xs, ys, zs = zip(*m.points_3d)
        return go.Figure(data=[go.Scatter3d(
            x=xs, y=ys, z=zs, mode="markers+text",
            text=list(m.labels), textposition="top center",
            marker={"size": 6},
        )])
    if m.points_2d:
        xs, ys = zip(*m.points_2d)
        return go.Figure(data=[go.Scatter(
            x=xs, y=ys, mode="markers+text",
            text=list(m.labels), textposition="top center",
            marker={"size": 10},
        )])
    return go.Figure(layout={"annotations": [{"text": "Submit attempts to see the projection",
                                              "showarrow": False, "x": 0.5, "y": 0.5}]})
```

- [ ] **Step 3: Write `polyglot_puzzle_view.py`**

```python
# views/polyglot_puzzle/polyglot_puzzle_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import PolyglotPuzzleVM
from views.theme.components import card, pill_button, section_header
from views.polyglot_puzzle.attempt_row import render as render_attempt
from views.polyglot_puzzle.embeddings_plot import render as render_plot


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "polyglot_puzzle")
    assert isinstance(vm, PolyglotPuzzleVM)

    # Lazy-load options on first render.
    if vm.model.request is None:
        # Schedule but don't await — NiceGUI's slot is sync-ish.
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_options_command.execute_async())

    with card():
        section_header("Polyglot Puzzle", subtitle="Translate, then compare semantic similarity")
        with ui.row().classes("gap-3 w-full"):
            src = ui.select([], label="Source").props("outlined dense").classes("flex-1")
            dst = ui.select([], label="Target").props("outlined dense").classes("flex-1")
            dif = ui.select(list(vm.model.difficulties), label="Difficulty").props("outlined dense").classes("flex-1")

        def _refresh_options(_=None) -> None:
            src._props["options"] = list(vm.model.src_langs)
            dst._props["options"] = list(vm.model.dst_langs)
            src.update(); dst.update()
            if vm.model.request:
                src.value = vm.model.request.src_lang
                dst.value = vm.model.request.dst_lang
                dif.value = vm.model.request.difficulty
        vm.model_changed.subscribe(_refresh_options)
        _refresh_options()

        def _set_req(field: str):
            def _cb(e) -> None:
                if not vm.model.request: return
                vm.model = vm.model.with_request(replace(vm.model.request, **{field: e.value or ""}))
            return _cb
        src.on_value_change(_set_req("src_lang"))
        dst.on_value_change(_set_req("dst_lang"))
        dif.on_value_change(_set_req("difficulty"))

        with ui.row().classes("gap-2 mt-3"):
            gen = pill_button("Generate puzzle", variant="primary",
                              on_click=vm.generate_command.execute_async)
            gen.bind_enabled_from(vm, "model", backward=lambda m: m.request is not None)

    # Response + attempts
    response_card = card()
    response_card.classes("mt-4").bind_visibility_from(vm, "model", backward=lambda m: m.has_response)
    with response_card:
        ui.label().bind_text_from(vm, "model", backward=lambda m: (m.response.src_lang_question if m.response else "")) \
            .classes("text-base font-medium")
        ui.label().bind_text_from(vm, "model", backward=lambda m: (m.response.dst_lang_question if m.response else "")) \
            .classes("text-xs text-[var(--text-3)] mt-1")

        attempts_col = ui.column().classes("gap-2 mt-3 w-full")

        def _render_attempts(_=None) -> None:
            attempts_col.clear()
            with attempts_col:
                for child in vm.children:
                    render_attempt(child)
        vm.children_changed.subscribe(_render_attempts)
        _render_attempts()

        with ui.row().classes("gap-2 mt-3"):
            add = pill_button("Add attempt", on_click=vm.add_attempt_command.execute)
            sub = pill_button("Submit", variant="primary", on_click=vm.submit_command.execute_async)
            for btn, cmd in ((add, vm.add_attempt_command), (sub, vm.submit_command)):
                btn.bind_enabled_from(cmd, "can_execute", backward=lambda v: v) if hasattr(cmd, "can_execute") else None

    render_plot(vm.embeddings)
```

(The `bind_enabled_from(cmd, "can_execute", ...)` form depends on VMx's RelayCommand exposing `can_execute` as a reactive property. If it doesn't, instead subscribe to a property-changed message from VMs and call `btn.set_enabled(cmd.can_execute())` manually in the handler.)

- [ ] **Step 4: Wire into `core/di.py`**

In `build_app_shell`, construct the puzzle services + VMs:

```python
from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.services.embeddings_service import EmbeddingsService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService
from viewmodels.polyglot_puzzle.polyglot_puzzle_vm import PolyglotPuzzleVM
from viewmodels.polyglot_puzzle.embeddings_view_vm import EmbeddingsViewVM
...
def build_app_shell(cfg, hub, dispatcher, http, auth_svc) -> AppShellVM:
    notifications = NotificationCenterVM(hub, dispatcher)
    settings = SettingsVM(hub, dispatcher)
    navigation = NavigationVM(hub, dispatcher)
    session = UserSessionVM(hub, dispatcher, auth_svc, http)

    puzzle_svc = PolyglotPuzzleService(http)
    emb_svc = EmbeddingsService(http)
    lang_svc = LanguageService(http)
    llm_svc = LLMService(http)

    home = HomeVM(hub, dispatcher, session)
    polyglot = PolyglotPuzzleVM(
        hub, dispatcher, puzzle_svc, emb_svc, lang_svc, llm_svc, notifications,
        EmbeddingsViewVM(hub, dispatcher),
    )

    return AppShellVM(
        hub, dispatcher,
        session=session, settings=settings, navigation=navigation, notifications=notifications,
        pages=[home, polyglot],
    )
```

- [ ] **Step 5: Register renderer in `app_shell.py`**

```python
from views.polyglot_puzzle.polyglot_puzzle_view import render as render_polyglot
PAGE_RENDERERS["polyglot_puzzle"] = render_polyglot
```

- [ ] **Step 6: Boot and smoke**

```bash
docker compose restart frontend
open "http://localhost:${FRONTEND_PORT}"
```

Log in, navigate to Polyglot (sidebar), generate a puzzle, type two translations, click Submit, observe similarities + 2D/3D plot toggle.

- [ ] **Step 7: Commit**

```bash
git add frontend/views/polyglot_puzzle frontend/views/app_shell.py frontend/core/di.py
git commit -m "feat(views/polyglot_puzzle): full page with attempts list + 2D/3D plotly viz"
```

---

## Task 3.7: Delete legacy `components/polyglot_puzzle.py` and sidebar dependency

**Files:**
- Delete: `frontend/components/polyglot_puzzle.py`
- Modify: `frontend/components/sidebar.py` (remove the `PolyglotPuzzleViewModel.instance().reinitialize()` import + call)

The legacy Streamlit components are still on disk (we delete the whole tree in Phase 7), but this file actively shadows our new `viewmodels/polyglot_puzzle/` namespace if both are around. Better to kill it now.

- [ ] **Step 1: Delete + fix sidebar**

```bash
cd frontend
git rm components/polyglot_puzzle.py
# Remove the import + call lines from the legacy sidebar
sed -i '' '/PolyglotPuzzleViewModel/d' components/sidebar.py
```

- [ ] **Step 2: Verify old streamlit app still parses (it's about to die in Phase 7 anyway, but keep it compilable for now)**

```bash
poetry run python -c "import components.sidebar; print('ok')"
```

If this errors (because other components import the deleted module), grep and remove their imports too.

- [ ] **Step 3: Commit**

```bash
git add -A frontend/components
git commit -m "refactor(legacy): drop polyglot_puzzle.py and sidebar's dependency on it"
```

---

## Task 3.8: Phase 3 gate

- [ ] **Step 1: Smoke**

In the browser: Polyglot Puzzle generates, accepts attempts, submits, plots both 2D and 3D, toggle switches between them.

- [ ] **Step 2: All checks green**

```bash
cd frontend
poetry run pytest -q
poetry run lint-imports
poetry run mypy --strict models viewmodels core views/theme
```

- [ ] **Step 3: Gate commit**

```bash
git commit --allow-empty -m "chore: phase 3 gate — polyglot puzzle full MVVM with composite/derived/commands"
```

---

# Phase 4 — Profile + Assessment

**Goal of this phase:** Profile (interests as composite children + assessment history as aggregate) and Assessment (questions as composite children + score derived). Validates form-heavy pages and history-rendering patterns.

**Phase 4 gate:** Profile loads current user data, edits persist; Assessment runs end-to-end (questions answered → score computed → recorded against the user); history reflows when language changes.

---

## Task 4.1: Refactor `user_service`, `skill_level_service`, `topic_service`, `user_content_service` to async/instance

**Files:**
- Modify: `frontend/models/services/user_service.py`
- Modify: `frontend/models/services/skill_level_service.py`
- Modify: `frontend/models/services/topic_service.py`
- Modify: `frontend/models/services/user_content_service.py`
- Test: `frontend/tests/models/services/test_user_service.py`

Same pattern as Task 3.1. Each becomes `class XService: def __init__(self, http: httpx.AsyncClient) -> None: ...` with all methods `async`. Delete `_sync` variants and class-method wrappers (the Streamlit pages depending on them die in Phase 7).

- [ ] **Step 1: Inspect current shape**

```bash
cd frontend && for f in models/services/{user,skill_level,topic,user_content}_service.py; do echo "=== $f"; head -50 "$f"; done
```

- [ ] **Step 2: Rewrite `user_service.py`** (canonical example)

```python
from __future__ import annotations
import httpx

from models.schemas.user import User, UserCreate, UserUpdate
from models.schemas.user_assessment import UserAssessmentCreate
from models.schemas.user_language import UserLanguage
from models.schemas.user_topic import UserTopicBase


class UserService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get_by_username(self, username: str) -> User:
        r = await self._http.get(f"/users/{username}"); r.raise_for_status()
        return User.model_validate(r.json())

    async def get_id_by_username(self, username: str) -> int:
        r = await self._http.get(f"/users/{username}/id"); r.raise_for_status()
        return int(r.json())

    async def create(self, payload: UserCreate) -> User:
        r = await self._http.post("/users", json=payload.model_dump()); r.raise_for_status()
        return User.model_validate(r.json())

    async def update(self, user_id: int, payload: UserUpdate) -> User:
        r = await self._http.patch(f"/users/{user_id}", json=payload.model_dump()); r.raise_for_status()
        return User.model_validate(r.json())

    async def add_assessment(self, user_id: int, payload: UserAssessmentCreate) -> None:
        r = await self._http.post(f"/users/{user_id}/assessments", json=payload.model_dump()); r.raise_for_status()

    async def set_languages(self, user_id: int, languages: list[UserLanguage]) -> None:
        r = await self._http.put(f"/users/{user_id}/languages", json=[x.model_dump() for x in languages]); r.raise_for_status()

    async def set_topics(self, user_id: int, topics: list[UserTopicBase]) -> None:
        r = await self._http.put(f"/users/{user_id}/topics", json=[x.model_dump() for x in topics]); r.raise_for_status()
```

(Endpoint paths above are illustrative — read the actual backend router and adjust.)

- [ ] **Step 3: Apply same pattern to skill_level, topic, user_content**

Each becomes an `__init__(self, http)` class with `async def` methods. Mirror existing call shapes.

- [ ] **Step 4: Delete `create_user_async` shim** (replaced now)

Remove the temporary `create_user_async` classmethod added in Task 2.5 (Step 3) from `user_service.py`.

- [ ] **Step 5: Fix any callers**

```bash
cd frontend && grep -rln 'UserService\.\|create_user_async' --include='*.py' . | head
```

Update each call site to use the instance (constructed in `core/di.py`). The legacy Streamlit `components/*.py` files may still use the class-method shape — leave them; they're deleted in Phase 7. Only new VMs (RegisterVM, ProfileVM in this phase) need updating.

- [ ] **Step 6: Update `core/di.py` to construct `UserService` and pass to RegisterVM**

In `build_process_scoped`, add `user_svc = UserService(http)` and return it; in `build_app_shell`, pass it to `RegisterVM` (or rather, to the place where `RegisterVM` is constructed — currently lazy in `main.py`'s `/register` route handler; move RegisterVM construction into `core/di.py` if you want it part of the shell, otherwise leave it lazy with the `UserService` injected).

Simpler approach: keep RegisterVM lazy in `main.py` but replace the `_UserSvcAdapter` shim with the real `UserService(HTTP)`. Update `RegisterVM._submit` to call `self._user_svc.create(UserCreate(...))`.

- [ ] **Step 7: Test**

```python
# tests/models/services/test_user_service.py
import httpx, pytest, respx
from models.services.user_service import UserService
from models.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user():
    async with httpx.AsyncClient(base_url="http://test") as http:
        with respx.mock() as router:
            router.post("http://test/users").mock(return_value=httpx.Response(200, json={
                "user_id": 1, "username": "alice", "email": "a@b.c", "first_name": "A", "last_name": "B",
                "user_type": "user",
            }))
            svc = UserService(http)
            payload = UserCreate(username="alice", password="secret1",
                                  email="a@b.c", first_name="A", last_name="B")
            r = await svc.create(payload)
            assert r.username == "alice"
```

(Add fields to the mock JSON to match your actual `User` schema's required fields.)

```bash
cd frontend && poetry run pytest tests/models/services/test_user_service.py -q
```

- [ ] **Step 8: Commit**

```bash
git add frontend/models/services/{user,skill_level,topic,user_content}_service.py \
        frontend/tests/models/services/test_user_service.py frontend/core/di.py frontend/main.py
git commit -m "refactor(services): async/instance user/skill_level/topic/user_content services"
```

---

## Task 4.2: Build `viewmodels/profile/` (interest_vm, profile_vm, assessment_history_vm)

**Files:**
- Create: `frontend/viewmodels/profile/__init__.py`
- Create: `frontend/viewmodels/profile/interest_vm.py`
- Create: `frontend/viewmodels/profile/assessment_history_vm.py`
- Create: `frontend/viewmodels/profile/profile_vm.py`
- Test: `frontend/tests/viewmodels/profile/test_profile_vm.py`

- [ ] **Step 1: `interest_vm.py`** (one per user topic chip)

```python
from __future__ import annotations
from dataclasses import dataclass, replace

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


@dataclass(frozen=True)
class Interest:
    topic_name: str
    selected: bool = False

    def with_selected(self, s: bool) -> "Interest":
        return replace(self, selected=s)


class InterestVM(ComponentVMOf[Interest]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, topic_name: str, selected: bool = False) -> None:
        super().__init__(name=f"interest-{topic_name}", services=(hub, dispatcher),
                         model=Interest(topic_name=topic_name, selected=selected))

    def toggle(self) -> None:
        self.model = self.model.with_selected(not self.model.selected)
```

- [ ] **Step 2: `assessment_history_vm.py`** (aggregate showing past assessments per language)

```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Tuple

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


@dataclass(frozen=True)
class HistoryEntry:
    language: str
    skill_level: str
    date_iso: str  # YYYY-MM-DD


@dataclass(frozen=True)
class AssessmentHistory:
    selected_language: str = ""
    entries: Tuple[HistoryEntry, ...] = field(default_factory=tuple)


class AssessmentHistoryVM(ComponentVMOf[AssessmentHistory]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher) -> None:
        super().__init__(name="assessment-history", services=(hub, dispatcher),
                         model=AssessmentHistory())

    def set_entries(self, entries: list[HistoryEntry]) -> None:
        self.model = replace(self.model, entries=tuple(entries))

    def set_language_filter(self, lang: str) -> None:
        if lang != self.model.selected_language:
            self.model = replace(self.model, selected_language=lang)

    @property
    def filtered_entries(self) -> tuple[HistoryEntry, ...]:
        if not self.model.selected_language:
            return self.model.entries
        return tuple(e for e in self.model.entries if e.language == self.model.selected_language)
```

- [ ] **Step 3: `profile_vm.py`** (composite of InterestVMs + history aggregate)

```python
from __future__ import annotations
from dataclasses import dataclass, field, replace
from typing import Optional, Tuple

from vmx.components import CompositeVM
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.profile.interest_vm import InterestVM
from viewmodels.profile.assessment_history_vm import AssessmentHistoryVM, HistoryEntry
from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.services.user_service import UserService
from models.services.topic_service import TopicService
from models.services.language_service import LanguageService
from models.schemas.user import UserUpdate
from models.schemas.user_topic import UserTopicBase


@dataclass(frozen=True)
class ProfileModel:
    user_id: Optional[int] = None
    preferred_name: str = ""
    first_name: str = ""
    last_name: str = ""
    email: str = ""
    native_language: str = ""
    learning_languages: Tuple[str, ...] = field(default_factory=tuple)
    in_flight: bool = False
    error: str = ""


class ProfileVM(CompositeVM[InterestVM], PageVM):  # type: ignore[misc]
    route = "profile"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        user_svc: UserService,
        topic_svc: TopicService,
        language_svc: LanguageService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
        history: AssessmentHistoryVM,
    ) -> None:
        super().__init__(name="profile", services=(hub, dispatcher))
        self._user_svc = user_svc
        self._topic_svc = topic_svc
        self._lang_svc = language_svc
        self._session = session
        self._notify = notifications
        self.history = history
        self.model = ProfileModel()

        self.load_command = RelayCommand(execute=self._load)
        self.save_command = RelayCommand(execute=self._save, can_execute=lambda: bool(self.model.first_name and not self.model.in_flight))

        # Auto-load when session has a username and we don't yet have data.
        session.model_changed.subscribe(lambda _: self._auto_load_if_needed())

    def _auto_load_if_needed(self) -> None:
        if self._session.model.is_authenticated and self.model.user_id is None:
            import asyncio; asyncio.create_task(self._load())

    async def _load(self) -> None:
        if not self._session.model.username:
            return
        user = await self._user_svc.get_by_username(self._session.model.username)
        all_topics = [t.topic_name for t in await self._topic_svc.list()]

        # populate ProfileModel from user
        self.model = ProfileModel(
            user_id=user.user_id,
            preferred_name=getattr(user, "preferred_name", "") or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            email=user.email or "",
            native_language=getattr(user, "native_language", "") or "",
            learning_languages=tuple(getattr(user, "learning_languages", ())),
        )

        # populate interest children
        user_topic_names = {t.topic_name for t in getattr(user, "user_topics", [])}
        for c in list(self.children):
            self.remove_child(c)
        for t_name in all_topics:
            self.add_child(InterestVM(self.message_hub, self.dispatcher, t_name, selected=(t_name in user_topic_names)))

        # populate assessment history
        history_entries = [
            HistoryEntry(language=a.language.language_name,
                         skill_level=a.skill_level,
                         date_iso=str(a.assessment_date)[:10])
            for a in getattr(user, "user_assessments", [])
        ]
        self.history.set_entries(history_entries)
        if history_entries:
            self.history.set_language_filter(history_entries[0].language)

    async def _save(self) -> None:
        if self.model.user_id is None:
            return
        self.model = replace(self.model, in_flight=True, error="")
        try:
            payload = UserUpdate(
                first_name=self.model.first_name,
                last_name=self.model.last_name,
                preferred_name=self.model.preferred_name,
                email=self.model.email,
            )
            await self._user_svc.update(self.model.user_id, payload)
            selected_topics = [UserTopicBase(topic_name=c.model.topic_name)
                               for c in self.children if c.model.selected]
            await self._user_svc.set_topics(self.model.user_id, selected_topics)
            self._notify.push_success("Profile saved.")
        except Exception as e:
            self.model = replace(self.model, in_flight=False, error=f"Save failed: {e}")
            return
        self.model = replace(self.model, in_flight=False)
```

- [ ] **Step 4: Minimal test**

```python
# tests/viewmodels/profile/test_profile_vm.py
import pytest
from unittest.mock import AsyncMock
import httpx
from dataclasses import replace

from vmx.services import MessageHub, RxDispatcher

from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.profile.assessment_history_vm import AssessmentHistoryVM
from viewmodels.profile.profile_vm import ProfileVM, ProfileModel


@pytest.fixture
def vm():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    auth = AsyncMock()
    http = httpx.AsyncClient(base_url="http://test")
    session = UserSessionVM(hub, disp, auth, http)
    return ProfileVM(hub, disp, AsyncMock(), AsyncMock(), AsyncMock(), session, NotificationCenterVM(hub, disp),
                     AssessmentHistoryVM(hub, disp))


def test_save_disabled_until_first_name(vm):
    assert not vm.save_command.can_execute()
    vm.model = replace(vm.model, user_id=1, first_name="A")
    assert vm.save_command.can_execute()
```

- [ ] **Step 5: Run + commit**

```bash
cd frontend && poetry run pytest tests/viewmodels/profile -q
git add frontend/viewmodels/profile frontend/tests/viewmodels/profile
git commit -m "feat(viewmodels): ProfileVM composite + interest children + history aggregate"
```

---

## Task 4.3: Build `views/profile/`

**Files:**
- Create: `frontend/views/profile/__init__.py`
- Create: `frontend/views/profile/interest_chip.py`
- Create: `frontend/views/profile/profile_view.py`
- Modify: `frontend/views/app_shell.py` (register renderer)
- Modify: `frontend/core/di.py` (construct ProfileVM + history; add to pages)

- [ ] **Step 1: `interest_chip.py`**

```python
from nicegui import ui

from viewmodels.profile.interest_vm import InterestVM


def render(vm: InterestVM) -> None:
    def _on_click() -> None:
        vm.toggle()
    chip = ui.element("span").classes("inline-flex items-center px-2 py-0.5 rounded-full text-xs cursor-pointer mr-1 mb-1") \
        .on("click", _on_click)
    def _refresh(_=None) -> None:
        chip._classes = [c for c in chip._classes if "bg-" not in c and "text-" not in c]
        if vm.model.selected:
            chip.classes("bg-[var(--brand)] text-[var(--surface-0)]")
        else:
            chip.classes("bg-white/5 text-[var(--text-2)] hover:bg-white/10")
        chip.update()
    vm.model_changed.subscribe(_refresh)
    with chip:
        ui.label(vm.model.topic_name)
    _refresh()
```

- [ ] **Step 2: `profile_view.py`**

```python
from nicegui import ui
from dataclasses import replace

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.profile.profile_vm import ProfileVM
from views.theme.components import card, pill_button, section_header
from views.profile.interest_chip import render as render_chip


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "profile")
    assert isinstance(vm, ProfileVM)

    with card():
        section_header("Profile")
        with ui.row().classes("gap-3 w-full"):
            preferred = ui.input("Preferred name").props("outlined dense").classes("flex-1") \
                .bind_value_from(vm, "model", backward=lambda m: m.preferred_name)
            preferred.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, preferred_name=e.value or "")))
            email = ui.input("Email").props("outlined dense").classes("flex-1") \
                .bind_value_from(vm, "model", backward=lambda m: m.email)
            email.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, email=e.value or "")))
        with ui.row().classes("gap-3 w-full mt-3"):
            first = ui.input("First name").props("outlined dense").classes("flex-1") \
                .bind_value_from(vm, "model", backward=lambda m: m.first_name)
            first.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, first_name=e.value or "")))
            last = ui.input("Last name").props("outlined dense").classes("flex-1") \
                .bind_value_from(vm, "model", backward=lambda m: m.last_name)
            last.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, last_name=e.value or "")))

        ui.label("Interests").classes("text-xs uppercase tracking-wider text-[var(--text-3)] mt-4")
        chips_row = ui.row().classes("flex-wrap w-full mt-2")
        def _render_chips(_=None) -> None:
            chips_row.clear()
            with chips_row:
                for c in vm.children:
                    render_chip(c)
        vm.children_changed.subscribe(_render_chips)
        _render_chips()

        with ui.row().classes("justify-end mt-4 w-full"):
            save = pill_button("Save", variant="primary", on_click=vm.save_command.execute_async)
            save.bind_enabled_from(vm, "model", backward=lambda m: bool(m.first_name and not m.in_flight))

    with card().classes("mt-4"):
        section_header("Assessment history")
        history = vm.history
        languages_sel = ui.select([], label="Filter by language").props("outlined dense").classes("w-60")
        def _refresh_filter(_=None) -> None:
            langs = sorted({e.language for e in history.model.entries})
            languages_sel._props["options"] = langs
            languages_sel.update()
            languages_sel.value = history.model.selected_language or (langs[0] if langs else None)
        history.model_changed.subscribe(_refresh_filter)
        _refresh_filter()
        languages_sel.on_value_change(lambda e: history.set_language_filter(e.value or ""))

        list_col = ui.column().classes("gap-1 mt-2 w-full")
        def _render_list(_=None) -> None:
            list_col.clear()
            with list_col:
                for entry in history.filtered_entries:
                    with ui.row().classes("items-center justify-between w-full py-1 border-b border-white/5"):
                        ui.label(f"{entry.date_iso} · {entry.language}").classes("text-sm")
                        ui.label(entry.skill_level).classes("text-xs text-[var(--brand)]")
        history.model_changed.subscribe(_render_list)
        _render_list()
```

- [ ] **Step 3: Wire DI + renderer**

In `core/di.py` add `ProfileVM` construction (services TopicService + UserService + LanguageService already there):

```python
from models.services.user_service import UserService
from models.services.topic_service import TopicService
from viewmodels.profile.profile_vm import ProfileVM
from viewmodels.profile.assessment_history_vm import AssessmentHistoryVM
...
user_svc = UserService(http)
topic_svc = TopicService(http)
profile = ProfileVM(hub, dispatcher, user_svc, topic_svc, lang_svc, session, notifications,
                     AssessmentHistoryVM(hub, dispatcher))
...
pages=[home, polyglot, profile]
```

In `views/app_shell.py`:

```python
from views.profile.profile_view import render as render_profile
PAGE_RENDERERS["profile"] = render_profile
```

- [ ] **Step 4: Smoke**

Boot, log in, navigate to Profile. Confirm: data loads, edits persist after Save, interests toggle.

- [ ] **Step 5: Commit**

```bash
git add frontend/views/profile frontend/views/app_shell.py frontend/core/di.py
git commit -m "feat(views/profile): edit profile, toggle interests, view assessment history"
```

---

## Task 4.4: Build `viewmodels/assessment/assessment_vm.py` + `views/assessment/`

**Files:**
- Create: `frontend/viewmodels/assessment/__init__.py`
- Create: `frontend/viewmodels/assessment/question_vm.py`
- Create: `frontend/viewmodels/assessment/assessment_vm.py`
- Create: `frontend/views/assessment/__init__.py`
- Create: `frontend/views/assessment/assessment_view.py`
- Modify: `frontend/core/di.py`
- Modify: `frontend/views/app_shell.py`

The current Streamlit assessment page (`frontend/components/assessment.py`, 178 LOC) collects a few topic-based responses and submits them as a `UserAssessmentCreate`. Mirror that flow as a composite-of-question-VMs with a derived score.

- [ ] **Step 1: Read current behavior**

```bash
sed -n '1,180p' frontend/components/assessment.py
```

Note the question shape: usually `{prompt, options[], correct_index}` or a free-form rating.

- [ ] **Step 2: Define `question_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional, Tuple

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


@dataclass(frozen=True)
class Question:
    prompt: str
    options: Tuple[str, ...]
    correct_index: int
    selected_index: Optional[int] = None

    @property
    def is_answered(self) -> bool:
        return self.selected_index is not None

    @property
    def is_correct(self) -> bool:
        return self.is_answered and self.selected_index == self.correct_index


class QuestionVM(ComponentVMOf[Question]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, model: Question) -> None:
        super().__init__(name=f"question-{model.prompt[:20]}", services=(hub, dispatcher), model=model)

    def select(self, idx: int) -> None:
        self.model = replace(self.model, selected_index=idx)
```

- [ ] **Step 3: Define `assessment_vm.py`**

```python
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx.components import CompositeVM
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.assessment.question_vm import QuestionVM, Question
from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM

from models.services.user_service import UserService
from models.services.language_service import LanguageService
from models.schemas.user_assessment import UserAssessmentCreate
from datetime import date


@dataclass(frozen=True)
class AssessmentModel:
    language: str = ""
    in_flight: bool = False
    completed_score: Optional[int] = None  # 0..100 if submitted


class AssessmentVM(CompositeVM[QuestionVM], PageVM):  # type: ignore[misc]
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
        super().__init__(name="assessment", services=(hub, dispatcher))
        self._user_svc = user_svc
        self._lang_svc = language_svc
        self._session = session
        self._notify = notifications
        self.model = AssessmentModel()

        self.load_command = RelayCommand(execute=self._load)
        self.submit_command = RelayCommand(execute=self._submit, can_execute=self._can_submit)

    @property
    def score_percent(self) -> int:
        if not self.children:
            return 0
        correct = sum(1 for c in self.children if c.model.is_correct)
        return round(100 * correct / len(self.children))

    @property
    def all_answered(self) -> bool:
        return bool(self.children) and all(c.model.is_answered for c in self.children)

    def _can_submit(self) -> bool:
        return self.all_answered and not self.model.in_flight and bool(self.model.language)

    def set_language(self, lang: str) -> None:
        if lang != self.model.language:
            self.model = replace(self.model, language=lang)
            # Reset children when language changes — different question set.
            for c in list(self.children):
                self.remove_child(c)
            for q in self._seed_questions_for(lang):
                self.add_child(QuestionVM(self.message_hub, self.dispatcher, q))

    def _seed_questions_for(self, lang: str) -> list[Question]:
        """Static placeholder question bank — replace with a backend fetch when /assessments/questions exists."""
        return [
            Question(prompt=f"What is 'hello' in {lang}?", options=("Salut", "Hola", "こんにちは", "Hallo"), correct_index=1),
            Question(prompt=f"Pick the verb form for 'I am' in {lang}.", options=("Soy", "Eres", "Es", "Somos"), correct_index=0),
            Question(prompt=f"Which is a greeting in {lang}?", options=("Adios", "Por favor", "Buenos días", "Gracias"), correct_index=2),
        ]

    async def _load(self) -> None:
        # Populate language list from user's learning languages; default to first.
        if not self._session.model.username:
            return
        user = await self._user_svc.get_by_username(self._session.model.username)
        learning = list(getattr(user, "learning_languages", []))
        if learning:
            self.set_language(learning[0])

    async def _submit(self) -> None:
        if not self._session.model.username:
            return
        user = await self._user_svc.get_by_username(self._session.model.username)
        score = self.score_percent
        skill_level = "A1" if score < 30 else "A2" if score < 50 else "B1" if score < 70 else "B2" if score < 85 else "C1"
        self.model = replace(self.model, in_flight=True)
        try:
            payload = UserAssessmentCreate(
                user_id=user.user_id,
                language_name=self.model.language,
                skill_level=skill_level,
                assessment_date=date.today(),
            )
            await self._user_svc.add_assessment(user.user_id, payload)
            self._notify.push_success(f"Score: {score}% — level {skill_level}")
            self.model = replace(self.model, in_flight=False, completed_score=score)
        except Exception as e:
            self.model = replace(self.model, in_flight=False)
            self._notify.push_error(f"Could not save assessment: {e}")
```

(Adjust `UserAssessmentCreate` constructor args to match your actual schema.)

- [ ] **Step 4: View**

```python
# views/assessment/assessment_view.py
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.assessment.assessment_vm import AssessmentVM
from views.theme.components import card, pill_button, section_header, chip


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "assessment")
    assert isinstance(vm, AssessmentVM)

    if not vm.model.language:
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_command.execute_async())

    with card():
        section_header("Skill assessment")
        ui.label().bind_text_from(vm, "model", backward=lambda m: f"Language: {m.language or '(loading…)'}") \
            .classes("text-sm text-[var(--text-2)] mb-2")

        questions_col = ui.column().classes("gap-3 w-full")
        def _render_questions(_=None) -> None:
            questions_col.clear()
            with questions_col:
                for i, q_vm in enumerate(vm.children):
                    with ui.column().classes("gap-1"):
                        ui.label(f"{i+1}. {q_vm.model.prompt}").classes("text-sm")
                        radio = ui.radio(list(q_vm.model.options))
                        idx = q_vm.model.selected_index
                        if idx is not None:
                            radio.value = q_vm.model.options[idx]
                        radio.on_value_change(_on_select(q_vm))
        vm.children_changed.subscribe(_render_questions)
        _render_questions()

        with ui.row().classes("justify-between items-center mt-4"):
            ui.label().bind_text_from(vm, "model",
                                       backward=lambda m: ("Score: " + str(m.completed_score) + "%") if m.completed_score is not None else "") \
                .classes("text-sm text-[var(--brand)]")
            submit = pill_button("Submit", variant="primary", on_click=vm.submit_command.execute_async)
            submit.bind_enabled_from(vm, "model",
                                      backward=lambda m: vm.all_answered and not m.in_flight)


def _on_select(q_vm):
    def _cb(e) -> None:
        idx = list(q_vm.model.options).index(e.value)
        q_vm.select(idx)
    return _cb
```

- [ ] **Step 5: Wire DI + renderer**

```python
# core/di.py
from viewmodels.assessment.assessment_vm import AssessmentVM
...
assessment = AssessmentVM(hub, dispatcher, user_svc, lang_svc, session, notifications)
pages=[home, polyglot, profile, assessment]
```

```python
# views/app_shell.py
from views.assessment.assessment_view import render as render_assessment
PAGE_RENDERERS["assessment"] = render_assessment
```

- [ ] **Step 6: Smoke**

Log in, go to Assessment, answer all questions, submit. Confirm score toast + history reflows in Profile.

- [ ] **Step 7: Commit + gate**

```bash
git add frontend/viewmodels/assessment frontend/views/assessment \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(assessment): composite QuestionVMs, derived score, submit to backend"
git commit --allow-empty -m "chore: phase 4 gate — profile/assessment end-to-end"
```

---

# Phase 5 — Chat

**Goal of this phase:** the most async-heavy page. Streaming token-by-token updates, persona switching, image upload (for vision-capable LLMs), TTS playback. Matches the polish-v2 chat mockup (left rail + conversation pane + right rail with persona/model/settings).

**Phase 5 gate:** real chat with backend streams responses without UI jank; persona swap mid-conversation preserves history; image upload + vision LLM works on a vision-capable model; TTS toggles on/off; toggle of vision/non-vision LLM enables/disables the attach widget (no more of the workaround in `develop` commit `250897d`).

---

## Task 5.1: Refactor `chat_service`, `text_to_speech_service`, `persona_service` to async/instance

**Files:**
- Modify: `frontend/models/services/chat_service.py`
- Modify: `frontend/models/services/text_to_speech_service.py`
- Modify: `frontend/models/services/persona_service.py`

- [ ] **Step 1: Streaming chat service**

The current implementation likely posts a chat message and awaits a full response. To stream, switch to `httpx.AsyncClient.stream(...)` and yield tokens as they arrive (backend must support a streaming endpoint — confirm against `backend/routers/chat.py`).

```python
# models/services/chat_service.py
from __future__ import annotations
from typing import AsyncIterator
import httpx
import json

from models.schemas.chat import ChatMessage
from models.schemas.prompt import Prompt


class ChatService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def stream(self, prompt: Prompt) -> AsyncIterator[str]:
        """Yield response chunks as they stream from the backend."""
        async with self._http.stream("POST", "/chat/stream", json=prompt.model_dump(),
                                     timeout=httpx.Timeout(connect=5.0, read=60.0, write=15.0, pool=15.0)) as r:
            r.raise_for_status()
            async for line in r.aiter_lines():
                if not line:
                    continue
                # Common SSE convention: lines start with "data: <json>"
                payload = line[6:] if line.startswith("data: ") else line
                try:
                    chunk = json.loads(payload)
                    yield chunk.get("text", "")
                except json.JSONDecodeError:
                    yield payload

    async def send(self, prompt: Prompt) -> ChatMessage:
        """Non-streaming fallback / for personas/LLMs that don't stream."""
        r = await self._http.post("/chat", json=prompt.model_dump())
        r.raise_for_status()
        return ChatMessage.model_validate(r.json())
```

If the backend doesn't yet support `/chat/stream`, fall back to `send()` only — `ChatVM` will still work, just without token-by-token rendering. Open a backend issue from this work for streaming support, but don't block this phase on it; we can always swap `_handle_send` to `stream()` later.

- [ ] **Step 2: TTS service**

```python
# models/services/text_to_speech_service.py
from __future__ import annotations
import httpx

from models.schemas.text_to_speech import TextToSpeechRequest


class TextToSpeechService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def synthesize(self, req: TextToSpeechRequest) -> bytes:
        r = await self._http.post("/tts", json=req.model_dump())
        r.raise_for_status()
        return r.content
```

- [ ] **Step 3: Persona service**

```python
# models/services/persona_service.py
from __future__ import annotations
import httpx
from models.domain.persona import Persona


class PersonaService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def list(self) -> list[Persona]:
        r = await self._http.get("/personas"); r.raise_for_status()
        return [Persona.model_validate(x) for x in r.json()]

    async def get_default(self) -> Persona | None:
        personas = await self.list()
        return next((p for p in personas if getattr(p, "is_default", False)), personas[0] if personas else None)
```

- [ ] **Step 4: Commit**

```bash
cd frontend
git add models/services/{chat,text_to_speech,persona}_service.py
git commit -m "refactor(services): async chat (streaming), tts, persona services"
```

---

## Task 5.2: Build `viewmodels/chat/chat_message_vm.py` (accumulator)

**Files:**
- Create: `frontend/viewmodels/chat/__init__.py`
- Create: `frontend/viewmodels/chat/chat_message_vm.py`

The key trick for jank-free streaming: the message model is a single string that mutates via append; the view binds once and the bound label updates in place. We do NOT add a new ChatMessageVM child per token.

- [ ] **Step 1: Write the VM**

```bash
cd frontend && mkdir -p viewmodels/chat tests/viewmodels/chat
touch viewmodels/chat/__init__.py tests/viewmodels/chat/__init__.py
```

```python
# viewmodels/chat/chat_message_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Literal, Optional
from datetime import datetime

from vmx.components import ComponentVMOf
from vmx.services import MessageHub, RxDispatcher


Role = Literal["user", "assistant", "system"]


@dataclass(frozen=True)
class ChatBubble:
    role: Role
    text: str
    timestamp_iso: str
    image_b64: Optional[str] = None     # for vision-uploaded user messages
    is_streaming: bool = False          # True for the in-flight assistant bubble


class ChatMessageVM(ComponentVMOf[ChatBubble]):
    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher, bubble: ChatBubble) -> None:
        super().__init__(name=f"chat-msg-{bubble.timestamp_iso}", services=(hub, dispatcher), model=bubble)

    def append_text(self, chunk: str) -> None:
        self.model = replace(self.model, text=self.model.text + chunk)

    def finalize(self) -> None:
        if self.model.is_streaming:
            self.model = replace(self.model, is_streaming=False)
```

- [ ] **Step 2: Commit**

```bash
git add frontend/viewmodels/chat/chat_message_vm.py frontend/viewmodels/chat/__init__.py
git commit -m "feat(viewmodels): ChatMessageVM with append_text accumulator for streaming"
```

---

## Task 5.3: Build `viewmodels/chat/chat_vm.py`

**Files:**
- Create: `frontend/viewmodels/chat/chat_vm.py`
- Test: `frontend/tests/viewmodels/chat/test_chat_vm.py`

Composite. Children are `ChatMessageVM`s (one per turn — user + assistant pair). Holds session-level state: current LLM, current persona, draft text, attachment, vision-capability derived flag.

- [ ] **Step 1: Write `chat_vm.py`**

```python
# viewmodels/chat/chat_vm.py
from __future__ import annotations
import base64
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Optional

from vmx.components import CompositeVM
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.chat.chat_message_vm import ChatMessageVM, ChatBubble
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.settings_vm import SettingsVM

from models.domain.llm import LLM
from models.domain.persona import Persona
from models.schemas.prompt import Prompt
from models.services.chat_service import ChatService
from models.services.llm_service import LLMService
from models.services.persona_service import PersonaService
from models.services.text_to_speech_service import TextToSpeechService


@dataclass(frozen=True)
class ChatSession:
    persona: Optional[Persona] = None
    llm: Optional[LLM] = None
    temperature: float = 0.7
    draft: str = ""
    attached_image_b64: Optional[str] = None
    tts_enabled: bool = False
    in_flight: bool = False

    @property
    def is_vision_llm(self) -> bool:
        return bool(self.llm and "vision" in (self.llm.capabilities or []))

    @property
    def can_attach(self) -> bool:
        return self.is_vision_llm and not self.in_flight

    @property
    def can_send(self) -> bool:
        return bool(self.persona and self.llm and self.draft.strip() and not self.in_flight)


class ChatVM(CompositeVM[ChatMessageVM], PageVM):  # type: ignore[misc]
    route = "chat"

    def __init__(
        self,
        hub: MessageHub,
        dispatcher: RxDispatcher,
        chat_svc: ChatService,
        llm_svc: LLMService,
        persona_svc: PersonaService,
        tts_svc: TextToSpeechService,
        settings: SettingsVM,
        notifications: NotificationCenterVM,
    ) -> None:
        super().__init__(name="chat", services=(hub, dispatcher))
        self._chat = chat_svc
        self._llm = llm_svc
        self._persona = persona_svc
        self._tts = tts_svc
        self._settings = settings
        self._notify = notifications
        self.model = ChatSession()

        self.load_options_command = RelayCommand(execute=self._load_options)
        self.send_command = RelayCommand(execute=self._send, can_execute=lambda: self.model.can_send)
        self.clear_command = RelayCommand(execute=self._clear)

    def set_persona(self, persona: Persona) -> None:
        self.model = replace(self.model, persona=persona)

    def set_llm(self, llm: LLM) -> None:
        self.model = replace(self.model, llm=llm)

    def set_temperature(self, t: float) -> None:
        self.model = replace(self.model, temperature=t)

    def set_draft(self, text: str) -> None:
        self.model = replace(self.model, draft=text)

    def toggle_tts(self) -> None:
        self.model = replace(self.model, tts_enabled=not self.model.tts_enabled)

    def attach_image_bytes(self, data: bytes) -> None:
        if not self.model.is_vision_llm:
            self._notify.push_warning("Current LLM doesn't support vision; attachment ignored.")
            return
        self.model = replace(self.model, attached_image_b64=base64.b64encode(data).decode("ascii"))

    def clear_attachment(self) -> None:
        self.model = replace(self.model, attached_image_b64=None)

    async def _load_options(self) -> None:
        personas = await self._persona.list()
        llms = await self._llm.get_content()
        if not (personas and llms):
            self._notify.push_error("Could not load personas or LLMs.")
            return
        default_persona = next((p for p in personas if getattr(p, "is_default", False)), personas[0])
        # honor user's persisted default if set
        if self._settings.model.default_persona_id:
            default_persona = next((p for p in personas if p.id == self._settings.model.default_persona_id), default_persona)
        default_llm = llms[0]
        if self._settings.model.default_llm_id:
            default_llm = next((m for m in llms if m.id == self._settings.model.default_llm_id), default_llm)
        self.model = replace(self.model, persona=default_persona, llm=default_llm)

    async def _send(self) -> None:
        if not (self.model.persona and self.model.llm and self.model.draft.strip()):
            return
        now = datetime.now().isoformat(timespec="seconds")
        user_bubble = ChatBubble(role="user", text=self.model.draft, timestamp_iso=now,
                                  image_b64=self.model.attached_image_b64)
        self.add_child(ChatMessageVM(self.message_hub, self.dispatcher, user_bubble))
        assistant_bubble = ChatBubble(role="assistant", text="", timestamp_iso=datetime.now().isoformat(timespec="seconds"),
                                       is_streaming=True)
        assistant_vm = ChatMessageVM(self.message_hub, self.dispatcher, assistant_bubble)
        self.add_child(assistant_vm)

        self.model = replace(self.model, in_flight=True, draft="", attached_image_b64=None)
        try:
            prompt = Prompt(
                messages=[{"role": c.model.role, "content": c.model.text,
                            "image_b64": c.model.image_b64} for c in self.children[:-1]],
                persona_id=self.model.persona.id,
                llm_id=self.model.llm.id,
                temperature=self.model.temperature,
            )
            try:
                async for chunk in self._chat.stream(prompt):
                    assistant_vm.append_text(chunk)
            except Exception:
                # Streaming endpoint not available; fall back to non-streaming.
                resp = await self._chat.send(prompt)
                assistant_vm.append_text(resp.content if hasattr(resp, "content") else str(resp))

            assistant_vm.finalize()

            if self.model.tts_enabled and assistant_vm.model.text.strip():
                # Best-effort TTS — silently no-op on failure.
                try:
                    from models.schemas.text_to_speech import TextToSpeechRequest
                    audio = await self._tts.synthesize(TextToSpeechRequest(
                        text=assistant_vm.model.text, language=self.model.persona.language if hasattr(self.model.persona, "language") else "en"))
                    # Audio playback wired in View layer (Task 5.5).
                    self._notify.push_info("Audio ready.")
                except Exception:
                    pass
        finally:
            self.model = replace(self.model, in_flight=False)

    def _clear(self) -> None:
        for c in list(self.children):
            self.remove_child(c)
```

- [ ] **Step 2: Quick test**

```python
# tests/viewmodels/chat/test_chat_vm.py
import pytest
from unittest.mock import AsyncMock
from dataclasses import replace

from vmx.services import MessageHub, RxDispatcher

from viewmodels.chat.chat_vm import ChatVM, ChatSession
from viewmodels.shell.settings_vm import SettingsVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM


@pytest.fixture
def vm():
    hub, disp = MessageHub(), RxDispatcher.immediate()
    return ChatVM(hub, disp, AsyncMock(), AsyncMock(), AsyncMock(), AsyncMock(),
                  SettingsVM(hub, disp), NotificationCenterVM(hub, disp))


def test_can_send_false_when_no_llm_or_draft(vm):
    assert not vm.send_command.can_execute()


def test_is_vision_llm_derived(vm):
    class _LLM: capabilities = ["vision", "content"]; id = "x"
    vm.set_llm(_LLM())
    assert vm.model.is_vision_llm
    assert vm.model.can_attach
```

- [ ] **Step 3: Run + commit**

```bash
cd frontend && poetry run pytest tests/viewmodels/chat -q
git add frontend/viewmodels/chat/chat_vm.py frontend/tests/viewmodels/chat
git commit -m "feat(viewmodels): ChatVM composite with streaming/vision/persona/TTS"
```

---

## Task 5.4: Build `views/chat/` (message_bubble + chat_view)

**Files:**
- Create: `frontend/views/chat/__init__.py`
- Create: `frontend/views/chat/message_bubble.py`
- Create: `frontend/views/chat/chat_view.py`
- Modify: `frontend/views/app_shell.py`
- Modify: `frontend/core/di.py`

- [ ] **Step 1: `message_bubble.py`**

```python
# views/chat/message_bubble.py
from nicegui import ui

from viewmodels.chat.chat_message_vm import ChatMessageVM


def render(vm: ChatMessageVM) -> None:
    is_user = vm.model.role == "user"
    cls_row = "items-start gap-3 max-w-[84%]" + (" self-end flex-row-reverse ml-auto" if is_user else "")
    bubble_cls = ("rounded-xl border px-3.5 py-2.5 text-sm leading-relaxed "
                  + ("border-[var(--brand)]/20 bg-[var(--brand)]/10 text-orange-100 rounded-tr-sm"
                     if is_user else
                     "border-white/5 bg-[var(--surface-1)] text-[var(--text-1)] rounded-tl-sm"))

    with ui.row().classes(cls_row):
        ui.label("YOU" if is_user else "AI").classes(
            "w-7 h-7 rounded-full text-white text-xs font-semibold flex items-center justify-center "
            + ("bg-violet-500" if is_user else "bg-pink-500")
        )
        with ui.column().classes("gap-1"):
            meta = ui.label().classes("text-[10px] text-[var(--text-3)]" + (" text-right" if is_user else ""))
            meta.bind_text_from(vm, "model",
                                 backward=lambda m: f"{'You' if m.role == 'user' else 'AI'} · {m.timestamp_iso[11:16]}")
            if vm.model.image_b64:
                ui.image(f"data:image/jpeg;base64,{vm.model.image_b64}").classes("max-w-xs rounded-lg mt-1")
            text_lbl = ui.label().classes(bubble_cls)
            text_lbl.bind_text_from(vm, "model", backward=lambda m: m.text + (" ▎" if m.is_streaming else ""))
```

- [ ] **Step 2: `chat_view.py`**

```python
# views/chat/chat_view.py
import base64
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.chat.chat_vm import ChatVM
from views.theme.components import card, pill_button, section_header, chip
from views.chat.message_bubble import render as render_bubble


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "chat")
    assert isinstance(vm, ChatVM)

    if vm.model.persona is None:
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_options_command.execute_async())

    # Three-column: nav is in shell drawer; here we render conversation + right rail.
    with ui.row().classes("w-full gap-4"):
        with ui.column().classes("flex-1 gap-2"):
            # Header strip
            with card():
                with ui.row().classes("items-center gap-3 w-full"):
                    ui.label().bind_text_from(vm, "model",
                                               backward=lambda m: m.persona.persona_name if m.persona else "(loading…)") \
                        .classes("text-sm font-semibold tracking-tight")
                    ui.label().bind_text_from(vm, "model",
                                               backward=lambda m: f"· {m.llm.display_name() if m.llm else ''}") \
                        .classes("text-xs text-[var(--text-3)]")
                    ui.space()
                    pill_button("Clear", on_click=vm.clear_command.execute)

            # Messages
            msg_col = ui.column().classes("gap-3 w-full mt-2 max-h-[58vh] overflow-y-auto")
            def _render_msgs(_=None) -> None:
                msg_col.clear()
                with msg_col:
                    for c in vm.children:
                        render_bubble(c)
            vm.children_changed.subscribe(_render_msgs)
            _render_msgs()

            # Composer
            with card().classes("mt-2"):
                # Top row: model/temp/locale chips + token meter (last is just a placeholder until backend reports it)
                with ui.row().classes("gap-2 items-center w-full mb-2"):
                    chip("model").classes("gap-1")
                    ui.label().bind_text_from(vm, "model", backward=lambda m: m.llm.display_name() if m.llm else "—") \
                        .classes("text-xs text-[var(--text-2)]")
                    ui.space()
                    chip(f"persona").classes("gap-1")
                    ui.label().bind_text_from(vm, "model", backward=lambda m: m.persona.persona_name if m.persona else "—") \
                        .classes("text-xs text-[var(--text-2)]")

                # Attachment preview
                attached_row = ui.row().classes("gap-2 mb-2")
                def _render_attach(_=None) -> None:
                    attached_row.clear()
                    if vm.model.attached_image_b64:
                        with attached_row:
                            ui.image(f"data:image/jpeg;base64,{vm.model.attached_image_b64}") \
                                .classes("max-w-[100px] rounded-md")
                            ui.button(icon="close", on_click=vm.clear_attachment).props("flat dense round")
                vm.model_changed.subscribe(_render_attach)
                _render_attach()

                with ui.row().classes("items-end gap-2 w-full"):
                    upload = ui.upload(on_upload=_on_upload(vm), auto_upload=True,
                                       max_files=1).props("flat hide-upload-btn accept=image/*") \
                        .classes("hidden") \
                        .bind_visibility_from(vm, "model", backward=lambda m: m.can_attach)
                    attach_btn = ui.button(icon="attach_file").props("flat round dense") \
                        .bind_enabled_from(vm, "model", backward=lambda m: m.can_attach) \
                        .on("click", lambda: upload.pick_files())

                    draft = ui.textarea(placeholder="Type your message…").classes("flex-1") \
                        .props("outlined autogrow dense")
                    draft.on_value_change(lambda e: vm.set_draft(e.value or ""))
                    draft.bind_value_from(vm, "model", backward=lambda m: m.draft)

                    send = ui.button(icon="send", on_click=vm.send_command.execute_async) \
                        .props("unelevated color=primary round dense") \
                        .bind_enabled_from(vm, "model", backward=lambda m: m.can_send)

        # Right rail: session settings
        with ui.column().classes("w-72 gap-2"):
            with card():
                section_header("Session", subtitle=None)
                ui.label("Model").classes("text-xs text-[var(--text-3)] mt-2")
                llm_sel = ui.select([], with_input=True).props("outlined dense").classes("w-full")
                def _refresh_llms(_=None) -> None:
                    # Populate options on first persona/llm load. Real LLM list from llm_svc would be cached;
                    # for simplicity refresh on every model change.
                    pass  # llm options populated lazily via vm.load_options_command — keep static for now
                vm.model_changed.subscribe(_refresh_llms)

                ui.label("Temperature").classes("text-xs text-[var(--text-3)] mt-2")
                ui.slider(min=0.0, max=1.0, step=0.05).props("color=primary dense") \
                    .bind_value_from(vm, "model", backward=lambda m: m.temperature) \
                    .on_value_change(lambda e: vm.set_temperature(float(e.value)))

                with ui.row().classes("items-center gap-2 mt-3"):
                    ui.switch("TTS").bind_value_from(vm, "model", backward=lambda m: m.tts_enabled) \
                        .on_value_change(lambda _: vm.toggle_tts())
                    ui.label().bind_text_from(vm, "model",
                                               backward=lambda m: "vision" if m.is_vision_llm else "no vision") \
                        .classes("text-xs text-[var(--text-3)] ml-auto")


def _on_upload(vm: ChatVM):
    async def _cb(e) -> None:
        data = e.content.read()
        vm.attach_image_bytes(data)
    return _cb
```

- [ ] **Step 3: Wire DI + renderer**

```python
# core/di.py
from models.services.chat_service import ChatService
from models.services.text_to_speech_service import TextToSpeechService
from models.services.persona_service import PersonaService
from viewmodels.chat.chat_vm import ChatVM
...
chat_svc = ChatService(http)
persona_svc = PersonaService(http)
tts_svc = TextToSpeechService(http)
chat = ChatVM(hub, dispatcher, chat_svc, llm_svc, persona_svc, tts_svc, settings, notifications)
pages = [home, chat, polyglot, profile, assessment]
```

```python
# views/app_shell.py
from views.chat.chat_view import render as render_chat
PAGE_RENDERERS["chat"] = render_chat
```

- [ ] **Step 4: Smoke**

Boot, log in, navigate to Chat. Send a message. Observe streaming tokens populating the assistant bubble (or full response if backend lacks `/chat/stream`). Switch to a vision LLM via the right rail (if the dropdown is wired) — attach button enables; upload an image; send a vision message.

- [ ] **Step 5: Commit + gate**

```bash
git add frontend/viewmodels/chat frontend/views/chat \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(chat): full MVVM chat with streaming, persona, vision, TTS toggle"
git commit --allow-empty -m "chore: phase 5 gate — chat end-to-end with streaming + vision"
```

---

# Phase 6 — Content trio (Content Gen, Rewrite, Review)

**Goal of this phase:** three structurally identical pages: request + result + one long-running command + optional TTS. They share a common shape so we templatize. All three become `ComponentVMOf[<RequestModel>]` (no children, no aggregates beyond TTS audio).

**Phase 6 gate:** all three pages generate, display result, optionally speak result; navigation between them feels consistent.

---

## Task 6.1: Refactor `content_gen_service`, `rewrite_content_service`, `review_writing_service`, `content_service` to async/instance

**Files:**
- Modify: `frontend/models/services/content_gen_service.py`
- Modify: `frontend/models/services/rewrite_content_service.py`
- Modify: `frontend/models/services/review_writing_service.py`
- Modify: `frontend/models/services/content_service.py`

Apply the same async/instance refactor template from Tasks 3.1 and 4.1. Each service: constructor takes `httpx.AsyncClient`; methods are `async def` returning typed schema objects.

- [ ] **Step 1: Rewrite each per the established pattern**

For brevity here, a canonical example for one (`content_gen_service.py`):

```python
from __future__ import annotations
import httpx

from models.schemas.content_gen import ContentGenRequest, ContentGenResponse


class ContentGenService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def generate(self, req: ContentGenRequest) -> ContentGenResponse:
        r = await self._http.post("/content/generate", json=req.model_dump()); r.raise_for_status()
        return ContentGenResponse.model_validate(r.json())
```

Mirror the same shape for `rewrite_content_service.py` (`POST /content/rewrite`), `review_writing_service.py` (`POST /content/review`), `content_service.py` (utility — likely `GET /content/topics` or similar — preserve current callsites).

- [ ] **Step 2: Verify each endpoint against backend router files; adjust paths**

```bash
grep -rln 'content_gen\|rewrite\|review' frontend/../backend/routers --include='*.py'
```

- [ ] **Step 3: Commit**

```bash
cd frontend
git add models/services/{content_gen,rewrite_content,review_writing,content}_service.py
git commit -m "refactor(services): async/instance content-gen / rewrite / review / content services"
```

---

## Task 6.2: Build ContentGenVM + view

**Files:**
- Create: `frontend/viewmodels/content_gen/__init__.py`
- Create: `frontend/viewmodels/content_gen/content_gen_vm.py`
- Create: `frontend/views/content_gen/__init__.py`
- Create: `frontend/views/content_gen/content_gen_view.py`

- [ ] **Step 1: VM**

```python
# viewmodels/content_gen/content_gen_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx.components import ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from models.services.content_gen_service import ContentGenService
from models.services.llm_service import LLMService
from models.services.language_service import LanguageService
from models.services.text_to_speech_service import TextToSpeechService
from models.schemas.content_gen import ContentGenRequest, ContentGenResponse


@dataclass(frozen=True)
class ContentGenState:
    language: str = ""
    topic: str = ""
    skill_level: str = "B1"
    temperature: float = 0.5
    llm_id: str = ""
    result: Optional[str] = None
    in_flight: bool = False
    languages: tuple[str, ...] = ()
    llms: tuple[tuple[str, str], ...] = ()  # (id, display_name)
    tts_enabled: bool = False


class ContentGenVM(ComponentVMOf[ContentGenState], PageVM):  # type: ignore[misc]
    route = "content_gen"

    def __init__(
        self, hub: MessageHub, dispatcher: RxDispatcher,
        svc: ContentGenService, llm_svc: LLMService, lang_svc: LanguageService,
        tts_svc: TextToSpeechService, notifications: NotificationCenterVM,
    ) -> None:
        super().__init__(name="content-gen", services=(hub, dispatcher), model=ContentGenState())
        self._svc, self._llm, self._lang, self._tts, self._notify = svc, llm_svc, lang_svc, tts_svc, notifications

        self.load_command = RelayCommand(execute=self._load)
        self.generate_command = RelayCommand(
            execute=self._generate,
            can_execute=lambda: bool(self.model.language and self.model.topic and self.model.llm_id and not self.model.in_flight),
        )
        self.speak_command = RelayCommand(
            execute=self._speak,
            can_execute=lambda: bool(self.model.result and self.model.language),
        )

    async def _load(self) -> None:
        langs = [L.language_name for L in await self._lang.list()]
        llms = await self._llm.get_content()
        if not (langs and llms):
            self._notify.push_error("Could not load options.")
            return
        self.model = replace(self.model,
                              languages=tuple(langs),
                              llms=tuple((m.id, m.display_name()) for m in llms),
                              language=langs[0], llm_id=llms[0].id)

    async def _generate(self) -> None:
        self.model = replace(self.model, in_flight=True, result=None)
        try:
            resp = await self._svc.generate(ContentGenRequest(
                language=self.model.language, topic=self.model.topic,
                skill_level=self.model.skill_level, llm_id=self.model.llm_id,
                temperature=self.model.temperature,
            ))
            self.model = replace(self.model, result=resp.content, in_flight=False)
        except Exception as e:
            self.model = replace(self.model, in_flight=False)
            self._notify.push_error(f"Generation failed: {e}")

    async def _speak(self) -> None:
        if not self.model.result:
            return
        from models.schemas.text_to_speech import TextToSpeechRequest
        try:
            await self._tts.synthesize(TextToSpeechRequest(text=self.model.result, language=self.model.language))
            self._notify.push_info("Audio ready.")
        except Exception as e:
            self._notify.push_error(f"TTS failed: {e}")
```

- [ ] **Step 2: View**

```python
# views/content_gen/content_gen_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.content_gen.content_gen_vm import ContentGenVM, ContentGenState
from views.theme.components import card, pill_button, section_header


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "content_gen")
    assert isinstance(vm, ContentGenVM)
    if not vm.model.languages:
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_command.execute_async())

    with card():
        section_header("Content reading", subtitle="Generate a passage at your level")
        with ui.row().classes("gap-3 w-full"):
            lang = ui.select([], label="Language").props("outlined dense").classes("flex-1")
            level = ui.select(["A1", "A2", "B1", "B2", "C1", "C2"], label="Level").props("outlined dense").classes("flex-1")
            llm = ui.select([], label="Model").props("outlined dense").classes("flex-1")

        def _refresh(_=None) -> None:
            lang._props["options"] = list(vm.model.languages); lang.update(); lang.value = vm.model.language
            llm._props["options"] = [n for _, n in vm.model.llms]; llm.update()
            llm.value = next((n for i, n in vm.model.llms if i == vm.model.llm_id), None)
            level.value = vm.model.skill_level
        vm.model_changed.subscribe(_refresh); _refresh()

        lang.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, language=e.value or "")))
        level.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, skill_level=e.value or "B1")))
        llm.on_value_change(lambda e: setattr(vm, "model", replace(vm.model,
                            llm_id=next((i for i, n in vm.model.llms if n == e.value), ""))))

        topic = ui.input("Topic").props("outlined dense").classes("w-full mt-3") \
            .bind_value_from(vm, "model", backward=lambda m: m.topic)
        topic.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, topic=e.value or "")))

        with ui.row().classes("items-center gap-3 mt-3"):
            ui.label("Temperature").classes("text-xs text-[var(--text-3)]")
            ui.slider(min=0.0, max=1.0, step=0.05).props("color=primary dense").classes("w-40") \
                .bind_value_from(vm, "model", backward=lambda m: m.temperature) \
                .on_value_change(lambda e: setattr(vm, "model", replace(vm.model, temperature=float(e.value))))
            ui.space()
            gen = pill_button("Generate", variant="primary", on_click=vm.generate_command.execute_async)
            gen.bind_enabled_from(vm, "model",
                backward=lambda m: bool(m.language and m.topic and m.llm_id and not m.in_flight))

    with card().classes("mt-4").bind_visibility_from(vm, "model", backward=lambda m: m.result is not None):
        section_header("Result")
        ui.label().bind_text_from(vm, "model", backward=lambda m: m.result or "") \
            .classes("text-sm whitespace-pre-wrap")
        with ui.row().classes("justify-end mt-3"):
            pill_button("🔊 Speak", on_click=vm.speak_command.execute_async)
```

- [ ] **Step 3: Wire DI + renderer**

```python
# core/di.py
from models.services.content_gen_service import ContentGenService
from viewmodels.content_gen.content_gen_vm import ContentGenVM
content_gen_svc = ContentGenService(http)
content_gen = ContentGenVM(hub, dispatcher, content_gen_svc, llm_svc, lang_svc, tts_svc, notifications)
pages = [home, chat, content_gen, polyglot, profile, assessment]
```

```python
# views/app_shell.py
from views.content_gen.content_gen_view import render as render_content_gen
PAGE_RENDERERS["content_gen"] = render_content_gen
```

- [ ] **Step 4: Commit**

```bash
git add frontend/viewmodels/content_gen frontend/views/content_gen \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(content_gen): generate-and-display page with TTS"
```

---

## Task 6.3: Build RewriteContentVM + view (mirrors ContentGen)

**Files:**
- Create: `frontend/viewmodels/rewrite_content/__init__.py`
- Create: `frontend/viewmodels/rewrite_content/rewrite_content_vm.py`
- Create: `frontend/views/rewrite_content/__init__.py`
- Create: `frontend/views/rewrite_content/rewrite_content_view.py`

- [ ] **Step 1: VM (mirrors ContentGenVM shape, but input is a passage and "register/style" instead of "topic")**

```python
# viewmodels/rewrite_content/rewrite_content_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx.components import ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from models.services.rewrite_content_service import RewriteContentService
from models.services.llm_service import LLMService
from models.services.text_to_speech_service import TextToSpeechService
from models.schemas.rewrite_content import RewriteContentRequest


@dataclass(frozen=True)
class RewriteState:
    source_text: str = ""
    target_style: str = "formal"
    llm_id: str = ""
    temperature: float = 0.5
    result: Optional[str] = None
    in_flight: bool = False
    llms: tuple[tuple[str, str], ...] = ()


class RewriteContentVM(ComponentVMOf[RewriteState], PageVM):  # type: ignore[misc]
    route = "rewrite_content"

    def __init__(self, hub, dispatcher, svc: RewriteContentService, llm_svc: LLMService,
                 tts_svc: TextToSpeechService, notifications: NotificationCenterVM) -> None:
        super().__init__(name="rewrite", services=(hub, dispatcher), model=RewriteState())
        self._svc, self._llm, self._tts, self._notify = svc, llm_svc, tts_svc, notifications

        self.load_command = RelayCommand(execute=self._load)
        self.rewrite_command = RelayCommand(execute=self._rewrite,
            can_execute=lambda: bool(self.model.source_text.strip() and self.model.llm_id and not self.model.in_flight))
        self.speak_command = RelayCommand(execute=self._speak,
            can_execute=lambda: bool(self.model.result))

    async def _load(self) -> None:
        llms = await self._llm.get_content()
        if not llms:
            self._notify.push_error("Could not load LLMs."); return
        self.model = replace(self.model,
                              llms=tuple((m.id, m.display_name()) for m in llms),
                              llm_id=llms[0].id)

    async def _rewrite(self) -> None:
        self.model = replace(self.model, in_flight=True, result=None)
        try:
            resp = await self._svc.rewrite(RewriteContentRequest(
                source_text=self.model.source_text, target_style=self.model.target_style,
                llm_id=self.model.llm_id, temperature=self.model.temperature,
            ))
            self.model = replace(self.model, result=resp.content, in_flight=False)
        except Exception as e:
            self.model = replace(self.model, in_flight=False)
            self._notify.push_error(f"Rewrite failed: {e}")

    async def _speak(self) -> None:
        if not self.model.result: return
        from models.schemas.text_to_speech import TextToSpeechRequest
        try:
            await self._tts.synthesize(TextToSpeechRequest(text=self.model.result, language="en"))
            self._notify.push_info("Audio ready.")
        except Exception as e:
            self._notify.push_error(f"TTS failed: {e}")
```

- [ ] **Step 2: View — analogous to content_gen_view, replace topic input with a multi-line textarea and add a style picker**

```python
# views/rewrite_content/rewrite_content_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.rewrite_content.rewrite_content_vm import RewriteContentVM
from views.theme.components import card, pill_button, section_header


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "rewrite_content")
    assert isinstance(vm, RewriteContentVM)
    if not vm.model.llms:
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_command.execute_async())

    with card():
        section_header("Rewrite content", subtitle="Paste a passage and adjust its register")
        src = ui.textarea("Source passage").props("outlined autogrow").classes("w-full") \
            .bind_value_from(vm, "model", backward=lambda m: m.source_text)
        src.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, source_text=e.value or "")))

        with ui.row().classes("gap-3 mt-3 w-full"):
            style = ui.select(["formal", "casual", "academic", "humorous", "concise"], label="Target style") \
                .props("outlined dense").classes("flex-1")
            llm = ui.select([], label="Model").props("outlined dense").classes("flex-1")

        def _refresh(_=None) -> None:
            llm._props["options"] = [n for _, n in vm.model.llms]; llm.update()
            llm.value = next((n for i, n in vm.model.llms if i == vm.model.llm_id), None)
            style.value = vm.model.target_style
        vm.model_changed.subscribe(_refresh); _refresh()

        style.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, target_style=e.value or "formal")))
        llm.on_value_change(lambda e: setattr(vm, "model", replace(vm.model,
                            llm_id=next((i for i, n in vm.model.llms if n == e.value), ""))))

        with ui.row().classes("justify-end mt-3"):
            btn = pill_button("Rewrite", variant="primary", on_click=vm.rewrite_command.execute_async)
            btn.bind_enabled_from(vm, "model",
                backward=lambda m: bool(m.source_text.strip() and m.llm_id and not m.in_flight))

    with card().classes("mt-4").bind_visibility_from(vm, "model", backward=lambda m: m.result is not None):
        section_header("Rewritten")
        ui.label().bind_text_from(vm, "model", backward=lambda m: m.result or "") \
            .classes("text-sm whitespace-pre-wrap")
        with ui.row().classes("justify-end mt-3"):
            pill_button("🔊 Speak", on_click=vm.speak_command.execute_async)
```

- [ ] **Step 3: Wire DI + renderer + commit**

```python
# core/di.py
from models.services.rewrite_content_service import RewriteContentService
from viewmodels.rewrite_content.rewrite_content_vm import RewriteContentVM
rewrite_svc = RewriteContentService(http)
rewrite = RewriteContentVM(hub, dispatcher, rewrite_svc, llm_svc, tts_svc, notifications)
pages = [home, chat, content_gen, rewrite, polyglot, profile, assessment]
```

```python
# views/app_shell.py
from views.rewrite_content.rewrite_content_view import render as render_rewrite
PAGE_RENDERERS["rewrite_content"] = render_rewrite
```

```bash
git add frontend/viewmodels/rewrite_content frontend/views/rewrite_content \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(rewrite_content): page wired with style picker + TTS"
```

---

## Task 6.4: Build ReviewWritingVM + view

**Files:**
- Create: `frontend/viewmodels/review_writing/__init__.py`
- Create: `frontend/viewmodels/review_writing/review_writing_vm.py`
- Create: `frontend/views/review_writing/__init__.py`
- Create: `frontend/views/review_writing/review_writing_view.py`

Structurally identical to RewriteContentVM. Inputs: source passage + "language being learned" + skill level. Output: backend's review (feedback text). Use the same pattern.

- [ ] **Step 1: VM (same shape as rewrite, swap `target_style`/`llm_id` for `language`/`skill_level`/`llm_id`)**

```python
# viewmodels/review_writing/review_writing_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Optional

from vmx.components import ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from models.services.review_writing_service import ReviewWritingService
from models.services.language_service import LanguageService
from models.services.llm_service import LLMService
from models.schemas.review_writing import ReviewWritingRequest


@dataclass(frozen=True)
class ReviewState:
    source_text: str = ""
    language: str = ""
    skill_level: str = "B1"
    llm_id: str = ""
    temperature: float = 0.3
    result: Optional[str] = None
    in_flight: bool = False
    languages: tuple[str, ...] = ()
    llms: tuple[tuple[str, str], ...] = ()


class ReviewWritingVM(ComponentVMOf[ReviewState], PageVM):  # type: ignore[misc]
    route = "review_writing"

    def __init__(self, hub, dispatcher, svc: ReviewWritingService,
                 llm_svc: LLMService, lang_svc: LanguageService,
                 notifications: NotificationCenterVM) -> None:
        super().__init__(name="review", services=(hub, dispatcher), model=ReviewState())
        self._svc, self._llm, self._lang, self._notify = svc, llm_svc, lang_svc, notifications
        self.load_command = RelayCommand(execute=self._load)
        self.review_command = RelayCommand(execute=self._review,
            can_execute=lambda: bool(self.model.source_text.strip() and self.model.language and self.model.llm_id and not self.model.in_flight))

    async def _load(self) -> None:
        langs = [L.language_name for L in await self._lang.list()]
        llms = await self._llm.get_content()
        if not (langs and llms):
            self._notify.push_error("Could not load options."); return
        self.model = replace(self.model,
                              languages=tuple(langs),
                              llms=tuple((m.id, m.display_name()) for m in llms),
                              language=langs[0], llm_id=llms[0].id)

    async def _review(self) -> None:
        self.model = replace(self.model, in_flight=True, result=None)
        try:
            resp = await self._svc.review(ReviewWritingRequest(
                source_text=self.model.source_text, language=self.model.language,
                skill_level=self.model.skill_level,
                llm_id=self.model.llm_id, temperature=self.model.temperature,
            ))
            self.model = replace(self.model, result=resp.feedback, in_flight=False)
        except Exception as e:
            self.model = replace(self.model, in_flight=False)
            self._notify.push_error(f"Review failed: {e}")
```

- [ ] **Step 2: View — copy `rewrite_content_view.py`, swap the style picker for a language + skill picker**

```python
# views/review_writing/review_writing_view.py
from nicegui import ui
from dataclasses import replace

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.review_writing.review_writing_vm import ReviewWritingVM
from views.theme.components import card, pill_button, section_header


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "review_writing")
    assert isinstance(vm, ReviewWritingVM)
    if not vm.model.languages:
        from asyncio import get_event_loop
        get_event_loop().create_task(vm.load_command.execute_async())

    with card():
        section_header("Review my writing", subtitle="Get feedback on a passage you wrote")
        src = ui.textarea("Your writing").props("outlined autogrow").classes("w-full") \
            .bind_value_from(vm, "model", backward=lambda m: m.source_text)
        src.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, source_text=e.value or "")))

        with ui.row().classes("gap-3 mt-3 w-full"):
            lang = ui.select([], label="Language").props("outlined dense").classes("flex-1")
            level = ui.select(["A1", "A2", "B1", "B2", "C1", "C2"], label="Skill level") \
                .props("outlined dense").classes("flex-1")
            llm = ui.select([], label="Model").props("outlined dense").classes("flex-1")

        def _refresh(_=None) -> None:
            lang._props["options"] = list(vm.model.languages); lang.update(); lang.value = vm.model.language
            llm._props["options"] = [n for _, n in vm.model.llms]; llm.update()
            llm.value = next((n for i, n in vm.model.llms if i == vm.model.llm_id), None)
            level.value = vm.model.skill_level
        vm.model_changed.subscribe(_refresh); _refresh()

        lang.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, language=e.value or "")))
        level.on_value_change(lambda e: setattr(vm, "model", replace(vm.model, skill_level=e.value or "B1")))
        llm.on_value_change(lambda e: setattr(vm, "model", replace(vm.model,
                            llm_id=next((i for i, n in vm.model.llms if n == e.value), ""))))

        with ui.row().classes("justify-end mt-3"):
            btn = pill_button("Get feedback", variant="primary", on_click=vm.review_command.execute_async)
            btn.bind_enabled_from(vm, "model",
                backward=lambda m: bool(m.source_text.strip() and m.language and m.llm_id and not m.in_flight))

    with card().classes("mt-4").bind_visibility_from(vm, "model", backward=lambda m: m.result is not None):
        section_header("Feedback")
        ui.label().bind_text_from(vm, "model", backward=lambda m: m.result or "") \
            .classes("text-sm whitespace-pre-wrap")
```

- [ ] **Step 3: Wire + commit + gate**

```python
# core/di.py
from models.services.review_writing_service import ReviewWritingService
from viewmodels.review_writing.review_writing_vm import ReviewWritingVM
review_svc = ReviewWritingService(http)
review = ReviewWritingVM(hub, dispatcher, review_svc, llm_svc, lang_svc, notifications)
pages = [home, chat, content_gen, rewrite, review, polyglot, profile, assessment]
```

```python
# views/app_shell.py
from views.review_writing.review_writing_view import render as render_review
PAGE_RENDERERS["review_writing"] = render_review
```

```bash
git add frontend/viewmodels/review_writing frontend/views/review_writing \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(review_writing): get-feedback page"
git commit --allow-empty -m "chore: phase 6 gate — content trio (gen / rewrite / review)"
```

---

# Phase 7 — Admin + cutover

**Goal of this phase:** small Admin page (`GroupVM[FeatureFlagVM]`), delete all legacy Streamlit artifacts, finalize cleanup, run final greps, squash-merge to `develop`.

**Phase 7 gate:** clean repo (no streamlit imports / `asyncio.run` / `_sync` / `.instance()` / `st.session_state`); all 4 import-linter contracts pass; mypy strict on M/VM/core/views.theme is clean; Docker image rebuilds and `docker compose up` serves the new app on `FRONTEND_PORT`.

---

## Task 7.1: Build AdminVM + view

**Files:**
- Create: `frontend/viewmodels/admin/__init__.py`
- Create: `frontend/viewmodels/admin/admin_vm.py`
- Create: `frontend/views/admin/__init__.py`
- Create: `frontend/views/admin/admin_view.py`

For now, the admin page is a minimal feature-flag viewer + a button to ping each backend health endpoint. Real admin functions can be added incrementally later.

- [ ] **Step 1: VM**

```python
# viewmodels/admin/admin_vm.py
from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple

from vmx.components import GroupVM, ComponentVMOf
from vmx.commands import RelayCommand
from vmx.services import MessageHub, RxDispatcher

from viewmodels.app_shell_vm import PageVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM
from viewmodels.shell.user_session_vm import UserSessionVM
from models.services.ping_service import PingService


@dataclass(frozen=True)
class FeatureFlag:
    name: str
    enabled: bool


class FeatureFlagVM(ComponentVMOf[FeatureFlag]):
    pass


class AdminVM(GroupVM[FeatureFlagVM], PageVM):  # type: ignore[misc]
    route = "admin"

    def __init__(self, hub: MessageHub, dispatcher: RxDispatcher,
                 ping_svc: PingService, session: UserSessionVM,
                 notifications: NotificationCenterVM) -> None:
        super().__init__(name="admin", services=(hub, dispatcher))
        self._ping = ping_svc
        self._session = session
        self._notify = notifications

        for name, enabled in [("vision-chat", True), ("tts", True), ("polyglot-3d", True),
                               ("streaming-chat", True)]:
            self.add_child(FeatureFlagVM.builder().name(f"flag-{name}")
                .model(FeatureFlag(name=name, enabled=enabled))
                .services(hub, dispatcher).build()
                if hasattr(FeatureFlagVM, "builder")
                else FeatureFlagVM(hub, dispatcher) ) # fallback ctor form

        self.ping_command = RelayCommand(execute=self._ping_backend)

    async def _ping_backend(self) -> None:
        r = await self._ping.ping()
        if r.ok:
            self._notify.push_success(f"Backend OK: {r.message}")
        else:
            self._notify.push_error(f"Backend ping failed: {r.message}")
```

(If `FeatureFlagVM.builder()` isn't supported, instantiate via plain ctor and set `.model` after — pattern from quickref.)

- [ ] **Step 2: View**

```python
# views/admin/admin_view.py
from nicegui import ui

from viewmodels.app_shell_vm import AppShellVM
from viewmodels.admin.admin_vm import AdminVM
from views.theme.components import card, pill_button, section_header, chip


def render(shell: AppShellVM) -> None:
    vm = next(p for p in shell.children if p.route == "admin")
    assert isinstance(vm, AdminVM)

    with card():
        section_header("Admin", subtitle="Feature flags & backend health")
        with ui.row().classes("flex-wrap gap-2 w-full mt-2"):
            for c in vm.children:
                tone = "success" if c.model.enabled else "neutral"
                chip(f"{c.model.name} · {'on' if c.model.enabled else 'off'}", tone=tone)
        with ui.row().classes("mt-4 justify-end"):
            pill_button("Ping backend", variant="primary", on_click=vm.ping_command.execute_async)
```

- [ ] **Step 3: Wire DI + renderer**

```python
# core/di.py
from viewmodels.admin.admin_vm import AdminVM
from models.services.ping_service import PingService
ping_svc = PingService(http)
admin = AdminVM(hub, dispatcher, ping_svc, session, notifications)
pages = [home, chat, content_gen, rewrite, review, polyglot, profile, assessment, admin]
```

```python
# views/app_shell.py
from views.admin.admin_view import render as render_admin
PAGE_RENDERERS["admin"] = render_admin
```

- [ ] **Step 4: Commit**

```bash
git add frontend/viewmodels/admin frontend/views/admin \
        frontend/core/di.py frontend/views/app_shell.py
git commit -m "feat(admin): minimal admin page (flags + backend ping)"
```

---

## Task 7.2: Delete legacy Streamlit artifacts

**Files:**
- Delete: `frontend/app.py`
- Delete: `frontend/components/` (entire tree)
- Delete: `frontend/models/services/state_service.py`
- Delete: `frontend/models/services/notification_service.py`
- Delete: `frontend/.streamlit/` (entire tree)
- Delete: `frontend/utils/` (entire tree — `http_utils.py`, `image_utils.py`, `logger.py`)
- Delete: `frontend/viewmodels/ping/` and `frontend/views/ping/` and `frontend/models/services/ping_service.py` — *no, keep ping_service.py for AdminVM; only delete the smoke VM/view*. Actually we still use `PingService` from AdminVM, so keep `ping_service.py`. Delete only `viewmodels/ping/` and `views/ping/` and the `/ping` route in `main.py`.

- [ ] **Step 1: Delete in order**

```bash
cd frontend
git rm frontend/app.py
git rm -r frontend/components frontend/.streamlit frontend/utils
git rm frontend/models/services/state_service.py frontend/models/services/notification_service.py
git rm -r frontend/viewmodels/ping frontend/views/ping
```

Wait — `git rm` paths above include `frontend/` prefix because we're at the repo root (worktree root). Adjust based on where you're running:

```bash
cd /Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul
git rm frontend/app.py
git rm -r frontend/components frontend/.streamlit frontend/utils
git rm frontend/models/services/state_service.py frontend/models/services/notification_service.py
git rm -r frontend/viewmodels/ping frontend/views/ping
```

- [ ] **Step 2: Remove the `/ping` route from `main.py`**

Open `frontend/main.py`, delete the entire `@ui.page("/ping")` function body.

- [ ] **Step 3: Remove the `streamlit*` deps**

In `frontend/pyproject.toml`, confirm `streamlit`, `streamlit-option-menu`, `streamlit-modal`, `sqlmodel`, `requests` are gone (they should have been removed in Task 0.2). If anything regressed, delete now.

```bash
cd frontend && poetry lock --no-update && poetry install --sync
```

- [ ] **Step 4: Re-run import-linter + tests + mypy**

```bash
cd frontend
poetry run lint-imports
poetry run pytest -q
poetry run mypy --strict models viewmodels core views/theme
```

Expected: all green. If imports break because something still tried to import a deleted module, grep and fix:

```bash
grep -rln 'app\.py\|components/\|state_service\|notification_service\|utils/' --include='*.py' .
```

- [ ] **Step 5: Commit**

```bash
git add -A frontend/
git commit -m "chore(cleanup): delete Streamlit app, components, utils, state/notification services"
```

---

## Task 7.3: Final repo greps + DoD verification

- [ ] **Step 1: Grep checks (all must return zero matches in `frontend/`)**

```bash
cd /Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul/frontend
echo '=== import streamlit ==='   ; grep -rln 'import streamlit'    --include='*.py' .
echo '=== asyncio.run in render ===' ; grep -rln 'asyncio\.run('   --include='*.py' views/ viewmodels/
echo '=== *_sync wrappers ==='    ; grep -rln '_sync\b\|\.list_sync\|\.run_until_complete' --include='*.py' .
echo '=== ClassName.instance() ===' ; grep -rln '\.instance()'      --include='*.py' viewmodels/ views/
echo '=== st.session_state ==='   ; grep -rln 'st\.session_state'   --include='*.py' .
```

Expected: every echo prints its header and no matching files.

- [ ] **Step 2: Docker rebuild + boot**

```bash
cd /Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul
docker compose build frontend
docker compose up -d
open "http://localhost:${FRONTEND_PORT}"
```

- [ ] **Step 3: Manual full-smoke checklist**

Tick each as done:

1. Open URL, see login panel.
2. Click "Create an account" — register a new user end-to-end.
3. Log in with the new user — home dashboard renders (greeting, quick actions, empty skill cards).
4. Navigate to **Profile** — data loads; edit a field; click Save; toast confirms.
5. Navigate to **Assessment** — answer questions; submit; score toast + history reflected on Profile.
6. Navigate to **Chat** — send a message; observe streaming or full response; toggle TTS; (if a vision LLM is configured) upload an image and send a vision message.
7. Navigate to **Content** — generate a passage; speak it.
8. Navigate to **Rewrite** — rewrite a passage in a different register.
9. Navigate to **Review** — submit your writing; receive feedback.
10. Navigate to **Polyglot** — generate puzzle, type two translations, submit, see similarities + 2D/3D toggle.
11. Navigate to **Admin** (if user_type=admin) — flags visible; ping button works.
12. Log out (header avatar menu) — login panel reappears; reload URL — still logged out (storage cleared).
13. Theme toggle cycles `system → light → dark → system` and persists across reload.

- [ ] **Step 4: Commit gate marker**

```bash
git commit --allow-empty -m "chore: phase 7 gate — full smoke, lint+type+test green, repo grep clean"
```

---

## Task 7.4: Squash-merge to develop (optional; offer)

This step writes no code — it's the handoff to the user. Do NOT push or merge without explicit go-ahead.

- [ ] **Step 1: Confirm branch state**

```bash
cd /Users/kaveh/repos/LinguAI/.claude/worktrees/frontend-overhaul
git log --oneline develop..HEAD | head -40
git status
```

- [ ] **Step 2: Surface the merge command to the user (don't execute)**

Report to the user:

> "Phase 7 complete. Ready to merge `worktree-frontend-overhaul` to `develop`. Suggested command:
> ```bash
> git -C /Users/kaveh/repos/LinguAI checkout develop
> git -C /Users/kaveh/repos/LinguAI merge --squash worktree-frontend-overhaul
> git -C /Users/kaveh/repos/LinguAI commit -m "feat(frontend): MVVM overhaul (NiceGUI + VMx)"
> ```
> Execute this when you're ready; do not run it for me."

---

# Self-review checklist (post-plan)

After writing the plan, the writing-plans skill requires a self-review pass. Findings + fixes inline below — nothing needs to be re-run.

- **Spec coverage:** every section of the spec maps to tasks above.
  - §3 Key decisions → Task 0.2 (deps), 0.3 (folder topology), Task 0.5 + Task 0.10 (visual direction), Task 3.x (worked example), Phase 7 (cutover).
  - §4 Architecture → Tasks 0.4–0.11.
  - §5 Folder structure → Task 0.3.
  - §6 App shell → Tasks 0.10, 0.11.
  - §7 Per-page MVVM pattern → Phase 3 fully worked example.
  - §8 Cross-cutting (auth, async, notifications, testing, lint) → Tasks 0.2 (lint), 0.4 (http), 0.7 (NotificationCenterVM), 2.1 (auth), 0.6 / 8.x tests throughout.
  - §9 Migration plan → Phases 0–7 mirror the spec's phase plan.
  - §10 Risks → mitigations applied (e.g., Task 0.1 VMx recon; fallback in Task 5.1 for streaming).
  - §11 Open questions → carried as inline notes where they touch tasks; #9 (VMx exact types) is addressed by Task 0.1 + the multi-inheritance fallback note in Phase 3.
  - §12 DoD → Task 7.3 enumerates every grep + manual smoke.

- **Placeholder scan:** code blocks are complete; no `TODO` / `TBD` left except one intentional `# TODO(phase-7-backend): real token issuance` (called out explicitly in Task 2.1 Step 2 as a deferred backend dependency, with the path forward documented).

- **Type consistency:** `ComponentVMOf[T]`, `CompositeVM[T]`, `GroupVM[T]`, `AggregateVM3[A,B,C]`, `RelayCommand` (with `execute_async`/`execute` + `can_execute` + optional `can_execute_trigger`), `MessageHub`, `RxDispatcher` — used uniformly across all tasks. Where VMx's actual surface differs from these names, Task 0.1's quickref captures the truth and the engineer adjusts locally before continuing.

- **Cross-task references:** every `pages = [...]` list is reassembled in full (not "add to existing list") so out-of-order reading isn't fatal. Every renderer registration is shown in full. DI imports are repeated each task that adds a service.

---

# Plan complete

**File:** `docs/superpowers/plans/2026-05-30-frontend-mvvm-overhaul.md`
**Tasks:** Phase 0 (12) → Phase 1 (1) → Phase 2 (9) → Phase 3 (8) → Phase 4 (4) → Phase 5 (4) → Phase 6 (4) → Phase 7 (4) = **46 tasks total** across 8 phases.
**Commits expected:** ~60 (one per task + phase-gate empty commits).






