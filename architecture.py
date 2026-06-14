"""Source for `images/linguai_system_architecture.jpg`.

Regenerate after editing:
    pip install diagrams
    # Graphviz must also be installed on the host (`brew install graphviz`
    # on macOS, `apt-get install graphviz` on Debian/Ubuntu).
    python architecture.py

The script writes a `.png` next to itself; rename to .jpg to overwrite
the asset referenced by README.md.
"""
from diagrams import Diagram, Cluster, Edge
from diagrams.onprem.client import Users
from diagrams.onprem.container import Docker
from diagrams.onprem.database import PostgreSQL
from diagrams.programming.framework import FastAPI


with Diagram("LinguAI System Architecture", show=False, filename="images/linguai_system_architecture"):
    clients = Users("Clients (browser)")

    with Cluster("Cloud LLM providers"):
        openai = Docker("OpenAI")
        groq = Docker("Groq")

    with Cluster("Docker Compose stack"):
        with Cluster("db service"):
            db = PostgreSQL("Postgres DB Engine")

        with Cluster("db-dashboard service"):
            db_dashboard = Docker("pgAdmin 4")
            db_dashboard >> db

        with Cluster("ollama service (optional)"):
            ollama = Docker("Local LLM runtime\n(Ollama)")

        with Cluster("backend service"):
            backend = FastAPI("Backend\n(FastAPI + LangChain + SQLModel)")
            backend >> db
            backend >> Edge(label="optional") >> ollama
            backend >> Edge(label="optional") >> openai
            backend >> Edge(label="optional") >> groq

        with Cluster("frontend service"):
            frontend = Docker("Frontend\n(NiceGUI + VMx, MVVM)")
            frontend >> backend
            # frontend depends_on db-dashboard so its boot is sequenced after the
            # DB is up (the dashboard transitively depends on the db service).
            frontend >> Edge(style="dashed", label="depends_on") >> db_dashboard

    clients >> frontend
