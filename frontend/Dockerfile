FROM python:3.10-slim

# Build context is the repo root (see docker-compose.yml). VMx is a published
# PyPI dependency (vmx>=2.6.0) resolved by Poetry at install time — no source
# copy needed. Context stays at the repo root for parity with the compose files.
WORKDIR /app/frontend

RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo America/New_York > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Build context is repo root (see docker-compose.yml). Copy deps first for cache.
COPY frontend/pyproject.toml frontend/poetry.lock* /app/frontend/

RUN pip install --no-cache-dir "poetry==2.4.1" && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

COPY frontend /app/frontend

CMD ["python", "-m", "main"]
