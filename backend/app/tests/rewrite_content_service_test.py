import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from app.schema.rewrite_content import ContentRewriteReq
from app.services.rewrite_content_service import RewriteContentService

@pytest.fixture
def db():
    return Mock(spec=Session)

@pytest.fixture
def sql_model_session():
    return Mock(spec=SqlModelSession)

@pytest.fixture
def content_rewrite_req():
    mock = Mock(spec=ContentRewriteReq)
    mock.user_base_language = "English"
    mock.user_skill_level = "beginner"
    mock.skill_level = "beginner"
    mock.language = "English"
    mock.llm_id = 1
    mock.temperature = 0.8
    mock.input_content = "input content"
    return mock

@pytest.fixture
def service(db, sql_model_session):
    with patch('app.services.rewrite_content_service.PromptService'):
        service = RewriteContentService(db, sql_model_session)
    return service

@patch('app.services.rewrite_content_service.ChatPromptTemplate.from_messages')
@patch('app.services.rewrite_content_service.LLMService')
@patch('app.services.rewrite_content_service.StrOutputParser')
@patch('app.services.rewrite_content_service.SystemMessage')
@pytest.mark.asyncio
async def test_arewrite_content(mock_system_message, mock_str_output_parser, mock_llm_service, mock_chat_prompt_template, service, content_rewrite_req):
    # Arrange
    mock_llm_service.return_value.get_chat_runnable.return_value = AsyncMock()
    mock_str_output_parser.return_value = AsyncMock()

    # Act
    result = await service.arewrite_content(content_rewrite_req)

    # Assert
    mock_chat_prompt_template.assert_called_once()
    mock_llm_service.assert_called_once_with(db_session=service.sql_model_session)
    mock_llm_service.return_value.get_chat_runnable.assert_called_once_with(llm_id=content_rewrite_req.llm_id, temperature=content_rewrite_req.temperature)
    mock_str_output_parser.assert_called_once()

def test__generate_prompt(service, content_rewrite_req):
    # Arrange
    service.prompt_service.get_prompt_by_search_criteria.return_value = None

    # Act
    result = service._generate_prompt(content_rewrite_req)

    # Assert
    service.prompt_service.get_prompt_by_search_criteria.assert_called_once()
    assert isinstance(result, str)