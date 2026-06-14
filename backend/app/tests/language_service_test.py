import pytest
from unittest.mock import MagicMock
from app.services.language_service import LanguageService
from app.schema.language import Language

@pytest.fixture
def mock_db_session():
    return MagicMock()

@pytest.fixture
def language_service(mock_db_session):
    return LanguageService(mock_db_session)

def test_get_language_by_name(language_service, mock_db_session):
    # Mocking the behavior of LanguageRepository.find_by_name
    mock_language_name = "English"
    mock_db_language = MagicMock()
    mock_db_language.language_name = "English"  # Set name attribute directly
    mock_db_language.language_id = 1  # Set id attribute directly

    # Set return_value directly on the mocked method
    language_service.language_repo.find_by_name = MagicMock(return_value=mock_db_language)

    # Calling the method under test
    retrieved_language = language_service.get_language_by_name(mock_language_name)

    # Asserting that the method returns the correct language schema
    assert retrieved_language.language_name == mock_db_language.language_name
    assert retrieved_language.language_id == mock_db_language.language_id

def test_get_all_languages(language_service, mock_db_session):
    # Mocking the behavior of LanguageRepository.get_all_languages
    mock_db_languages = [MagicMock(), MagicMock()]
    for idx, mock_language in enumerate(mock_db_languages):
        mock_language.language_name = f"Language {idx + 1}"  # Set name attribute directly
        mock_language.language_id = idx + 1  # Set id attribute directly

    # Set return_value directly on the mocked method
    language_service.language_repo.get_all_languages = MagicMock(return_value=mock_db_languages)

    # Calling the method under test
    retrieved_languages = language_service.get_all_languages()

    # Asserting that the method returns the correct list of language schemas
    assert len(retrieved_languages) == len(mock_db_languages)
    for idx, retrieved_language in enumerate(retrieved_languages):
        assert retrieved_language.language_name == mock_db_languages[idx].language_name
        assert retrieved_language.language_id == mock_db_languages[idx].language_id
