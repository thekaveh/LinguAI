import pytest
from unittest.mock import Mock, AsyncMock
from sqlalchemy.orm import Session
from sqlmodel import Session as SqlModelSession
from app.schema.content_gen import ContentGenReq, Content, Language
from app.services.content_gen_service import ContentGenService
from app.services.prompt_service import PromptService
from app.services.llm_service import LLMService

@pytest.fixture
def db():
    # This fixture creates a mock object for the Session class from SQLAlchemy
    return Mock(spec=Session)

@pytest.fixture
def sql_model_session():
    # This fixture creates a mock object for the Session class from SQLModel
    return Mock(spec=SqlModelSession)

@pytest.fixture
def prompt_service():
    # This fixture creates a mock object for the PromptService class
    return Mock(spec=PromptService)

@pytest.fixture
def llm_service():
    # This fixture creates a mock object for the LLMService class
    return Mock(spec=LLMService)

@pytest.fixture
def content_gen_req():
    # This fixture creates a mock object for the ContentGenReq class and sets some attributes
    mock = Mock(spec=ContentGenReq)
    mock.content = Content(content_name="content_name", content_id=1)
    mock.skill_level = "skill_level"
    mock.user_topics = ["topic1", "topic2"]
    mock.language = Language(language_name="language_name", language_id=1)
    return mock

@pytest.fixture
def service(db, sql_model_session, prompt_service, llm_service):
    # This fixture creates an instance of the ContentGenService class and sets some attributes
    service = ContentGenService(db, sql_model_session)
    service.prompt_service = prompt_service
    service.llm_service = llm_service
    return service

def test_init(service, db, sql_model_session, prompt_service):
    # This test checks that the ContentGenService instance was initialized correctly
    assert service.db == db
    assert service.sql_model_session == sql_model_session
    assert isinstance(service.prompt_service, PromptService)

def test_generate_prompt(service, content_gen_req):
    # This test checks that the _generate_prompt method of the ContentGenService class is called correctly
    service._generate_prompt(content_gen_req)
    service.prompt_service.get_prompt_by_search_criteria.assert_called_once()