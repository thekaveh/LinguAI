# Using Python 3.10 as the base image for compatibility with both Streamlit and FastAPI
FROM python:3.10-slim

# Set the working directory in the container to /app
WORKDIR /app

# Copy only the dependency management files initially to leverage Docker cache
COPY ./pyproject.toml ./poetry.lock* /app/

# Install Poetry and dependencies in a single layer to keep the image size down
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev

# Copy the rest of the application's code into the container
COPY . /app

# Expose the port Streamlit runs on
EXPOSE 8501

# Specify the command to run the Streamlit app
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]