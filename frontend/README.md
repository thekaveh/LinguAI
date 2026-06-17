# 1. Frontend (`frontend/`)

The LinguAI frontend is a NiceGUI single-page app built on top of
[VMx](https://pypi.org/project/vmx/) for the ViewModel layer. The architecture is
strict MVVM with import-linter contracts enforcing the layering.

For project setup, compose variants, and the end-to-end workflow, see the
top-level [`README.md`](../README.md). For deeper design context, see the
[frontend MVVM overhaul spec](../docs/superpowers/specs/2026-05-30-frontend-mvvm-overhaul-design.md)
and the [VMx API quickref](../docs/superpowers/notes/vmx-api-quickref.md).

## 1.1. Entry point

`frontend/main.py` registers two NiceGUI pages:

- `/` — the authenticated/loggedin shell, served by `views.app_shell.mount`.
  Per-client `AppShellVM` is constructed by `core/di.build_shell`.
- `/register` — the registration wizard, served via dedicated VMs/views.

Process-scoped VMx infrastructure (the hub, dispatcher, HTTP client, and
auth service) is created once via `core/di.build_process_scoped` and
shared across all NiceGUI clients.

## 1.2. Directory layout

```
frontend/
├── main.py                       # NiceGUI page registration + ui.run()
├── core/
│   ├── config.py                 # AppConfig (pydantic-settings)
│   ├── di.py                     # composition root for the shell
│   ├── http.py                   # shared httpx.AsyncClient + URL assembly
│   └── logger.py                 # logging setup
├── models/
│   ├── domain/                   # frozen dataclasses (immutable domain types)
│   ├── schemas/                  # Pydantic backend payload shapes
│   └── services/                 # thin HTTP clients (one per backend service)
├── viewmodels/                   # VMx ViewModels
│   ├── app_shell_vm.py           # root shell VM
│   ├── shell/                    # nav, session, settings, notifications
│   ├── auth/                     # login + registration wizard
│   ├── home/, profile/, chat/, …
│   └── polyglot_puzzle/, content_gen/, rewrite_content/, review_writing/
├── views/                        # NiceGUI render functions; read VM state
│   ├── app_shell.py              # PAGE_RENDERERS dispatch
│   ├── theme/                    # palette + typography
│   └── …
├── static/                       # static assets
└── tests/                        # unit + integration tests
```

## 1.3. Layering rules

The import-linter contracts in `pyproject.toml` enforce:

```
views → viewmodels → models → core
```

`core.di` is the composition root and is the only `core.*` module
permitted to import from `viewmodels` and `models.services`. The
explicit allow-list lives in `[tool.importlinter.contracts]`.

A second contract keeps `viewmodels` UI-free (no NiceGUI imports).

## 1.4. Page-VM lifecycle and the shell

Page VMs are constructed once per NiceGUI client and attached to the
shell instance as private attributes (e.g. `shell._chat_vm`). The
canonical home VM is also exposed via `shell.pages`. Views look up the
appropriate page VM by route through `views/app_shell.PAGE_RENDERERS`.

Passwords are never held on Pydantic models. Forms keep plaintext in
private `_<field>` slots and expose a boolean `has_<field>` on the
public model so views can render filled/empty state without ever
seeing the plaintext.

## 1.5. URL assembly

All backend URLs are assembled in `core/http.py`:

```python
base = cfg.backend_endpoint.rstrip("/") + "/v1"
```

Services in `models/services/` take the `httpx.AsyncClient` returned by
`core/http.build_http_client` and append endpoint-specific paths.

## 1.6. Running the tests

From the host with the stack running:

```bash
# All frontend tests (unit + integration)
docker exec -it frontend python -m pytest tests/

# With coverage on the services layer
docker exec -it frontend python -m pytest --cov=models/services tests/

# A single file or test
docker exec -it frontend python -m pytest tests/integration/test_vm_tree.py
```

The integration suite (`tests/integration/test_vm_tree.py`) builds the
real DI graph and uses `respx` to mock the backend; it catches end-to-end
wiring regressions early.

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
