# VMx: Submodule → PyPI Dependency Migration Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the `external/vmx` git submodule (consumed by `frontend/` as a Poetry path dependency) with the conventional published PyPI release `vmx`, and update all build files and documentation accordingly.

**Architecture:** `frontend/pyproject.toml` currently pins VMx as an editable path dep against the submodule at `external/vmx/langs/python` (commit `e2b23f8`, version `2.1.0`). The published package on PyPI is `vmx` **2.6.0** — the submodule version `2.1.0` was never published, so this is also a `2.1.0 → 2.6.0` upgrade. All seven primitives the frontend imports (`CompositeVM`, `ComponentVM`, `ComponentVMOf`, `MessageHub`, `RxDispatcher`, `RelayCommand`, `GroupVM`) are still exported in 2.6.0, and the 2.2→2.6 changelog is additive/bugfix-only with no breaking removals — so the API risk is low but must be verified, not assumed. We change the dependency, regenerate the lock, strip VMx out of the Docker build (the build context was widened to the repo root *solely* to reach the submodule), remove the submodule from git, and rewrite the docs that describe the submodule workflow.

**Tech Stack:** Python 3.10, Poetry 2.4.1, NiceGUI, Docker Compose, `vmx` (PyPI), import-linter, mypy, pytest.

## Global Constraints

- **Version pin:** `vmx = "^2.6.0"` in `frontend/pyproject.toml` (caret → `>=2.6.0,<3.0.0`). Matches the file's existing style (`nicegui = "^2.0"`, `httpx = "^0.27"`).
- **Pure PyPI:** No editable/local-dev path for VMx is committed or documented. The submodule is fully removed; no `external/vmx` directory, `.gitmodules` entry, or path/git dependency remains anywhere.
- **No behavior change in frontend code:** The 29 `from vmx import …` sites are *not* edited — the import surface is unchanged. If any 2.6.0 API divergence surfaces during verification, STOP and report; do not silently patch consumer code as part of this migration.
- **Verification commands run from `frontend/`** using local Poetry (2.4.1 is installed) unless a step says otherwise. Docker verification uses the repo root.
- **Frontend tests** are self-contained (`respx` mocks the backend); no live backend/db is required to run them.

---

## File Structure

Files created or modified, grouped by the task that owns them:

| File | Change | Owning task |
|---|---|---|
| `frontend/pyproject.toml` | Line 11: path dep → `vmx = "^2.6.0"` | Task 1 |
| `frontend/poetry.lock` | Regenerated — vmx resolved from PyPI with wheel hashes | Task 1 |
| `frontend/Dockerfile` | Remove `COPY external/vmx …` (line 15); rewrite the comment block (lines 2-6) | Task 2 |
| `docker-compose.yml` | Remove `- ./external/vmx:/app/external/vmx` bind mount (line 69) | Task 2 |
| `docker-compose.ollama-localhost.dev.yml` | Remove bind mount (line 55) | Task 2 |
| `docker-compose.ollama-none.dev.yml` | Remove bind mount (line 54) | Task 2 |
| `docker-compose-gpu-nvidia.prod.yml` | Remove bind mount (line 78) | Task 2 |
| `.gitmodules` | Submodule entry removed (file deleted — it's the only submodule) | Task 3 |
| `external/vmx` (gitlink + working tree) | Removed via `git submodule deinit` + `git rm` | Task 3 |
| `.git/config`, `.git/modules/external/vmx` | Local submodule state cleaned | Task 3 |
| `README.md` | §4.1 rewritten; lines 143 & 209 de-submoduled | Task 4 |
| `frontend/README.md` | §1.7 rewritten to describe the PyPI dep | Task 4 |
| `docs/README.md` | Line 45 "vendored under `external/vmx/`" → "the `vmx` PyPI release" | Task 4 |
| `docs/superpowers/notes/vmx-api-quickref.md` | §0 caveat, §1 install, §11 Docker section updated | Task 4 |
| `docs/superpowers/notes/vmx-issues-report.md` | A1/A3 marked resolved (VMx now on PyPI) | Task 4 |
| `CHANGELOG.md` | New "Changed" entry under §1.1 Unreleased | Task 4 |

---

### Task 1: Swap the dependency and regenerate the lock

This is the core change and must stand on its own: after it, `poetry install` pulls `vmx==2.6.0` from PyPI and the full frontend quality gate (tests + import-linter + mypy) passes — with the submodule directory still physically present but no longer referenced.

**Files:**
- Modify: `frontend/pyproject.toml:11`
- Modify (regenerate): `frontend/poetry.lock`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: a `frontend` project whose only VMx reference is `vmx = "^2.6.0"` resolved from PyPI. Tasks 2–4 assume `external/vmx` is no longer needed by the Python build.

- [ ] **Step 1: Edit the dependency line**

In `frontend/pyproject.toml`, replace line 11:

```toml
vmx = {path = "../external/vmx/langs/python", develop = true}
```

with:

```toml
vmx = "^2.6.0"
```

- [ ] **Step 2: Regenerate the lock file**

Run (from `frontend/`):

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry lock
```

Expected: succeeds, writes `poetry.lock`. The `vmx` stanza changes from `files = []` (a path dep) to a real PyPI entry with `version = "2.6.0"` and populated wheel/sdist `files` hashes.

- [ ] **Step 3: Verify the lock points at PyPI 2.6.0, not the path**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && grep -A6 'name = "vmx"' poetry.lock
```

Expected: shows `version = "2.6.0"` and a non-empty `files = [...]` list (wheel + tar.gz hashes). If `files = []` or any `[tool.poetry.dependencies]`-relative path is mentioned, STOP — the path dep was not replaced.

- [ ] **Step 4: Install into a clean environment**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry install --sync
```

Expected: succeeds and reports `Installing vmx (2.6.0)` (downloaded from PyPI, *not* "from ../external/..."). No reference to `external/vmx` in the output.

- [ ] **Step 5: Verify the import surface resolves from the installed wheel**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry run python -c "import vmx; from vmx import CompositeVM, ComponentVM, ComponentVMOf, MessageHub, RxDispatcher, RelayCommand, GroupVM; print(vmx.__version__); print(vmx.__file__)"
```

Expected: prints `2.6.0` and a `__file__` path inside the virtualenv's `site-packages/vmx/` (NOT under `external/vmx/`). No `ImportError` for any of the seven names.

- [ ] **Step 6: Run the frontend test suite**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry run pytest tests/
```

Expected: all tests pass (this includes `tests/integration/test_vm_tree.py`, which builds the real DI graph against VMx). If any test fails with an `AttributeError`/`ImportError`/`TypeError` originating in `vmx`, that is a genuine 2.1.0→2.6.0 API divergence — STOP and report it with the failing test name and traceback; do not edit consumer code under this migration.

- [ ] **Step 7: Run the import-linter contracts**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry run lint-imports
```

Expected: `Contracts: 4 kept, 0 broken.` (MVVM layering + the three forbidden-import contracts).

- [ ] **Step 8: Run mypy**

Run:

```bash
cd /Users/kaveh/repos/LinguAI/frontend && poetry run mypy .
```

Expected: `Success: no issues found` (the `type-arg` code is already disabled in `[tool.mypy]`). A new VMx-typing error here also indicates a 2.6.0 divergence — report it.

- [ ] **Step 9: Commit**

```bash
cd /Users/kaveh/repos/LinguAI
git add frontend/pyproject.toml frontend/poetry.lock
git commit -m "build(frontend): consume vmx 2.6.0 from PyPI instead of the submodule path dep"
```

---

### Task 2: Strip VMx out of the Docker build

The build context was widened to the repo root *only* so the Dockerfile could `COPY external/vmx`. We keep the repo-root context (narrowing it is an optional follow-up, see end of task) and simply remove the VMx copy step and the four bind mounts. After this task, `docker compose build frontend` succeeds with no `external/vmx` present in the image.

**Files:**
- Modify: `frontend/Dockerfile` (comment block lines 2-6; delete line 15)
- Modify: `docker-compose.yml:69`
- Modify: `docker-compose.ollama-localhost.dev.yml:55`
- Modify: `docker-compose.ollama-none.dev.yml:54`
- Modify: `docker-compose-gpu-nvidia.prod.yml:78`

**Interfaces:**
- Consumes: Task 1's `frontend/pyproject.toml` (no longer a path dep) and regenerated `frontend/poetry.lock`.
- Produces: a frontend image build that depends on nothing under `external/`.

- [ ] **Step 1: Rewrite the Dockerfile comment + remove the VMx copy**

In `frontend/Dockerfile`, replace lines 2-6 (the comment block):

```dockerfile
# Mirror the repo layout inside the image so the pyproject's relative
# path-dep `vmx = {path = "../external/vmx/langs/python"}` resolves correctly:
# /app/frontend/pyproject.toml + /app/external/vmx/ → `../external/...` works.
WORKDIR /app/frontend
```

with:

```dockerfile
# Build context is the repo root (see docker-compose.yml). VMx is a published
# PyPI dependency (vmx>=2.6.0) resolved by Poetry at install time — no source
# copy needed. Context stays at the repo root for parity with the compose files.
WORKDIR /app/frontend
```

Then delete line 15 entirely:

```dockerfile
COPY external/vmx /app/external/vmx
```

The result: the `COPY frontend/pyproject.toml frontend/poetry.lock* /app/frontend/` line is immediately followed by the `RUN pip install … poetry install` line — no VMx copy between them.

- [ ] **Step 2: Remove the bind mount from all four compose files**

In each of the four files, delete the line that mounts the submodule into the frontend service:

```yaml
      - ./external/vmx:/app/external/vmx
```

Run this to confirm the exact lines first, then remove each:

```bash
cd /Users/kaveh/repos/LinguAI && grep -n './external/vmx:/app/external/vmx' docker-compose.yml docker-compose.ollama-localhost.dev.yml docker-compose.ollama-none.dev.yml docker-compose-gpu-nvidia.prod.yml
```

Expected before edit: one match per file (4 total). Remove each matched line. Leave the sibling `- ./frontend:/app/frontend` and `- ./logs/frontend:/app/logs` mounts intact.

- [ ] **Step 3: Verify no compose/Dockerfile reference to the submodule remains**

Run:

```bash
cd /Users/kaveh/repos/LinguAI && grep -rn 'external/vmx' docker-compose*.yml frontend/Dockerfile
```

Expected: **no output** (exit 1). Any match means a reference was missed.

- [ ] **Step 4: Build the frontend image cleanly**

Run (default dev compose):

```bash
cd /Users/kaveh/repos/LinguAI && docker compose -f docker-compose.yml build frontend
```

Expected: build succeeds. The `poetry install` layer downloads `vmx (2.6.0)` from PyPI. No "external/vmx not found" / "path does not exist" error.

- [ ] **Step 5: Smoke-test that VMx imports inside the built image**

Run:

```bash
cd /Users/kaveh/repos/LinguAI && docker compose -f docker-compose.yml run --rm --no-deps frontend python -c "import vmx; print(vmx.__version__)"
```

Expected: prints `2.6.0`. (`--no-deps` avoids spinning up db/backend just for the import check.)

- [ ] **Step 6: Commit**

```bash
cd /Users/kaveh/repos/LinguAI
git add frontend/Dockerfile docker-compose.yml docker-compose.ollama-localhost.dev.yml docker-compose.ollama-none.dev.yml docker-compose-gpu-nvidia.prod.yml
git commit -m "build: drop external/vmx copy and bind mounts now that vmx ships from PyPI"
```

> **Optional follow-up (not in scope, note for the user):** With VMx gone, the frontend build no longer needs the repo-root context — it could be narrowed back to `context: ./frontend` with `WORKDIR /app` and `./frontend:/app` mounts. That touches `WORKDIR`, the `COPY frontend /app/frontend` line, and all four compose `context`/`dockerfile`/volume entries, so it's a separate, larger cleanup. Left as-is here to keep this migration low-risk.

---

### Task 3: Remove the git submodule

With the Python build and Docker build no longer referencing `external/vmx`, remove the submodule from git entirely. This is the only submodule in the repo, so `.gitmodules` is deleted too. (Removing the submodule also eliminates the worktree friction noted in the dev runbook — submodule worktrees previously required `deinit --force`.)

**Files:**
- Modify/Delete: `.gitmodules`
- Delete: `external/vmx` (gitlink + working tree)
- Clean: `.git/config` submodule section, `.git/modules/external/vmx`

**Interfaces:**
- Consumes: Tasks 1 & 2 (nothing in the build references the submodule anymore).
- Produces: a repo with zero submodules. `git submodule status` prints nothing.

- [ ] **Step 1: Deinit and remove the submodule**

Run:

```bash
cd /Users/kaveh/repos/LinguAI
git submodule deinit -f external/vmx
git rm -f external/vmx
rm -rf .git/modules/external/vmx
```

Expected: `git rm -f external/vmx` stages the removal of the `external/vmx` gitlink **and** strips the `[submodule "external/vmx"]` stanza from `.gitmodules` (staging that change too).

- [ ] **Step 2: Remove `.gitmodules` if it is now empty**

`external/vmx` was the only submodule, so `.gitmodules` is now empty. Run:

```bash
cd /Users/kaveh/repos/LinguAI
[ -f .gitmodules ] && [ ! -s .gitmodules ] && git rm -f .gitmodules || echo ".gitmodules already gone or non-empty"
```

Expected: `.gitmodules` is removed and staged (it was empty). If it prints "non-empty", inspect it — another submodule exists and must NOT be removed.

- [ ] **Step 3: Verify no submodule state remains**

Run:

```bash
cd /Users/kaveh/repos/LinguAI
echo "--- submodule status ---"; git submodule status
echo "--- .gitmodules ---"; ls .gitmodules 2>/dev/null || echo "(deleted)"
echo "--- .git/config sections ---"; git config --get-regexp '^submodule\.' || echo "(none)"
echo "--- external dir ---"; ls external 2>/dev/null || echo "(deleted)"
```

Expected: `git submodule status` is empty; `.gitmodules` is `(deleted)`; `.git/config` submodule sections are `(none)`; `external/` is `(deleted)` (or empty — if an empty `external/` dir lingers, it is untracked and harmless, but remove it: `rmdir external 2>/dev/null || true`).

- [ ] **Step 4: Confirm the working tree is staged correctly**

Run:

```bash
cd /Users/kaveh/repos/LinguAI && git status
```

Expected: staged changes show `deleted: .gitmodules` and `deleted: external/vmx`. No unexpected modifications.

- [ ] **Step 5: Commit**

```bash
cd /Users/kaveh/repos/LinguAI
git commit -m "build: remove the external/vmx git submodule (VMx is now a PyPI dependency)"
```

---

### Task 4: Update the documentation

Rewrite every doc that describes VMx as a submodule. These are the six files surfaced by the repo-wide grep. Internal notes (`vmx-api-quickref.md`, `vmx-issues-report.md`) are historical reconnaissance — update the *install/Docker mechanics* and mark the pre-PyPI items resolved, but leave the API-behavior content (verified against 2.1.0) intact, since the import surface is unchanged.

**Files:**
- Modify: `README.md` (§4.1 lines 43-53; line 143; line 209)
- Modify: `frontend/README.md` (§1.7 lines 108-119)
- Modify: `docs/README.md` (line 45)
- Modify: `docs/superpowers/notes/vmx-api-quickref.md` (§0, §1, §11)
- Modify: `docs/superpowers/notes/vmx-issues-report.md` (A1/A3)
- Modify: `CHANGELOG.md` (§1.1 Unreleased)

**Interfaces:**
- Consumes: the end state from Tasks 1–3 (PyPI dep, no submodule).
- Produces: docs with no instruction to clone/init a submodule for VMx.

- [ ] **Step 1: Rewrite `README.md` §4.1**

Replace lines 43-55 (the `### 4.1. Clone with submodules` heading through the closing code fence, up to but not including `### 4.2.`):

```markdown
### 4.1. Clone with submodules

VMx is consumed as a git submodule under `external/vmx/`. Either clone
recursively or initialise the submodule afterwards:

```bash
git clone --recurse-submodules https://github.com/thekaveh/LinguAI.git
cd LinguAI

# or, if you cloned without --recurse-submodules:
git submodule update --init --recursive
```
```

with:

```markdown
### 4.1. Clone

```bash
git clone https://github.com/thekaveh/LinguAI.git
cd LinguAI
```

VMx is a published PyPI dependency (`vmx`, pinned in
`frontend/pyproject.toml`); Poetry resolves it during the frontend build, so
there is no submodule to initialise.
```

- [ ] **Step 2: Fix `README.md` line ~143 (bind-mount description)**

Replace:

```markdown
Source trees are bind-mounted into the containers (`./backend` → `/app`,
`./frontend` → `/app/frontend`, plus `./external/vmx` for the submodule).
```

with:

```markdown
Source trees are bind-mounted into the containers (`./backend` → `/app`,
`./frontend` → `/app/frontend`).
```

- [ ] **Step 3: Fix `README.md` line ~209 (docs index blurb)**

Replace:

```markdown
- [`frontend/README.md`](frontend/README.md) — MVVM rules, import-linter
  contracts, page-VM lifecycle, VMx submodule handling.
```

with:

```markdown
- [`frontend/README.md`](frontend/README.md) — MVVM rules, import-linter
  contracts, page-VM lifecycle, the VMx dependency.
```

- [ ] **Step 4: Rewrite `frontend/README.md` §1.7**

Replace lines 108-119 (the `## 1.7. VMx submodule` section body):

```markdown
## 1.7. VMx submodule

VMx is consumed as a git submodule under `external/vmx/`. After cloning,
initialise it:

```bash
git submodule update --init --recursive
```

`frontend/pyproject.toml` references it as a path dependency
(`vmx = {path = "../external/vmx/langs/python", develop = true}`); the
frontend Docker image bind-mounts both `./frontend` and `./external/vmx`
so iterating on VMx does not require a container rebuild.
```

with:

```markdown
## 1.7. VMx dependency

VMx is a published PyPI package. `frontend/pyproject.toml` pins it as a normal
dependency:

```toml
vmx = "^2.6.0"
```

Poetry resolves and installs it from PyPI during `poetry install` (and during
the Docker build), so there is no submodule to initialise and nothing extra to
mount into the container. To move to a newer VMx, bump the constraint and run
`poetry lock` in `frontend/`.
```

- [ ] **Step 5: Fix `docs/README.md` line ~45**

Replace:

```markdown
  cheat sheet for the consumer-facing VMx API as it actually behaves in
  the version vendored under `external/vmx/`. **This is the authoritative
```

with:

```markdown
  cheat sheet for the consumer-facing VMx API as it actually behaves in
  the `vmx` PyPI release pinned by `frontend/pyproject.toml`. **This is the authoritative
```

- [ ] **Step 6: Update `vmx-api-quickref.md` §0 caveat row**

In `docs/superpowers/notes/vmx-api-quickref.md`, the §0 table's first row currently says VMx is not on PyPI. Replace that row:

```markdown
| `vmx = "^2.1.0"` on PyPI | **VMx is NOT on PyPI yet.** Use Poetry path dep against the **git submodule** at `external/vmx/`: `vmx = {path = "../external/vmx/langs/python", develop = true}` (from `frontend/pyproject.toml`'s perspective — `frontend/` and `external/` are siblings under the repo root). |
```

with:

```markdown
| `vmx = "^2.1.0"` on PyPI | VMx now ships on PyPI. `frontend/pyproject.toml` pins `vmx = "^2.6.0"`; Poetry resolves it normally — no submodule, no path dep. (This quickref's API notes were verified against 2.1.0; the import surface is unchanged through 2.6.0.) |
```

- [ ] **Step 7: Update `vmx-api-quickref.md` §1 (install section)**

Replace the §1 body (from the `## 1. Installing VMx (git submodule + Poetry path dep)` heading through the `(`frontend/` and `external/` are siblings …)` parenthetical):

```markdown
## 1. Installing VMx (git submodule + Poetry path dep)

VMx lives in this repo as a git submodule at `external/vmx`, pinned to a specific commit. To pull it after a fresh `git clone`:

```bash
git submodule update --init external/vmx
```

In `frontend/pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.10"
vmx = {path = "../external/vmx/langs/python", develop = true}
```

(`frontend/` and `external/` are siblings under the repo root; relative path traverses one level up then into the submodule.)
```

with:

```markdown
## 1. Installing VMx (PyPI + Poetry)

VMx is a published PyPI package — there is no submodule. In `frontend/pyproject.toml`:

```toml
[tool.poetry.dependencies]
python = "^3.10"
vmx = "^2.6.0"
```

Poetry resolves it from PyPI on `poetry install`; the lock file (`frontend/poetry.lock`) pins the exact resolved version and hashes.
```

- [ ] **Step 8: Update `vmx-api-quickref.md` §11 (Docker section)**

§11 documents the now-obsolete "widen the build context for the submodule" change. Replace the entire §11 (from the `## 11. Dockerfile + docker-compose change for the VMx submodule` heading through the end of the "Fresh-clone setup checklist" subsection — i.e. up to but not including the next `##` heading or EOF) with:

```markdown
## 11. Dockerfile + docker-compose (historical)

> **Superseded.** VMx is now a PyPI dependency, so none of the submodule
> plumbing below is needed. The frontend image installs `vmx` from PyPI via
> `poetry install`; no source copy or bind mount is required, and a fresh
> clone needs no `git submodule` step. This section is retained only as a
> record of the pre-2.6.0 setup.
```

(Delete the original `### docker-compose.yml`, `### frontend/Dockerfile`, and `### Fresh-clone setup checklist` subsections that followed the old heading.)

- [ ] **Step 9: Mark `vmx-issues-report.md` A1/A3 resolved**

In `docs/superpowers/notes/vmx-issues-report.md`, the A3 "Suggested action" line (around line 30) references the pre-PyPI submodule workaround. Replace:

```markdown
- **Suggested action:** None on the VMx side beyond fixing A1. Document the "while we're pre-PyPI, use a submodule / `pip install git+https://github.com/thekaveh/VMx.git#subdirectory=langs/python`" path in README §4.1.
```

with:

```markdown
- **Suggested action:** Resolved — VMx now publishes to PyPI, and LinguAI consumes `vmx` as a normal Poetry dependency (`frontend/pyproject.toml`). The submodule/path-dep workaround has been removed.
```

If A1 (the "publish to PyPI" item) carries an open/unresolved status marker, prepend `**Resolved (VMx is on PyPI as of 2.6.0).**` to its description line as well — VMx is now published, so A1's premise is satisfied.

- [ ] **Step 10: Add a CHANGELOG entry**

In `CHANGELOG.md`, under `## 1.1. Unreleased`, add a `### 1.1.N. Changed` subsection (numbered after the existing `### 1.1.1. Added`; if a "Changed" subsection already exists under Unreleased, append the bullet to it instead):

```markdown
### 1.1.2. Changed
- Frontend now consumes VMx as a published PyPI dependency (`vmx = "^2.6.0"`,
  upgraded from the vendored `2.1.0`) instead of a git submodule path dep. The
  `external/vmx` submodule, its Docker `COPY`/bind mounts, and the
  `git submodule` clone steps in the docs have been removed.
```

- [ ] **Step 11: Verify no stale submodule references survive in docs**

Run:

```bash
cd /Users/kaveh/repos/LinguAI && grep -rniE 'git submodule|recurse-submodules|external/vmx|path *= *"\.\./external' --include='*.md' . | grep -vE 'historical|Superseded|Resolved|removed|instead of a git submodule'
```

Expected: **no output** (exit 1). The `grep -v` filter allows the deliberate historical/resolved mentions; any other hit is a doc that still tells the reader to use a submodule and must be fixed.

- [ ] **Step 12: Commit**

```bash
cd /Users/kaveh/repos/LinguAI
git add README.md frontend/README.md docs/README.md docs/superpowers/notes/vmx-api-quickref.md docs/superpowers/notes/vmx-issues-report.md CHANGELOG.md
git commit -m "docs: describe VMx as a PyPI dependency; drop submodule instructions"
```

---

## Self-Review

**Spec coverage** (every submodule touchpoint found in research → a task):
- `frontend/pyproject.toml` path dep → Task 1 ✓
- `frontend/poetry.lock` → Task 1 ✓
- `frontend/Dockerfile` COPY + comment → Task 2 ✓
- 4× compose bind mounts → Task 2 ✓
- `.gitmodules` / `external/vmx` / `.git` state → Task 3 ✓
- `README.md` (3 spots), `frontend/README.md`, `docs/README.md`, `vmx-api-quickref.md` (3 spots), `vmx-issues-report.md`, `CHANGELOG.md` → Task 4 ✓
- No CI workflows reference the submodule (confirmed: `.github/workflows` absent) — nothing to change there.

**Placeholder scan:** No TBD/TODO/"handle edge cases" steps; every edit shows exact before/after text and every verification shows the command + expected output.

**Consistency:** Version string `vmx = "^2.6.0"` is identical across Task 1, Task 4 (frontend/README, quickref §1), and the CHANGELOG. The "verify no reference remains" greps in Tasks 2, 3, and 4 are scoped to the file types each task owns. The upgrade framing (2.1.0 → 2.6.0, additive-only, seven primitives stable) is stated once in the header and relied on by Task 1's verification gate.

**Known risk, explicitly gated:** Because PyPI has only 2.6.0 (no 2.1.0), Task 1 is also a version upgrade. Steps 5–8 (import check, pytest, import-linter, mypy) are the gate; any VMx-originated failure stops the migration for a report rather than being silently patched.

---

## Execution Handoff

**Plan complete and saved to `docs/superpowers/plans/2026-06-16-vmx-submodule-to-pypi.md`. Two execution options:**

**1. Subagent-Driven (recommended)** — I dispatch a fresh subagent per task, review between tasks, fast iteration.

**2. Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints.

**Which approach?**
