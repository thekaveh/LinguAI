from __future__ import annotations
import httpx
import pytest
import respx

from models.services.polyglot_puzzle_service import PolyglotPuzzleService
from models.domain.polyglot_puzzle import PolyglotPuzzleRequest


@pytest.mark.asyncio
async def test_generate_returns_validated_response():
    async with httpx.AsyncClient(base_url="http://test/v1") as http:
        with respx.mock() as router:
            router.post("http://test/v1/polyglot_puzzle/generate").mock(
                return_value=httpx.Response(200, json={
                    "src_lang_question": "Hello",
                    "dst_lang_question": "Hola",
                })
            )
            svc = PolyglotPuzzleService(http)
            r = await svc.generate(PolyglotPuzzleRequest(
                src_lang="English", dst_lang="Spanish",
                difficulty="Easy", llm_id=1, llm_temperature=0.0,
            ))
            assert r.src_lang_question == "Hello"
            assert r.dst_lang_question == "Hola"
