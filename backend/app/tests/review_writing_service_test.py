import pytest
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from app.schema.review_writing import ReviewWritingReq
from app.services.review_writing_service import ReviewWritingService

@pytest.fixture
def db():
    return Mock(spec=Session)

@pytest.fixture
def sql_model_session():
    return Mock(spec=SqlModelSession)

@pytest.fixture
def review_writing_req():
    mock = Mock(spec=ReviewWritingReq)
    mock.curr_skill_level = "beginner"
    mock.next_skill_level = "intermediate"
    mock.strength = "strength"
    mock.weakness = "weakness"
    mock.input_content = "input content"
    mock.language = "English"
    mock.llm_id = 1
    mock.temperature = 0.8
    return mock

@pytest.fixture
def service(db, sql_model_session):
    with patch('app.services.review_writing_service.PromptService'), \
         patch('app.services.review_writing_service.SkillLevelService'):
        service = ReviewWritingService(db, sql_model_session)
    return service

@patch('app.services.review_writing_service.ChatPromptTemplate.from_messages')
@patch('app.services.review_writing_service.LLMService')
@patch('app.services.review_writing_service.StrOutputParser')
@pytest.mark.asyncio
async def test_areview_writing(mock_str_output_parser, mock_llm_service, mock_chat_prompt_template, service, review_writing_req):
    # Arrange
    mock_llm_service.return_value.get_chat_runnable.return_value = AsyncMock()
    mock_str_output_parser.return_value = AsyncMock()

    # Act
    result = await service.areview_writing(review_writing_req)

    # Assert
    mock_chat_prompt_template.assert_called_once()
    mock_llm_service.assert_called_once_with(db_session=service.sql_model_session)
    mock_llm_service.return_value.get_chat_runnable.assert_called_once_with(llm_id=review_writing_req.llm_id, temperature=review_writing_req.temperature)
    mock_str_output_parser.assert_called_once()

@pytest.mark.parametrize("db_prompt", [None, Mock()])
def test__generate_prompt(service, review_writing_req, db_prompt):
    # Arrange
    service.prompt_service.get_prompt_by_search_criteria.return_value = db_prompt

    # Act
    result = service._generate_prompt(review_writing_req)

    # Assert
    service.prompt_service.get_prompt_by_search_criteria.assert_called_once()
    assert isinstance(result, str)