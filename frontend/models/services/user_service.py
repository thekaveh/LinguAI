from __future__ import annotations
import httpx

from models.schemas.user import User, UserCreate
from models.schemas.user_topic import UserTopicBase
from models.schemas.user_assessment import UserAssessment, UserAssessmentCreate


class UserService:
    def __init__(self, http: httpx.AsyncClient) -> None:
        self._http = http

    async def get_by_username(self, username: str) -> User:
        r = await self._http.get(f"/users/username/{username}")
        r.raise_for_status()
        return User.model_validate(r.json())

    async def get_id_by_username(self, username: str) -> int:
        r = await self._http.get(f"/users/username/{username}/id")
        r.raise_for_status()
        return int(r.json())

    async def create(self, payload: UserCreate) -> User:
        r = await self._http.post("/users/", json=payload.model_dump(mode="json"))
        r.raise_for_status()
        return User.model_validate(r.json())

    async def update(self, username: str, payload: User) -> User:
        r = await self._http.post(
            f"/users/{username}/update", json=payload.model_dump(mode="json")
        )
        r.raise_for_status()
        return User.model_validate(r.json())

    async def set_topics(self, username: str, topics: list[UserTopicBase]) -> None:
        r = await self._http.post(
            f"/users/{username}/topics",
            json=[t.model_dump(mode="json") for t in topics],
        )
        r.raise_for_status()

    async def add_topic(self, user_id: int, topic_name: str) -> None:
        r = await self._http.post(f"/users/{user_id}/topics/{topic_name}")
        r.raise_for_status()

    async def remove_topic(self, user_id: int, topic_name: str) -> None:
        r = await self._http.delete(f"/users/{user_id}/topics/{topic_name}")
        r.raise_for_status()

    async def add_assessment(
        self, user_id: int, payload: UserAssessmentCreate
    ) -> UserAssessment:
        r = await self._http.post(
            f"/users/{user_id}/assessments/", json=payload.model_dump(mode="json")
        )
        r.raise_for_status()
        return UserAssessment.model_validate(r.json())

    async def list(self) -> list[User]:
        r = await self._http.get("/users/list")
        r.raise_for_status()
        return [User.model_validate(x) for x in r.json()]

    async def delete_by_username(self, username: str) -> None:
        r = await self._http.delete(f"/users/{username}/delete")
        r.raise_for_status()
