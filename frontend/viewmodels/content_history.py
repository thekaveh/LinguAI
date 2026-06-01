"""Shared content-history helper used by ContentGen, Rewrite, Review.

Each content page has the same shape:
- on successful generation, save the (input, output, level, language) to backend with a type discriminator
- a list of historical entries fetched per user × type
- ability to delete an entry

Rather than duplicating the boilerplate in each VM, expose a small helper that
each VM composes.
"""
from __future__ import annotations
import datetime
from typing import Optional

from models.services.user_content_service import UserContentService
from models.services.user_service import UserService
from models.schemas.user_content import UserContentBase, UserContentSearch, UserContent
from viewmodels.shell.user_session_vm import UserSessionVM
from viewmodels.shell.notification_center_vm import NotificationCenterVM


class ContentHistoryHelper:
    """Composable helper. Each content VM owns one; the VM manages a state field
    that holds the history tuple; this helper does the I/O.
    """

    def __init__(
        self,
        *,
        content_type: int,
        user_content_svc: UserContentService,
        user_svc: UserService,
        session: UserSessionVM,
        notifications: NotificationCenterVM,
    ) -> None:
        self._type = content_type
        self._svc = user_content_svc
        self._user_svc = user_svc
        self._session = session
        self._notify = notifications

    async def save(
        self,
        *,
        user_content: Optional[str],
        gen_content: str,
        language: Optional[str],
        level: Optional[str],
    ) -> None:
        """Persist a generation outcome. Best-effort; failures push an error toast but don't raise."""
        if not self._session.model.username:
            return
        try:
            user = await self._user_svc.get_by_username(self._session.model.username)
            user_id = getattr(user, "user_id", None)
            if user_id is None:
                return
            now = datetime.datetime.now(datetime.timezone.utc)
            payload = UserContentBase(
                user_id=user_id,
                user_content=user_content,
                gen_content=gen_content,
                type=self._type,
                level=level,
                language=language,
                created_date=now,
                expiry_date=now + datetime.timedelta(days=7),
            )
            await self._svc.create(payload)
        except Exception as e:
            self._notify.push_warning(f"Could not save to history: {e}")

    async def fetch(self) -> tuple[UserContent, ...]:
        """Return the user's content rows of this type. Best-effort; empty on error."""
        if not self._session.model.username:
            return ()
        try:
            user = await self._user_svc.get_by_username(self._session.model.username)
            user_id = getattr(user, "user_id", None)
            if user_id is None:
                return ()
            items = await self._svc.search(
                UserContentSearch(user_id=user_id, content_type=self._type)
            )
            return tuple(items)
        except Exception:
            return ()

    async def delete(self, content_id: int) -> None:
        try:
            await self._svc.delete(content_id)
        except Exception as e:
            self._notify.push_warning(f"Could not delete: {e}")
