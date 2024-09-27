from datetime import datetime, timedelta
from typing import Type, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from AlchSessionManager import AlchSessionManager
from Model import UserData, FollowedUsers


class AlchCrud:
    def __init__(self, session_manager: AlchSessionManager):
        self.session_manager = session_manager

    async def _session(self) -> AsyncSession:
        return await self.session_manager.session()

    async def insert_any(self, session: AsyncSession, entry):
        session.add(entry)
        await session.commit()

    async def get_or_create(self, session: AsyncSession, model, **kwargs):
        q = select(model).filter_by(**kwargs)
        instance = await session.execute(q)
        instance = instance.scalars().first()
        if instance:
            return instance
        else:
            instance = model(**kwargs)
            session.add(instance)
            await session.commit()
            return instance

    async def filter_existing_users(self, session: AsyncSession, steam_ids: List[str]) -> List[UserData]:
        q = select(UserData).filter(UserData.steam_id.in_(steam_ids))
        result = await session.execute(q)
        return list(result.scalars().all())

    async def filter_non_existing_users(self, session: AsyncSession, steam_ids: List[int]) -> List[int]:
        q = select(UserData.steam_id).filter(UserData.steam_id.in_(steam_ids))
        existing_users = await session.execute(q)
        existing_ids = [i[0] for i in existing_users]
        non_existing_ids = list(set(steam_ids) - set(existing_ids))
        return non_existing_ids

    async def get_tracked_users(self, session: AsyncSession) -> List[int]:
        yesterday = datetime.now() - timedelta(days=1)
        q = (select(FollowedUsers.user_id)
             .join(UserData)
             .filter(UserData.last_updated < yesterday)
             .filter(UserData.is_dead_account.is_(False)))
        result = await session.execute(q)

        return list(result.scalars().all())

    async def add_tracked_users(self, session: AsyncSession, n: int):
        # select steam_id into followed_users from user_data left join followed_users on user_data.steam_id =
        # followed_users.steam_id where followed_users.steam_id is null and user_data.is_dead_account = false limit n;
        result = await self.get_untracked_users(session, n)
        for user_data in result:
            steam_id = user_data.steam_id
            followed_user = FollowedUsers(user_id=steam_id)
            session.add(followed_user)
        await session.commit()

    async def remove_dead_tracked_users(self, session: AsyncSession):
        q = select(FollowedUsers).join(UserData).filter(UserData.is_dead_account.is_(True))
        result = await session.execute(q)
        for user in result.scalars().all():
            await session.delete(user)
        await session.commit()
        return

    async def get_untracked_users(self, session, n) -> List[UserData]:
        q = (select(UserData).join(FollowedUsers, isouter=True)
             .filter(FollowedUsers.user_id.is_(None))
             .filter(UserData.is_dead_account.is_(False))
             .filter(UserData.last_updated < datetime.now() - timedelta(days=1))
             .limit(n))

        result = await session.execute(q)

        return list(result.scalars().all())
