import pytest
from unittest.mock import AsyncMock
from typing import List
from core.config import Config
from models.persona import Persona
from utils.http_utils import HttpUtils
from services.persona_service import PersonaService

@pytest.mark.asyncio
async def test_get_all_success():
    # Mock HttpUtils.get to return a list of Persona objects
    personas = [Persona(persona_id=1, persona_name="Persona1", description="Description1", is_default=False),
                Persona(persona_id=2, persona_name="Persona2", description="Description2", is_default=False)]
    HttpUtils.get = AsyncMock(return_value=personas)

    # Test and assertion
    result = await PersonaService.get_all()
    assert result == personas
    HttpUtils.get.assert_awaited_once_with(Config.PERSONA_SERVICE_LIST_ENDPOINT, response_model=List[Persona])

@pytest.mark.asyncio
async def test_get_all_names_success():
    # Mock PersonaService.get_all to return a list of Persona objects
    personas = [Persona(persona_id=1, persona_name="Persona1", description="Description1", is_default=False),
                Persona(persona_id=2, persona_name="Persona2", description="Description2", is_default=False)]
    PersonaService.get_all = AsyncMock(return_value=personas)

    # Test and assertion
    result = await PersonaService.get_all_names()
    assert result == ["Persona1", "Persona2"]
    PersonaService.get_all.assert_awaited_once()
