from datetime import date
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schema.user import UserCreate
from app.data_access.models.user import User as DBUser, UserAssessment, UserTopic
from app.schema.language import Language
from app.schema.user_topic import UserTopicBase
from app.schema.user_assessment import UserAssessmentCreate, UserAssessmentBase
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse
import bcrypt

class MockLanguage:
    def __init__(self, language_name, language_id):
        self.language_name = language_name
        self.language_id = language_id

@pytest.fixture
def mock_db_session():
    return MagicMock(spec=Session)

@pytest.fixture
def user_service(mock_db_session):
    return UserService(mock_db_session)

def test_hash_password(user_service):
    password = "password"
    hashed_password = user_service.hash_password(password)

    assert isinstance(hashed_password, str), "The hashed password should be a string."

def test_verify_password(user_service):
    password = "password"
    hashed_password = user_service.hash_password(password)

    assert user_service.verify_password(password, hashed_password), "The password should be verified correctly."

@patch('app.services.user_service.LanguageService')
@patch('app.services.user_service.UserRepository')
@patch('app.services.user_service.DBUser')
def test_create_user(mock_db_user, mock_user_repository, mock_language_service, user_service, mock_db_session):
    user_create = UserCreate(
        username="testuser",
        email="testuser@example.com",
        password_hash="password",
        user_type="type",
        # base_language="English",
        # learning_languages=["Spanish"],
        first_name="Test",
        last_name="User",
        preferred_name="Test",
        age=30,
        gender="Male",
        discovery_method="method",
        motivation="motivation",
        middle_name="Middle",
        mobile_phone="1234567890",
        landline_phone="0987654321",
        contact_preference="Email",
    )

    mock_db_user.return_value = MagicMock(spec=DBUser)
    mock_user_repository.return_value = MagicMock()
    mock_language = Language(language_name="Spanish", language_id=1)

    mock_language_service.language_repo.find_by_name.return_value = mock_language


    user = user_service.create_user(user_create)

    mock_db_session.add.assert_called(), "The user should be added to the session."
    mock_db_session.commit.assert_called(), "The session should be committed."
    mock_db_session.refresh.assert_called_with(user), "The user object should be refreshed."

def test_add_user_topics(user_service, mock_db_session):
    user = DBUser(user_id=1)
    topics = [UserTopicBase(user_id=1, topic_name="topic1"), UserTopicBase(user_id=1, topic_name="topic2")]
    user_service.add_user_topics(user, topics)
    mock_db_session.add_all.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_get_user_by_id(user_service):
    user_service.user_repo.find_by_id = MagicMock(return_value=DBUser(user_id=1))
    user_service.get_user_by_id(1)
    user_service.user_repo.find_by_id.assert_called_with(1)

def test_get_user_by_username(user_service):
    user_service.user_repo.find_by_username = MagicMock(return_value=DBUser(username="username"))
    user_service.get_user_by_username("username")
    user_service.user_repo.find_by_username.assert_called_with("username")

def test_get_users(user_service):
    user_service.user_repo.get_all_users = MagicMock()
    user_service.get_users()
    user_service.user_repo.get_all_users.assert_called_once()

def test_add_topic_to_user(user_service, mock_db_session):
    user_service.user_repo.find_by_id = MagicMock(return_value=DBUser(user_id=1))
    user_service.add_topic_to_user(1, "topic")
    mock_db_session.commit.assert_called_once()

def test_update_user_topics(user_service, mock_db_session):
    user = DBUser(user_id=1, username="username")
    user_service.update_user_topics("username", user)
    mock_db_session.commit.assert_called_once()

def test_remove_topic_from_user(user_service, mock_db_session):
    db_user = DBUser(user_id=1)
    topic = UserTopic(topic_name="topic", user_id=1)
    db_user.user_topics = [topic]
    user_service.user_repo.find_by_id = MagicMock(return_value=db_user)
    
    # Mock the query to return the same topic instance
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = topic

    user_service.remove_topic_from_user(1, "topic")
    mock_db_session.commit.assert_called_once()

# def test_get_user_topics(user_service):
#     user_service.user_repo.find_by_id = MagicMock(return_value=DBUser(user_id=1))
#     user_service.get_user_topics(1)

def test_authenticate(user_service):
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    request = AuthenticationRequest(username="username", password=password)
    user_service.user_repo.find_by_username = MagicMock(return_value=DBUser(username="username", password_hash=hashed_password.decode('utf-8')))
    user_service.authenticate(request)
