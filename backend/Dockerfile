# Use an official Python runtime as a parent image, updated to Python 3.10
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install tzdata and set the timezone. `apt-get update` is required before any
# `install` because the base image ships without package lists; clean afterwards
# to keep the image small.
RUN apt-get update && apt-get install -y --no-install-recommends tzdata && \
    ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
    echo America/New_York > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# Copying pyproject.toml and poetry.lock first to leverage Docker cache. The
# lock is required (no glob fallback) so a missing lock fails the build loudly
# instead of silently resolving fresh versions.
COPY ./pyproject.toml ./poetry.lock /app/

# Install Poetry and runtime dependencies. Pinned to the same version that
# generated poetry.lock (matches the frontend image); `--without dev` replaces
# the deprecated `--no-dev`.
RUN pip install --no-cache-dir "poetry==2.4.1" && \
	poetry config virtualenvs.create false && \
	poetry install --no-root --without dev

# Copy the rest of the application code
COPY . /app

# Command to run the app, ensuring reload is available for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
