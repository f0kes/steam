from contextlib import asynccontextmanager
from typing import List, Type, AsyncGenerator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import sessionmaker

from sqlalchemy_utils import create_database, database_exists

from Model import Base, UserData, GameData


# todo: refactor, moving crud to another file. this class should only be responsible for creating the engine and session
# todo: add support for other databases


class AlchSessionManager:
    def __init__(self, host, port, user, password, database):
        self.engine = create_async_engine(f'postgresql+asyncpg://{user}:{password}@{host}:{port}/{database}')
        # if not database_exists(self.engine.url):
        #    create_database(self.engine.url)
        # Base.metadata.create_all(self.engine)
        self._session_factory = async_sessionmaker(bind=self.engine, expire_on_commit=False)

    async def create_all(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._session_factory() as session:
            yield session

    @asynccontextmanager
    async def session(self):
        try:
            async with self._session_factory() as session:
                yield session
        except:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self):
        await self.engine.dispose()
