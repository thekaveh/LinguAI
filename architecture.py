from diagrams import Diagram, Cluster
from diagrams.onprem.client import Users
from diagrams.aws.security import Cognito
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.framework import FastAPI

with Diagram("LinguAI System Architecture", show=True):
    clients = Users("Clients")

    with Cluster("AWS"):
        cognito = Cognito("AWS Cognito")

        with Cluster("EC2 Instance"):
            with Cluster("LinguAI Composite Docker Container"):
                with Cluster("db service"):
                    db = PostgreSQL("Postgres DB Engine")

                with Cluster("db-dashboard"):
                    db_dashboard = Docker("pgAdmin DB Dashboard")

                    db_dashboard >> db

                with Cluster("ollama service"):
                    ollama = Docker("LLM Engine\n (Ollama)")

                with Cluster("backend service"):
                    backend = FastAPI("Backend\n(FastAPI+LangChain+SqlAlchemy)")

                    backend >> db
                    backend >> ollama

                with Cluster("frontend service"):
                    frontend = Docker("Frontend\n(Streamlit)")

                    frontend >> backend
                    frontend >> cognito

    clients >> frontend
