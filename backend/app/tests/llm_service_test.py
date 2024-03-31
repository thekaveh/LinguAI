import unittest
from unittest.mock import patch, MagicMock
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from ollama import Client
from app.core.config import Config
from app.services.llm_service import LLMService

class TestLLMService(unittest.TestCase):
    @patch.object(ChatOpenAI, '__init__', return_value=None)
    def test_get_chat_runnable_openai(self, mock_chat_openai):
        model = "gpt-3"
        runnable = LLMService.get_chat_runnable(model)
        mock_chat_openai.assert_called_once_with(
            model=model,
            streaming=True,
            temperature=0,
            base_url=Config.OPENAI_API_ENDPOINT,
            openai_api_key=Config.OPENAI_API_KEY,
        )
        self.assertIsInstance(runnable, ChatOpenAI)

    @patch.object(ChatOllama, '__init__', return_value=None)
    def test_get_chat_runnable_ollama(self, mock_chat_ollama):
        model = "ollama-1"
        runnable = LLMService.get_chat_runnable(model)
        mock_chat_ollama.assert_called_once_with(
            model=model,
            streaming=True,
            temperature=0,
            base_url=Config.OLLAMA_API_ENDPOINT,
        )
        self.assertIsInstance(runnable, ChatOllama)

    @patch.object(Client, 'list', return_value={"models": [{"model": "ollama-1"}]})
    def test_list_models(self, mock_client_list):
        Config.OLLAMA_API_ENDPOINT = "http://ollama.ai"
        Config.OPENAI_API_KEY = "key"
        Config.OPENAI_MODELS = "gpt-3"
        models = LLMService.list_models()
        mock_client_list.assert_called_once()
        self.assertEqual(models, ["ollama-1", "gpt-3"])

    @patch.object(LLMService, 'list_models', return_value=["gpt-3", "vision-1"])
    def test_list_vision_models(self, mock_list_models):
        Config.VISION_MODELS = "vision-1"
        vision_models = LLMService.list_vision_models()
        mock_list_models.assert_called_once()
        self.assertEqual(vision_models, ["vision-1"])

if __name__ == '__main__':
    unittest.main()