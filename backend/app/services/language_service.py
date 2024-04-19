from typing import List, Optional
from sqlalchemy.orm import Session

from app.data_access.models.language import Language
from app.schema.language import LanguageCreate, Language as LanguageSchema
from app.data_access.repositories.language_repository import LanguageRepository


class LanguageService:
    """
    Service class for handling language-related operations.
    """

    def __init__(self, db_session: Session):
        self.language_repo = LanguageRepository(db_session)

    def get_language_by_name(self, language_name: str) -> Optional[LanguageSchema]:
        """
        Retrieves a language by its name.

        Args:
            language_name (str): The name of the language.

        Returns:
            Optional[LanguageSchema]: The language schema if found, None otherwise.
        """
        language = self.language_repo.find_by_name(language_name)
        if language:
            return LanguageSchema(**language.__dict__)
        return None

    def get_all_languages(self) -> List[LanguageSchema]:
        """
        Retrieves all languages.

        Returns:
            List[LanguageSchema]: A list of language schemas.
        """
        languages = self.language_repo.get_all_languages()
        return [LanguageSchema(**language.__dict__) for language in languages]