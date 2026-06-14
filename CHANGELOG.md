# 1. Changelog

All notable user-visible changes to LinguAI are recorded here. The format is
based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); the project
does not currently tag releases, so dated entries below correspond to merges
into `develop`.

## 1.1. Unreleased

### 1.1.1. Added
- `LICENSE` (MIT) at the repository root.
- `CHANGELOG.md` (this file).
- `docs/README.md` — top-level documentation index linking the specs, plans,
  and notes that live under `docs/superpowers/`.
- Service-level `README.md` files for `backend/` and `frontend/`.
- `.dockerignore` at the repository root so the frontend build context stops
  shipping `.env`, `.git/`, caches, and docs into the image.
- Backend `DB_ECHO` environment variable that gates SQLAlchemy statement
  logging (default `false`; previously hardcoded `True` in
  `services/dependency/db_service.py`).
- Backend `pytest` configuration: `asyncio_mode = "auto"` in
  `backend/pyproject.toml`.

### 1.1.2. Changed
- Rewrote `README.md` to reflect the post-Streamlit architecture: NiceGUI +
  VMx frontend, SQLModel backend, Groq provider, submodule-init step,
  pgAdmin dashboard, and hierarchical section numbering.
- Regenerated `architecture.py` to drop the never-implemented AWS Cognito
  edge, label the backend as `FastAPI + LangChain + SQLModel`, and the
  frontend as `NiceGUI + VMx`. Added explicit edges to the optional Ollama,
  OpenAI, and Groq providers, plus a `depends_on` edge from frontend to
  db-dashboard.
- All four docker-compose files: dropped the obsolete `version: "3.8"` key.
- The two `*.ollama-*.dev.yml` variants and `docker-compose-gpu-nvidia.prod.yml`
  now match the NiceGUI build (port 8080, repo-root build context, vmx
  submodule mount, `FRONTEND_PORT=8080` override).
- `db/scripts/db-snapshot.sh` and `db/db-snapshot-win.ps1` both fail fast on
  missing required env vars and read role/password from the environment
  rather than hardcoding them.
- Backend Dockerfile: prefixed `apt-get install` with `apt-get update`,
  added `--no-install-recommends`, replaced the deprecated `--no-dev` flag
  with `--without dev`. Backend `pytest*` deps moved to the dev group so
  they no longer ship to production.
- Backend `@log_decorator` now redacts password/secret/token/api_key fields
  before writing args/kwargs to the debug log.

### 1.1.3. Fixed
- Backend `UserService.get_user_topics` returned `db_user.topics` (no such
  attribute) — corrected to `db_user.user_topics`.
- Backend `update_user_languages`, `update_user_profile`, and
  `change_password` now lowercase the username on lookup, matching
  `create_user`/`authenticate`. Previously, mixed-case usernames silently
  failed those updates.
- Backend `PolyglotPuzzleService.agenerate` validated requests via bare
  `assert`s, which are stripped under `python -O`. Replaced with explicit
  `HTTPException(422)` checks.
- Backend `UserService.update_user_topics` stray `print(...)` calls replaced
  with proper logger calls.
- Frontend `UserBase` schema declared `user_assessments` twice; the duplicate
  is removed.
- `docker-compose.ollama-none.dev.yml`: fixed the `/app.` volume-mount typo
  that broke frontend hot-reload, and added the missing `env_file: .env` on
  the frontend service.
- `docker-compose-gpu-nvidia.prod.yml`: the frontend service was mounting
  `./logs/backend` as its log directory; corrected to `./logs/frontend`.

### 1.1.4. Removed
- Streamlit-era empty placeholder directories that survived the NiceGUI
  cutover: `frontend/components/`, `frontend/pages/`, `frontend/schema/`,
  `frontend/utils/`, `frontend/services/`, `frontend/logs/`.
- Two unused frontend service modules:
  `frontend/models/services/content_service.py` and `skill_level_service.py`.
- Three Streamlit-era environment variables from `.env.example`:
  `DEFAULT_LANGUAGE`, `DEFAULT_SKILL_LEVEL`, `DEFAULT_USER_NAME` (no
  remaining references in code).

## 1.2. Prior history

Earlier user-visible changes are not yet captured in this file. Notable
recent commits on the `develop` branch:

- `67fa99c` — `feat(frontend): replace Streamlit with NiceGUI + VMx`
  (strict MVVM frontend overhaul).
- `661b7ca` — Renamed "embeddings quiz" → "polyglot puzzle" across the
  product.
- `c5c296d` — Removed the log-rotation handler that crashed under Streamlit's
  reload behaviour.
- `8e87192` — Repaired the backend pytest suite.
