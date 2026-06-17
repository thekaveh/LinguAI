import pytest
from unittest.mock import Mock
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession

from app.schema.content_gen import ContentGenReq, Content, Language
from app.services.content_gen_service import ContentGenService
from app.services.llm_service import LLMService


@pytest.fixture
def sql_model_session():
    return Mock(spec=SqlModelSession)


@pytest.fixture
def llm_service():
    return Mock(spec=LLMService)


@pytest.fixture
def content_gen_req():
    mock = Mock(spec=ContentGenReq)
    mock.content = Content(content_name="content_name", content_id=1)
    mock.skill_level = "skill_level"
    mock.user_topics = ["topic1", "topic2"]
    mock.language = Language(language_name="language_name", language_id=1)
    return mock


@pytest.fixture
def service(sql_model_session):
    return ContentGenService(sql_model_session)


def test_init(service, sql_model_session):
    assert service.sql_model_session is sql_model_session


def test_generate_prompt_returns_string_with_request_fields(service, content_gen_req):
    """`_generate_prompt` no longer touches the prompts table — it returns a
    deterministic string built from the request fields."""
    result = service._generate_prompt(content_gen_req)
    assert isinstance(result, str)
    assert "content_name" in result
    assert "topic1" in result and "topic2" in result
    assert "language_name" in result
