# LinguAI

LinguAI is a language-learning assistant. Practise conversations with an
AI persona, generate or rewrite learning content, review writing and
assess language skills through a browser interface.

## 1. Capabilities

- Chat with a selected persona and model; optionally attach images to a vision model.
- Generate learning content, rewrite text and review writing.
- Explore translation exercises with Polyglot and track assessments in your profile.
- Use available OpenAI, Groq or Ollama models. Provider credentials and pulled models determine what appears in the interface.

The stack uses a NiceGUI + VMx frontend, FastAPI + LangChain + SQLModel
backend and PostgreSQL. Start with the local learning task below. The
[documentation index](docs/README.md) routes to operations and internal references.

## 2. Requirements

Required:

- Git
- Docker (Engine 24+) with Docker Compose v2

Optional, for working outside the containers:

- Python 3.10
- Poetry (used by both services for dependency management)

## 3. Run locally

### 3.1. Clone

```bash
git clone https://github.com/thekaveh/LinguAI.git
cd LinguAI
```

VMx is a published PyPI dependency (`vmx`, pinned in
`frontend/pyproject.toml`); Poetry resolves it during the frontend build, so
there is no submodule to initialise.

### 3.2. Configure environment

Copy the example and fill in any provider keys you intend to use. `.env`
is gitignored.

```bash
cp .env.example .env
```

- `OPENAI_API_KEY` — leave blank to disable OpenAI-backed LLMs.
- `GROQ_API_KEY` — leave blank to disable Groq-backed LLMs.
Container Ollama startup queries active Ollama rows in the seeded `llm`
table and pulls those models. It does not use an `OLLAMA_MODELS` value from
`.env`. Model downloads can require substantial time, disk space and RAM.
For host Ollama, pull a model whose name matches an active database row.
Choose the no-Ollama variant and a provider key if you want to avoid local
model downloads.

The backend's LLM service hides any LLM row whose provider credentials
are absent, so a missing key simply removes that provider's models from
the UI listing.

### 3.3. Pick a compose variant

| Compose file                                  | Environment | Ollama source                | Notes                                  |
| --------------------------------------------- | ----------- | ---------------------------- | -------------------------------------- |
| `docker-compose.yml`                          | dev         | containerised (CPU)          | Downloads seeded active models          |
| `docker-compose.ollama-localhost.dev.yml`     | dev         | host (`host.docker.internal`)| Faster on Apple Silicon                |
| `docker-compose.ollama-none.dev.yml`          | dev         | none                         | OpenAI / Groq only                     |
| `docker-compose-gpu-nvidia.prod.yml`          | prod        | containerised (NVIDIA GPU)   | EC2 + NVIDIA target                    |

The bare `docker-compose` / `docker compose` command will not find these
non-default files automatically — pass `-f` explicitly.

### 3.4. Bring the stack up

```bash
# Default dev stack
docker compose up --build

# Or pick a variant
docker compose -f docker-compose.ollama-localhost.dev.yml up --build
```

The default ports from `.env.example` are:

- Frontend: `http://localhost:50004`
- Backend Swagger UI: `http://localhost:50003/docs`
- pgAdmin (db-dashboard): `http://localhost:50001`

Use `-d` to run detached (logs not streamed); `docker compose logs -f
<service>` to follow logs after the fact.

To tear down the stack while preserving the data volume:

```bash
docker compose down --remove-orphans
```

Use the same `-f` selection for logs and shutdown when running a variant.
Do not add `-v` unless you intend to erase the database. Snapshot reload and
backup instructions are in the [operations guide](docs/operations.md).

## 4. Try your first conversation

Use this task only on your private local development stack. The snapshot
contains demonstration accounts with known passwords. Sign in as
`kumar` with password `linguai`; do not expose these accounts publicly.
Other seeded accounts can have different passwords.

1. Open `http://localhost:50004` and select **Sign in** after entering the credentials.
2. Open **Chat** in the left drawer. Under **Session**, choose a **Persona** and an available **Model**. Leave **TTS** off for this first task.
3. In **Type your message…**, enter: `Help me practise ordering tea in Spanish. Ask me one short question.` Select the send icon.
4. Expect your message and an assistant reply to appear in the conversation pane. Reply to continue practising. The exact response depends on the model.
5. Select **Clear** to reset the conversation, or visit **Profile** to inspect your learning languages.

If the model list is empty or **Could not load personas or LLMs** appears,
check the backend logs and provider configuration. OpenAI/Groq need valid
keys and accessible models; Ollama needs a running endpoint and a pulled
model matching an active database row. A visible model can still fail when
provider access, quota or connectivity changes. Provider calls may incur
charges. See [operations and troubleshooting](docs/operations.md).

## 5. Development and operations

- [Operations](docs/operations.md): database snapshots, backups, provider troubleshooting and EC2 deployment requirements.
- [Backend](backend/README.md): service layout, database sessions and provider filtering.
- [Frontend](frontend/README.md): MVVM layers, page lifecycle and local test commands.
- [Documentation index](docs/README.md): architecture, specifications and historical implementation records.
- [Changelog](CHANGELOG.md): recorded changes.

The development source directories are bind-mounted into containers.
The backend runs with uvicorn reload; restart the frontend after code
changes. Both services use Poetry. Commit changes to `pyproject.toml`
and `poetry.lock` together, then rebuild the relevant image.

The images install runtime dependencies only. In your disposable development
containers, install the locked development dependencies before running tests
from the host:

```bash
docker exec -it backend poetry install --no-root --with dev
docker exec -it frontend poetry install --no-root --with dev
docker exec -it backend python -m pytest app/tests/
docker exec -it frontend python -m pytest tests/
```

## 6. License

[MIT](LICENSE).
