# Use an official Python runtime as a parent image, updated to Python 3.10
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copying pyproject.toml and poetry.lock* first to leverage Docker cache
COPY ./pyproject.toml ./poetry.lock* /app/

# Install Poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy the rest of the application code
COPY . /app

# Command to run the app, ensuring reload is available for development
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]