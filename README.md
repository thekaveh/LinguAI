# Name
LinguaAI, a language processing and improvement assistant!

# Description
This project integrates a Streamlit frontend with a FastAPI+LangChain+SqlAlchemy backend, leveraging AI services of either Ollama or OpenAI, each within their respective Docker containers, alongside a prospective PostgreSQL database.

This documentation is designed to provide a seamless development and deployment workflow for this application.

## Prerequisites

Ensure you have Git, Docker, Docker Compose, installed on your machine. Python 3.10 and Poetry are optional for local setups but recommended for managing dependencies and running the application outside of Docker.

## Setup

This section provides a step-by-step guide for getting started and setting up the project.

For both development and deployment, `Docker Compose` is used to orchestrate the application's services, enabling live code reloading for rapid development.

1. Clone the project repository: `git clone https://github.com/thekaveh/LinguAI.git && cd LinguAI`

2. Copy the vanilla `.env.example` file as `.env`

3. If you intend to use OpenAI's LLMs, fill in the optional `OPENAI_API_KEY` environment variable entry in the `.env` file with your own OpenAI API key.

4. If you intend to use Ollama's LLMs Modify the optional `OLLAMA_MODELS` environment variable entry in the `.env` to specify the models you expect to use via Ollama.

5.1. First choose the relevant docker-compose.yml file based on the information in the table below.

|     **docker-compose-file-name**    | **environment** | **Ollama Source** | **Ollama processing** |
|:-----------------------------------:|:---------------:|:-----------------:|-----------------------|
|          docker-compose.yml         |       dev       |     dockerized    |          CPU          |
| docker-compose.ollama-localhost.dev |       dev       |     localhost     |        depends        |
|    docker-compose.ollama-none.dev   |       dev       |        none       |          N/A          |
|    docker-compose-gpu-nvidia.prod   |       prod      | dockerized        |       gpu/nvidia      |

5.2. Then run the following command to build and start the container services. This setup mounts your local code into the containers, enabling live reloading:

   `docker-compose -f {docker-compose-file-name} up --build`

Please note that you can optionally start services in detached mode using `docker-compose -f {docker-compose-file-name} up --build -d` but you won't be able to see the live logs any longer.

6. Accessing the Application

   - Streamlit frontend will be accessible at: `http://localhost:{FRONTEND_PORT}`
   - FastAPI backend (Swagger UI) at: `http://localhost:{BACKEND_PORT}/docs`
   - pgAdmin DB-dashboard will be accessible at: `http://localhost:{DB_DASHBOARD_PORT}`

7. Optionally, Use VSCode's Remote Container extension to connect to and develop directly inside one of the backend or frontend containers. To do this, find the `Remote Explorer` from VSCode's tools pane on the left, select `Dev Containers`, locate either the `linguai backend` or `linguai frontend` running container, and then `Attach in New Window`

8. To bring down the LinguAI services: `docker-compose down --remove-orphans`

9. When you have db changes including schema or data changes, simply run the following command in your terminal to take a snapshot of the database and replace the current snapshot:
    - `docker exec db sh ./scripts/db-snapshot.sh`

10. In order to make sure recent DB schema and data changes are reflected in your DB container, make sure you bring down the docker compose using the command below (with `-v`):
    - `docker-compose down -v --remove-orphans`

### Code Changes

Thanks to Docker volumes that mount the code inside the containers, changes made to the codebase will automatically reflect in the running containers and will, in turn, show up on both the running frontend and backend services. Once happy with your changes, you can simply commit them to Git branch you're working on regardless of whether you applied the changes from inside the running containers or outside.

## Production Deployment

For production, the application should be deployed with Docker, ensuring that the code is copied into the images rather than mounted.

For now the only supported and tested deployment scenario is to setup an EC2 instance, select the Ubuntu-Nvidia-PyTorch2 image, SSH into the newly deployed and running instance, and run the same environment setup steps as above before running the slightly modified docker compose command below:

`docker-compose -f docker-compose-gpu-nvidia.prod.yml up --build`

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

Please, note that you can also optionally attach to the running container and then run the `poetry add <package-name>` command.

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

Please, note that you can also optionally attach to the running container and then run the `poetry remove <package-name>` command.

3. **Running Commands with Poetry**:
   - Use `poetry run` to execute commands within the virtual environment created by Poetry, for example:
     ```bash
     poetry run pytest
     ```

Please, note that you can also optionally attach to the running container and then run the `poetry run` command.

**Note**: While developing within Docker containers, you typically won't need to run Poetry commands directly, as dependencies are installed during the Docker build process. However, these steps are essential for local development, adding/updating dependencies, or when setting up CI/CD pipelines.

### Reflecting Dependency Changes in Docker Containers

After updating dependencies, ensure to rebuild your Docker images to apply these changes in your containers:

```bash
docker-compose build
```

### System Architecture
![LinguAI System Architecture](/images/linguai_system_architecture.jpg)