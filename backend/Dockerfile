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

# Copying pyproject.toml and poetry.lock* first to leverage Docker cache
COPY ./pyproject.toml ./poetry.lock* /app/

# Install Poetry and runtime dependencies. Pin to <2 for now; `--without dev`
# is forward-compatible with Poetry 2.x, replacing the deprecated `--no-dev`.
RUN pip install --no-cache-dir "poetry<2" && \
	poetry config virtualenvs.create false && \
	poetry install --no-root --without dev

# Copy the rest of the application code
COPY . /app

# Command to run the app, ensuring reload is available for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"]
