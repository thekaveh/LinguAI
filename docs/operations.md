# Operations

This guide covers the current Compose configuration. It does not establish
that an EC2 deployment has been validated for public production use.
Start with the [local setup and first chat](../README.md).

## Database lifecycle

`db/snapshot/linguai_db_ss.sql` is the schema and seed-data source. There is
no migration framework. PostgreSQL loads this snapshot only into an empty
`db-data` volume; an existing volume keeps its current data and passwords.

Inspect the script and back up the existing snapshot before running it;
it overwrites the mounted snapshot file. Treat backups as private because
they contain account data and password hashes.

To take a repository-format snapshot of a running development database:

```bash
docker exec db bash ./scripts/db-snapshot.sh
```

For a disposable development database only, `docker compose down -v
--remove-orphans` deletes data volumes. The next startup reloads the snapshot.
Use your selected Compose file with `-f`. This also removes the pgAdmin
volume. Never use this command on data that must be retained.

## Provider troubleshooting

- An empty model list means no applicable active models are available. Configure OpenAI/Groq keys or make Ollama reachable with a matching pulled model.
- Container Ollama startup selects active models from `public.llm`. An `.env` `OLLAMA_MODELS` list does not override that query. Inspect startup logs for download failures.
- Model visibility is not a successful inference test. Inspect backend logs for provider authentication, quota, model availability and connectivity errors when a request fails.
- Follow logs with `docker compose logs -f backend ollama`, using your variant's `-f` option. Omit `ollama` for the no-Ollama variant. Do not share logs containing credentials or private learning content.

## EC2 deployment requirements

The provided `docker-compose-gpu-nvidia.prod.yml` targets an EC2 host with
Docker Compose, an NVIDIA GPU, working NVIDIA container support and enough
RAM/disk for the selected models. The original target was an Ubuntu-NVIDIA-
PyTorch2 AMI. Confirm those prerequisites on your actual host first.

The file builds service images **and still bind-mounts** `./backend` to
`/app` and `./frontend` to `/app/frontend`. The backend image starts uvicorn
with `--reload` and debug logging. Keep the checkout available; this is not
an immutable-image deployment. A hardened image-only deployment requires
separate Compose/runtime changes and validation.

Before starting services on any remotely reachable host:

1. Prepare a private `.env`. Replace the known PostgreSQL administrator and pgAdmin credentials, and set a random `FRONTEND_STORAGE_SECRET`. Configure only the provider credentials you need. Changing `.env` does not rotate credentials already stored in a volume.
2. Secure the PostgreSQL application role too. The snapshot explicitly creates `linguai_app` with password `linguai`; changing `POSTGRES_APP_PASSWORD` alone does not update that role. Coordinate the database role and application configuration on a protected database before allowing application access.
3. Remove or rotate demonstration accounts, including the seeded administrator, before granting remote access. Their passwords are not changed by PostgreSQL or pgAdmin environment variables. Use an isolated private initialization stage; back up existing data before changing it.
4. Review host firewall, EC2 security groups and Docker port exposure. The supplied mappings omit a host IP and publish database, pgAdmin, Ollama, backend and frontend ports on all host interfaces by default. Do not expose the database, pgAdmin or Ollama publicly. Configure explicit private/loopback bindings and restrict direct backend/frontend access before starting this Compose configuration.
5. Provide an HTTPS reverse proxy and restrict the application ports to that proxy. Review the application authentication and access-control design for your intended audience. The supplied Compose file provides neither a TLS proxy nor a public-production security baseline.
6. Set `PROD_ENV_CPUS` and `PROD_ENV_MEM_LIMIT` for the Ollama container, check provider access/model requirements and prepare database backups. These limits do not constrain every service.

After completing the above configuration on your own isolated deployment:

```bash
# Run from the configured checkout root on the EC2 host.
docker compose -f docker-compose-gpu-nvidia.prod.yml up --build
```

Verify service logs, private reachability, sign-in and one model request
before allowing intended users to connect. Verify the external firewall
from an authorized client. No EC2 deployment or firewall change is implied
by these documentation instructions.

See [Docker's port-publishing documentation](https://docs.docker.com/engine/network/port-publishing/)
for binding behaviour. The backend and frontend guides describe implementation
limits; they are not evidence of a completed security assessment.
