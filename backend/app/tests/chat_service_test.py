import pytest
from unittest.mock import AsyncMock, patch
from sqlmodel import Session, SQLModel, create_engine
from app.schema.chat import ChatRequest
from app.models.persona import Persona
from app.services.chat_service import ChatService
from typing import AsyncIterable

class TestChatService:
    @pytest.fixture
    def setup(self):
        engine = create_engine("sqlite:///:memory:")
        session = Session(engine)
        return session

    @patch('app.services.persona_service.PersonaService.get_by_name')
    @patch('app.services.llm_service.LLMService.get_chat_runnable')
    @pytest.mark.asyncio
    async def test_achat_with_valid_request(self, mock_get_chat_runnable, mock_get_by_name, setup):
        # Arrange
        mock_persona = AsyncMock(spec=Persona)
        mock_persona.description = "Mocked persona description"
        mock_get_by_name.return_value = mock_persona

        mock_get_chat_runnable.return_value = AsyncMock()

        chat_service = ChatService(db_session=setup)
        chat_request = ChatRequest(
            model="gpt-3",
            messages=[{"sender": "test-sender", "text": "Hello, world!"}],
            persona="existing_persona",
            temperature=0.5
        )

        # Act
        result = await chat_service.achat(request=chat_request)

        # Assert
        assert isinstance(result, AsyncIterable), "Result must be an AsyncIterable"
        mock_get_by_name.assert_called_once_with(name="existing_persona")
        mock_get_chat_runnable.assert_called_once_with(model="gpt-3", temperature=0.5)

    @patch('app.services.persona_service.PersonaService.get_by_name')
    @patch('app.services.llm_service.LLMService.get_chat_runnable')
    @pytest.mark.asyncio
    async def test_achat_with_invalid_persona(self, mock_get_chat_runnable, mock_get_by_name, setup):
        # Arrange
        mock_get_by_name.return_value = None

        chat_service = ChatService(db_session=setup)
        chat_request = ChatRequest(
            model="gpt-3",
            messages=[{"sender": "test-sender", "text": "Hello, world!"}],
            persona="non_existing_persona",
            temperature=0.5
        )

        # Act & Assert
        with pytest.raises(ValueError):
            await chat_service.achat(request=chat_request)

    @patch('app.services.persona_service.PersonaService.get_by_name')
    @patch('app.services.llm_service.LLMService.get_chat_runnable')
    @pytest.mark.asyncio
    async def test_achat_with_empty_messages(self, mock_get_chat_runnable, mock_get_by_name, setup):
        # Arrange
        mock_persona = AsyncMock(spec=Persona)
        mock_persona.description = "Mocked persona description"
        mock_get_by_name.return_value = mock_persona

        mock_get_chat_runnable.return_value = AsyncMock()

        chat_service = ChatService(db_session=setup)
        chat_request = ChatRequest(
            model="gpt-3",
            messages=[],
            persona="existing_persona",
            temperature=0.5
        )

        # Act & Assert
        with pytest.raises(AssertionError, match="messages must not be empty"):
            await chat_service.achat(request=chat_request)
