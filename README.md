# Project Name

This project integrates a Streamlit frontend with a FastAPI backend, leveraging AI services such as Ollama + LiteLLM within Docker containers, alongside a PostgreSQL database. It is designed to provide a seamless development and deployment workflow for a language processing application.

## Prerequisites

Ensure you have Docker, Docker Compose, and Git installed on your machine. Python 3.10 and Poetry are optional for local setups but recommended for managing dependencies and running the application outside of Docker.

## Getting Started

First, clone the project repository:

git clone <repository-url>
cd <project-directory>

Replace <repository-url> and <project-directory> with your repository's URL and the name of the directory you wish to clone into, respectively.

## Development Setup

For development, Docker Compose is used to orchestrate the application's services, enabling live code reloading for rapid development.

### Environment Setup

1. Build and Start Services

   Run the following command to build and start the containers. This setup mounts your local code into the containers, enabling live reloading:

   docker-compose up --build

2. Accessing the Application

   - Streamlit frontend will be accessible at: http://localhost:8501
   - FastAPI backend (Swagger UI) at: http://localhost:8000/docs

### Code Changes

Changes made to the codebase will automatically reflect in the running containers, thanks to Docker volumes that mount the code inside the containers.

## Production Deployment

For production, the application should be deployed with Docker, ensuring that the code is copied into the images rather than mounted.

### Preparing for Production

1. Adjust docker-compose.yml for Production

   It's advisable to remove or comment out the volume mounts in docker-compose.yml for the frontend and backend services. This ensures the containers run with the code copied at build time, not the live-mounted code.

2. Rebuild and Start Containers

   Use the following command to rebuild the images and start the containers in detached mode:

   docker-compose up --build -d

## Dependency Management

This project uses Poetry for Python dependency management in both the frontend and backend. Here's how to manage those dependencies:

1. **Adding a Dependency**:
   - Navigate to the respective directory (`frontend` or `backend`):
     ```bash
     cd frontend # or backend
     ```
   - Run Poetry to add a new dependency:
     ```bash
     poetry add <package-name>
     ```
   - This command updates `pyproject.toml` and `poetry.lock`. Commit these changes to your repository.

2. **Installing Dependencies Locally**:
   - To set up a local development environment with all dependencies, run:
     ```bash
     poetry install
     ```
   - This is useful for running the application or tests locally outside Docker.

3. **Running Commands with Poetry**:
   - Use `poetry run` to execute commands within the virtual environment created by Poetry, for example:
     ```bash
     poetry run pytest
     ```

**Note**: While developing within Docker containers, you typically won't need to run Poetry commands directly, as dependencies are installed during the Docker build process. However, these steps are essential for local development, adding/updating dependencies, or when setting up CI/CD pipelines.

### Reflecting Dependency Changes in Docker Containers

After updating dependencies, ensure to rebuild your Docker images to apply these changes in your containers:

```bash
docker-compose build
