from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from app.core.config import Config
from app.services.llm_service import LlmService

class JokeService:
    def __init__(self):
        self.prompt_template = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
        self.output_parser = StrOutputParser()

    def process(self, topic: str, llm_type: str) -> str:
        llm = LlmService().get_llm(llm_type)
        chain = self.prompt_template | llm | self.output_parser
        result = chain.invoke({"topic": topic})
        return result
