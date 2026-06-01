from __future__ import annotations
import httpx

from models.schemas.user_content import UserContentBase, UserContentSearch, UserContent


class UserContentService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def create(self, payload: UserContentBase) -> UserContent:
        r = await self._http.post(
            "/user-contents/", json=payload.model_dump(mode="json")
        )
        r.raise_for_status()
        return UserContent.model_validate(r.json())

    async def search(self, params: UserContentSearch) -> list[UserContent]:
        r = await self._http.post(
            "/user-contents/search", json=params.model_dump(mode="json")
        )
        r.raise_for_status()
        return [UserContent.model_validate(x) for x in r.json()]

    async def delete(self, content_id: int) -> None:
        r = await self._http.delete(f"/user-contents/{content_id}")
        r.raise_for_status()
