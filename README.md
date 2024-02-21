# Name
LinguaAI, a language processing and improvement assistant!

# Description
This project integrates a Streamlit frontend with a FastAPI+LangChain+SqlAlchemy backend, leveraging AI services of either Ollama or OpenAI, each within their respective Docker containers, alongside a prospective PostgreSQL database.

This documentation is designed to provide a seamless development and deployment workflow for this application.

## Prerequisites

Ensure you have Git, Docker, Docker Compose, installed on your machine. Python 3.10 and Poetry are optional for local setups but recommended for managing dependencies and running the application outside of Docker.

## Getting Started

First, clone the project repository:

`git clone https://github.com/thekaveh/LinguAI.git && cd LinguAI`

## Development Setup

For development, Docker Compose is used to orchestrate the application's services, enabling live code reloading for rapid development. Optioanlly Use VSCode's Remote Container extension to develop inside a container.

### Environment Setup

1. Copy the `.env.example` file to `.env`

2. Fill in the optional `OPENAI_API_KEY` environment variable entry in the `.env` with your own OpenAI API key.

3. Modify the optional `OLLAMA_MODELS` environment variable entry in the `.env` to specify the models you would like pulled by Ollama at startup time.

4. Build and Start Services by running the following command to build and start the containers. This setup mounts your local code into the containers, enabling live reloading:

   `docker-compose up --build`

Please note that you can optionally start services in detached mode using `docker-compose up --build -d` but you won't be able to see the live logs any longer.

5. Accessing the Application

   - Streamlit frontend will be accessible at: `http://localhost:{FRONTEND_PORT}`
   - FastAPI backend (Swagger UI) at: `http://localhost:{BACKEND_PORT}/docs`

### Code Changes

Thanks to Docker volumes that mount the code inside the containers, changes made to the codebase will automatically reflect in the running containers and will, in turn, show up on both the running frontend and backend services. Once happy with your changes, you can simply commit them to Got branch you're working on regardless of whether you applied the changes from inside the running containers or outside.

## Production Deployment

For production, the application should be deployed with Docker, ensuring that the code is copied into the images rather than mounted.

For now the only supported and tested deployment scenario is to setup an EC2 instance, select the Ubuntu-Nvidia-PyTorch2 image, SSH into the newly deployed and running instance, and run the same environment setup steps as above before running the slightly modified docker compose command below:

`docker-compose -f docker-compose-nvidia.yml up --build`

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

2. **Removing a Dependency**:
   - Navigate to the respective directory (`frontend` or `backend`):
     ```bash
     cd frontend # or backend
     ```
   - Run Poetry to remove a dependency:
     ```bash
     poetry remove <package-name>
     ```
   - This command updates `pyproject.toml` and `poetry.lock`. Commit these changes to your repository.

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
```

### System Architecture
![LinguAI System Architecture](/images/linguai_system_architecture.png)