import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from app.schema.content_gen import ContentGenReq, Content, Language
from app.services.content_gen_service import ContentGenService

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def mock_content_gen_req():
    return ContentGenReq(
        user_id=1,
        user_topics=["topic1", "topic2"],
        content=Content(content_name="content1", content_id=1),
        language=Language(language_name="English", language_id=1),
        skill_level="beginner",
        model_name="model name",
        temperature=0.8
    )

@pytest.fixture
def content_gen_service(mock_db_session):
    return ContentGenService(mock_db_session)

@patch('app.services.content_gen_service.LLMService.get_chat_runnable', new_callable=AsyncMock)
@patch('app.services.content_gen_service.StrOutputParser')
@patch('app.services.content_gen_service.ChatPromptTemplate.from_messages')
@patch('app.services.content_gen_service.SystemMessage')
@pytest.mark.asyncio
async def test_agenerate_content(mock_system_message, mock_chat_prompt_template, mock_str_output_parser, mock_get_chat_runnable, content_gen_service, mock_content_gen_req):
    mock_get_chat_runnable.return_value = AsyncMock()
    mock_str_output_parser.return_value = AsyncMock()
    mock_chat_prompt_template.return_value = AsyncMock()
    mock_system_message.return_value = AsyncMock()

    async_generator = await content_gen_service.agenerate_content(mock_content_gen_req)
    async for _ in async_generator:
        pass

    assert mock_system_message.call_count == 1, "SystemMessage should be called once."
    assert mock_chat_prompt_template.call_count == 1, "ChatPromptTemplate.from_messages should be called once."
    assert mock_get_chat_runnable.call_count == 1, "LLMService.get_chat_runnable should be called once."
    assert mock_str_output_parser.call_count == 1, "StrOutputParser should be called once."

@patch('app.services.content_gen_service.PromptSearch')
@patch('app.services.content_gen_service.PromptService')
def test__generate_prompt(mock_prompt_service, mock_prompt_search, content_gen_service, mock_content_gen_req):
    mock_prompt_service.get_prompt_by_search_criteria.return_value = MagicMock()

    result = content_gen_service._generate_prompt(mock_content_gen_req)

    assert mock_prompt_search.call_count == 1, "PromptSearch should be called once."
    # assert mock_prompt_service.get_prompt_by_search_criteria.call_count == 1, "PromptService.get_prompt_by_search_criteria should be called once."
    assert isinstance(result, str), "The result of _generate_prompt should be a string."