import requests
from config import Config

class APIClient:
    @staticmethod
    def get_hello_world():
        response = requests.get(Config.BACKEND_ENDPOINT)
        return response.json() if response.ok else {"Error": "Failed to fetch"}

    @staticmethod
    def call_joke_service(topic, llm_type):
        response = requests.post(f"{Config.BACKEND_ENDPOINT}/v1/joke", json={"topic": topic, "llm_type": llm_type})
        return response.json().get("result", "") if response.status_code == 200 else "Error"
