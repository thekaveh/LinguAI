from app.core.config import config
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class JokeService:
    def __init__(self):
        self.llm_local = ChatOpenAI(
            base_url=config.LLM_ENDPOINT_LOCAL
            , openai_api_key=config.LLM_API_KEY_LOCAL
        )
        self.llm_openai = ChatOpenAI(
            model="gpt-4"
            , base_url=config.LLM_ENDPOINT_OPENAI
            , openai_api_key=config.LLM_API_KEY_OPENAI
        )
        self.prompt_template = ChatPromptTemplate.from_template("tell me a short joke about {topic}")
        self.output_parser = StrOutputParser()

    def process(self, topic: str, llm_type: str) -> str:
        llm = self.llm_local if llm_type == "local" else self.llm_openai
        chain = self.prompt_template | llm | self.output_parser
        result = chain.invoke({"topic": topic})
        return result
