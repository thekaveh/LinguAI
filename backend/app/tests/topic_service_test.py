import pytest
from unittest.mock import MagicMock
from app.services.topic_service import TopicService
from app.schema.topic import TopicCreate, Topic as TopicSchema

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def topic_service(mock_db_session):
    return TopicService(mock_db_session)

def test_create_topic(topic_service, mock_db_session):
    mock_topic_create = TopicCreate(topic_name="Test Topic")
    mock_db_topic = MagicMock()
    mock_db_topic.topic_id = 1
    mock_db_topic.topic_name = "Test Topic"

    topic_service.topic_repo.create = MagicMock(return_value=mock_db_topic)

    created_topic = topic_service.create_topic(mock_topic_create)

    assert created_topic.topic_id == mock_db_topic.topic_id
    assert created_topic.topic_name == mock_db_topic.topic_name

def test_get_topic_by_id(topic_service, mock_db_session):
    mock_topic_id = 1
    mock_db_topic = MagicMock()
    mock_db_topic.topic_id = 1
    mock_db_topic.topic_name = "Test Topic"

    topic_service.topic_repo.find_by_topic_id = MagicMock(return_value=mock_db_topic)

    retrieved_topic = topic_service.get_topic_by_id(mock_topic_id)

    assert retrieved_topic.topic_id == mock_db_topic.topic_id
    assert retrieved_topic.topic_name == mock_db_topic.topic_name

def test_get_all_topics(topic_service, mock_db_session):
    mock_db_topics = [MagicMock(), MagicMock()]
    for idx, mock_topic in enumerate(mock_db_topics):
        mock_topic.topic_id = idx + 1
        mock_topic.topic_name = f"Topic {idx + 1}"

    topic_service.topic_repo.find_all = MagicMock(return_value=mock_db_topics)

    retrieved_topics = topic_service.get_all_topics()

    assert len(retrieved_topics) == len(mock_db_topics)
    for idx, retrieved_topic in enumerate(retrieved_topics):
        assert retrieved_topic.topic_id == mock_db_topics[idx].topic_id
        assert retrieved_topic.topic_name == mock_db_topics[idx].topic_name

def test_update_topic(topic_service, mock_db_session):
    mock_topic_id = 1
    mock_topic_update = TopicCreate(topic_name="Updated Topic")
    mock_db_topic = MagicMock()
    mock_db_topic.topic_id = 1
    mock_db_topic.topic_name = "Test Topic"
    mock_updated_topic = MagicMock()
    mock_updated_topic.topic_id = 1
    mock_updated_topic.topic_name = "Updated Topic"

    topic_service.topic_repo.find_by_topic_id = MagicMock(return_value=mock_db_topic)
    topic_service.topic_repo.update = MagicMock(return_value=mock_updated_topic)

    updated_topic = topic_service.update_topic(mock_topic_id, mock_topic_update)

    assert updated_topic.topic_id == mock_updated_topic.topic_id
    assert updated_topic.topic_name == mock_updated_topic.topic_name

def test_delete_topic(topic_service, mock_db_session):
    mock_topic_id = 1

    topic_service.topic_repo.delete = MagicMock()

    topic_service.delete_topic(mock_topic_id)

    topic_service.topic_repo.delete.assert_called_once_with(mock_topic_id)
