# 1. Backend (`backend/`)

The LinguAI backend is a FastAPI application that exposes versioned REST
endpoints, dispatches LLM calls through LangChain, and persists state in
PostgreSQL via SQLModel (with a small amount of legacy SQLAlchemy).

This README focuses on the **internal layout and conventions** of the
backend. For overall project setup, compose variants, and end-to-end
workflow, see the top-level [`README.md`](../README.md).

## 1.1. Entry point

`app/main.py` constructs the FastAPI app and mounts every v1 route via
`app/api/v1/router.py`. Database init runs once at startup via a lifespan
context manager that calls `SQLModel.metadata.create_all(...)`.

## 1.2. Directory layout

```
backend/app/
├── main.py                       # FastAPI app + lifespan
├── api/v1/
│   ├── router.py                 # mounts all endpoints under /v1
│   └── endpoints/                # thin route handlers
├── services/                     # business logic (most extend CRUDService)
│   ├── crud_service.py           # generic CRUD Protocol/base
│   ├── llm_service.py            # provider-conditional LLM listing/dispatch
│   ├── dependency/db_service.py  # SQLModel engine + get_db_session
│   └── …
├── data_access/
│   ├── repositories/             # SQLModel/SQLAlchemy queries
│   ├── models/                   # persistence models (DB-mapped)
│   └── session.py                # legacy SQLAlchemy session (deprecated)
├── models/                       # Pydantic/SQLModel domain DTOs
├── schema/                       # Pydantic request/response schemas
├── core/config.py                # env-backed Config constants
├── utils/                        # logger + helpers
└── tests/                        # pytest suites
```

## 1.3. Layering

Imports flow only downward:

```
api/v1/endpoints → services → data_access/repositories → data_access/models
```

Domain DTOs in `app/models/` may be returned by services or accepted as
request bodies; persistence models (`app/data_access/models/`) stay below
the service layer.

## 1.4. Database session caveat

The project migrated mid-flight from SQLAlchemy to SQLModel. Two engine
constructions exist:

- `services/dependency/db_service.py` — SQLModel engine (current).
- `data_access/session.py` — legacy SQLAlchemy engine.

Some older code paths still inject the legacy SQLAlchemy session
(`Depends(get_db)`). Avoid mixing both sessions inside a single request
— each holds its own connection and transaction, and changes made through
one are not visible to the other. New code should use the SQLModel
`get_db_session` dependency exclusively.

`Config.DB_ECHO` (env var `DB_ECHO`, default `false`) gates SQL statement
logging on both engines.

## 1.5. LLM provider filtering

`services/llm_service.py` returns only those `LLM` rows whose provider
credentials are present (`OPENAI_API_KEY`, `GROQ_API_KEY`,
`OLLAMA_API_ENDPOINT`). For Ollama specifically, the model must additionally
have been pulled into the running Ollama container. Missing creds → the
model is silently hidden from listings.

## 1.6. Schema management

There is **no migration framework** (no Alembic). The source of truth for
schema is `db/snapshot/linguai_db_ss.sql`. To change schema:

1. Edit the snapshot SQL, or let `SQLModel.metadata.create_all` add new
   SQLModel-defined tables on backend startup.
2. Re-snapshot the running DB:
   `docker exec db sh ./scripts/db-snapshot.sh`
3. For others to pick up the new schema, they must drop the data volume:
   `docker-compose down -v --remove-orphans`

The snapshot is loaded by Postgres' `docker-entrypoint-initdb.d` only when
the data volume is empty.

## 1.7. Running the tests

From the host with the stack running:

```bash
# All backend tests
docker exec -it backend python -m pytest app/tests/

# With coverage on the services layer
docker exec -it backend python -m pytest --cov=app/services app/tests/

# A single file or single test
docker exec -it backend python -m pytest app/tests/user_service_test.py
docker exec -it backend python -m pytest app/tests/user_service_test.py::test_create_user
```

`pytest-asyncio` is configured in `pyproject.toml` with `asyncio_mode = "auto"`,
so `async def test_*` functions do not need the `@pytest.mark.asyncio`
decorator.

## 1.8. Logging

The backend's structured-text logger is configured by `app/utils/logger_config.py`
from `BACKEND_LOGGER_NAME`, `BACKEND_LOG_LEVEL`, and `BACKEND_LOG_FILE`.
The `@log_decorator` wrapper used across services redacts password / secret
/ token / API-key fields before writing args/kwargs to debug log lines.
