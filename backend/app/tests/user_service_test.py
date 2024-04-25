from datetime import date, datetime
import pytest
from unittest.mock import MagicMock, patch
from sqlalchemy.orm import Session
from app.services.user_service import UserService
from app.schema.user import User, UserCreate
from app.data_access.models.user import User as DBUser, UserAssessment, UserTopic
from app.schema.language import Language
from app.schema.user_topic import UserTopicBase
from app.schema.user_assessment import UserAssessmentCreate, UserAssessmentBase
from app.schema.authentication import AuthenticationRequest, AuthenticationResponse
from app.schema.language import LanguageCreate, Language as LanguageSchema
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

def test_get_user_topics(user_service, mock_db_session):
    # Create a mock DBUser instance with a topics attribute
    db_user = DBUser(user_id=1)
    db_user.topics = ["topic1", "topic2"]
    
    # Mock the user_repo.find_by_id method to return the mock DBUser instance
    user_service.user_repo.find_by_id = MagicMock(return_value=db_user)

    # Call the method and check the result
    result = user_service.get_user_topics(1)
    assert result == ["topic1", "topic2"]

def test_authenticate(user_service):
    password = "password"
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    request = AuthenticationRequest(username="username", password=password)
    user_service.user_repo.find_by_username = MagicMock(return_value=DBUser(username="username", password_hash=hashed_password.decode('utf-8')))
    user_service.authenticate(request)

def test_create_user_assessment(user_service, mock_db_session):
    language_data = Language(language_id=1, language_name="English")
    assessment_data = UserAssessmentCreate(
        user_id=1,
        language=language_data,
        assessment_date=datetime.today(),
        assessment_type="Initial",
        skill_level="beginner",
        strength="Listening",
        weakness="Speaking",
        language_id=1,
    )
    user_service.create_user_assessment(1, assessment_data)
    mock_db_session.add.assert_called_once()
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

def test_get_user_assessment(user_service, mock_db_session):
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = UserAssessment(assessment_id=1)
    result = user_service.get_user_assessment(1)
    assert isinstance(result, UserAssessment)

def test_update_user_assessment(user_service, mock_db_session):
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = UserAssessment(assessment_id=1)
    language_data = Language(language_id=1, language_name="English")
    assessment_data = UserAssessmentCreate(
        user_id=1,
        language=language_data,
        assessment_date=datetime.today(),
        assessment_type="Updated",
        skill_level="intermediate",
        strength="Reading",
        weakness="Writing",
        language_id=1,
    )
    user_service.update_user_assessment(1, assessment_data)
    mock_db_session.commit.assert_called_once()
    mock_db_session.refresh.assert_called_once()

def test_delete_user_assessment(user_service, mock_db_session):
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = UserAssessment(assessment_id=1)
    user_service.delete_user_assessment(1)
    mock_db_session.delete.assert_called_once()
    mock_db_session.commit.assert_called_once()

def test_update_user_languages(user_service, mock_db_session):
    user = User(
        user_id=1,
        username="test",
        email="test@example.com",
        user_type="type",
        first_name="Test",
        last_name="User",
        learning_languages=["English", "Spanish"]
    )
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = DBUser(username="test", learning_languages=[])

    with patch.object(user_service.language_service, 'get_language_by_name', return_value=LanguageSchema(language_name="English", language_id=1)):
        user_service.update_user_languages("test", user)
    mock_db_session.commit.assert_called_once()

def test_update_user_profile(user_service, mock_db_session):
    user_update = UserCreate(
        username="test",
        user_type="type",
        password_hash="password",
        first_name="Test",
        middle_name="Middle",
        last_name="User",
        preferred_name="Test",
        base_language="English",
        gender="Male",
        email="test@example.com",
        mobile_phone="1234567890",
        contact_preference="Email",
    )
    user_service.update_user_profile("test", user_update)
    mock_db_session.commit.assert_called_once()

def test_change_password(user_service, mock_db_session):
    hashed_password = bcrypt.hashpw("old_password".encode('utf-8'), bcrypt.gensalt())
    mock_query = mock_db_session.query.return_value
    mock_query.filter.return_value.first.return_value = DBUser(username="test", password_hash=hashed_password.decode()) 
    user_service.change_password("test", "old_password", "new_password")
    mock_db_session.commit.assert_called_once()