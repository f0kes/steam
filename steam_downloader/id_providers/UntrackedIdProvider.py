from typing import AsyncIterator

from AlchCrud import AlchCrud
from AlchSessionManager import AlchSessionManager
from id_providers.SteamIdProvider import SteamIdProvider


class UntrackedIdProvider(SteamIdProvider):

    def __init__(self, alch_crud: AlchCrud, session_manager: AlchSessionManager) -> None:
        self.alch_crud = alch_crud
        self.session_manager = session_manager

    async def get_ids(self, n=100) -> set[int]:
        # searches for untracked steam ids
        async with self.session_manager.session() as session:
            untracked_users = await self.alch_crud.get_untracked_users(session, n)
            ids = [user.steam_id for user in untracked_users]
            return set(ids)
