# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Architecture

LinguAI is a containerized language-learning assistant with five services orchestrated by Docker Compose:

- **`db`** — PostgreSQL 16. On first boot it loads `db/snapshot/linguai_db_ss.sql` from `docker-entrypoint-initdb.d` (schema + seed data). The snapshot is the source of truth for schema; there is **no migration framework** (no Alembic). Schema changes are made by editing snapshot SQL or by letting `SQLModel.metadata.create_all` add new tables on backend startup, then re-snapshotting.
- **`backend`** — FastAPI + LangChain + SQLModel (with some legacy SQLAlchemy). Entry `backend/app/main.py`. All routes live under `app/api/v1/endpoints/*` and are aggregated in `app/api/v1/router.py` with prefix `/v1`. Talks to LLM providers via `app/services/llm_service.py`, which dynamically filters the `LLM` table by which provider creds are present (`OPENAI_API_KEY`, `GROQ_API_KEY`, `OLLAMA_API_ENDPOINT`) — an LLM row is only surfaced if its provider is configured *and*, for Ollama, the model has actually been pulled.
- **`frontend`** — NiceGUI + VMx on strict horizontal MVVM. Entry `frontend/main.py`. Top-level layers `views/ → viewmodels/ → models/ → core/` (enforced by import-linter; `core/di.py` is the composition root). HTTP clients live in `models/services/*` and share one `httpx.AsyncClient` built in `core/http.py` from `core/config.py`'s `backend_endpoint` (with `/v1` appended). VMx is a PyPI dependency (`vmx`), not a submodule.
- **`db-dashboard`** — pgAdmin web UI for the Postgres instance (the frontend's `depends_on` waits on it).
- **`ollama`** — optional local LLM runtime (custom Dockerfile under `ollama/`). The `OLLAMA_MODELS` env var controls which models are pulled at container start.

Layering inside `backend/app`:
- `api/v1/endpoints/*` → thin FastAPI handlers
- `services/*` → business logic; most extend `CRUDService` from `services/crud_service.py`
- `data_access/repositories/*` → SQLModel/SQLAlchemy queries against `data_access/models/*`
- `models/*` (top-level) → Pydantic/SQLModel domain models distinct from the persistence models in `data_access/models/*`

Frontend mirrors this in MVVM layers: `views/*` (UI) → `viewmodels/*` (presentation state) → `models/services/*` (HTTP clients) → backend.

DB session: `backend/app/services/dependency/db_service.py` exposes `get_db_session` (FastAPI dependency) and `init_db` (called from `lifespan`). Note from that file: the project mid-flight migrated from SQLAlchemy to SQLModel — some older code paths may still use raw SQLAlchemy, so be careful mixing the two in a single transaction.

`APP_CONTEXT` env var (`backend` vs `frontend`) is set in `docker-compose.yml` and is what lets shared-looking utilities know which side they're running on.

## Compose variants

Pick the right compose file for the situation (the bare `docker compose` command will not find them by default — pass `-f`):

| File | Use case |
|---|---|
| `docker-compose.yml` | Default dev; Ollama runs in a container on CPU |
| `docker-compose.ollama-localhost.dev.yml` | Dev; Ollama runs on host (faster on Apple Silicon) |
| `docker-compose.ollama-none.dev.yml` | Dev; no Ollama service at all (OpenAI/Groq only) |
| `docker-compose-gpu-nvidia.prod.yml` | Production on EC2 + NVIDIA |

`frontend` depends on `db-dashboard` (not just `backend`) to delay frontend startup until backend init has progressed — relevant if you change `depends_on`.

## Common commands

All commands assume the stack is already running via one of the compose files above.

```bash
# Bring up dev stack (CPU Ollama in a container)
docker compose up --build

# Tear down (keep volumes)
docker compose down --remove-orphans

# Tear down AND wipe DB volume — needed to re-load the snapshot after schema/data changes
docker compose down -v --remove-orphans

# Re-snapshot the running DB into db/snapshot/linguai_db_ss.sql
docker exec db sh ./scripts/db-snapshot.sh
```

Tests (run inside the containers):

```bash
# Backend
docker exec -it backend python -m pytest app/tests/
docker exec -it backend python -m pytest --cov=app/services app/tests/
docker exec -it backend python -m pytest app/tests/user_service_test.py        # single file
docker exec -it backend python -m pytest app/tests/user_service_test.py::test_x # single test

# Frontend
docker exec -it frontend python -m pytest tests/
docker exec -it frontend python -m pytest --cov=models/services tests/
```

Dependencies are managed with Poetry inside each service (`backend/pyproject.toml`, `frontend/pyproject.toml`). After `poetry add`/`poetry remove`, rebuild: `docker compose build`.

Service URLs (default ports from `.env.example`): frontend `http://localhost:50004`, backend Swagger `http://localhost:50003/docs`, pgAdmin `http://localhost:50001`.

## Things to know before editing

- **Code is bind-mounted into the dev containers** (`./backend:/app`, `./frontend:/app/frontend`), so edits hot-reload — no rebuild needed unless `pyproject.toml` changes.
- **DB schema changes require a snapshot refresh and `down -v`** for other devs to see them — the snapshot only loads when the `db-data` volume is empty.
- **Adding a new LLM** requires a row in the `LLM` table (via snapshot) *and* the right provider env var set; otherwise `LLMService.get_all` filters it out.
- **Adding a new backend endpoint**: create `app/api/v1/endpoints/foo.py` with an `APIRouter` called `router`, then register it in `app/api/v1/router.py`. The frontend side needs a new HTTP client in `frontend/models/services/` that calls the path on the shared `httpx.AsyncClient` from `core/http.build_http_client()` (the `/v1` prefix is already applied).
- `.env` is git-ignored; copy `.env.example` to `.env` and fill in provider keys before first `up`.
