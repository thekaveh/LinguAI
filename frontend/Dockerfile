FROM python:3.10-slim

# Mirror the repo layout inside the image so the pyproject's relative
# path-dep `vmx = {path = "../external/vmx/langs/python"}` resolves correctly:
# /app/frontend/pyproject.toml + /app/external/vmx/ → `../external/...` works.
WORKDIR /app/frontend

RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo America/New_York > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Build context is repo root (see docker-compose.yml). Copy deps first for cache.
COPY frontend/pyproject.toml frontend/poetry.lock* /app/frontend/
COPY external/vmx /app/external/vmx

RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

COPY frontend /app/frontend

CMD ["python", "-m", "main"]
