import pytest
from unittest.mock import patch, AsyncMock
from services.persona_service import PersonaService
from models.persona import Persona
from core.config import Config
from typing import List

class TestPersonaService:
    @pytest.mark.asyncio
    @patch('services.persona_service.HttpUtils.get', new_callable=AsyncMock)
    async def test_aget_all(self, mock_get):
        # Arrange
        mock_persona = Persona(persona_id=1, persona_name="persona1", description="description")
        mock_get.return_value = [mock_persona, mock_persona]

        # Act
        result = await PersonaService.aget_all()

        # Assert
        mock_get.assert_called_once_with(Config.PERSONA_SERVICE_LIST_ENDPOINT, response_model=List[Persona])
        assert len(result) == 2
        assert result[0].persona_id == 1
        assert result[0].persona_name == "persona1"

    @pytest.mark.asyncio
    @patch('services.persona_service.PersonaService.aget_all', new_callable=AsyncMock)
    async def test_aget_all_names(self, mock_aget_all):
        # Arrange
        mock_persona = Persona(persona_id=1, persona_name="persona1", description="description")
        mock_aget_all.return_value = [mock_persona, mock_persona]

        # Act
        result = await PersonaService.aget_all_names()

        # Assert
        mock_aget_all.assert_called_once()
        assert len(result) == 2
        assert result[0] == "persona1"