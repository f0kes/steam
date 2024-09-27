from typing import AsyncIterator

from redis import Redis

import AlchSessionManager
from AlchCrud import AlchCrud
from id_providers.SteamIdProvider import SteamIdProvider


class TrackingSteamIDProvider(SteamIdProvider):
    # searches for not recently updated tracked steam ids
    # if not enough, searches for eligible untracked steam ids to add to the tracking list

    def __init__(self, alch_crud: AlchCrud, session_manager: AlchSessionManager.AlchSessionManager) -> None:
        self.alch_crud = alch_crud
        self.session_manager = session_manager

    async def get_ids(self, n=100) -> set[int]:
        async with self.session_manager.session() as session:
            await self.alch_crud.remove_dead_tracked_users(session)
            tracked_users = await self.alch_crud.get_tracked_users(session)
            if len(tracked_users) < n:
                await self.alch_crud.add_tracked_users(session, n - len(tracked_users))
            tracked_users = await self.alch_crud.get_tracked_users(session)
            return set(tracked_users)
