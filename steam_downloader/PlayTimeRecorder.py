import asyncio
from datetime import datetime

from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from AlchCrud import AlchCrud
from AlchSessionManager import AlchSessionManager
from AsyncLogger import GenericLogger
from Fetcher import Fetcher
from InputModel import UserHoursData
from Model import PlayedTime, UserData, GameData
from Result import Result
from id_providers.SteamIdProvider import SteamIdProvider


class PlayTimeRecorder:
    def __init__(self,
                 crud: AlchCrud,
                 redis: Redis,
                 fetcher: Fetcher,
                 id_provider: SteamIdProvider,
                 session_manager: AlchSessionManager,
                 logger: GenericLogger):
        self.crud = crud
        self.redis = redis
        self.fetcher = fetcher
        self.id_provider = id_provider
        self.session_manager = session_manager
        self.logger = logger

    async def start_collecting(self, requests_per_second=10):
        while True:
            await self.logger.info(f"Fetching steam ids, current time: {datetime.now()}")
            steam_ids = await self.id_provider.get_ids(requests_per_second)
            await self.logger.info(f"Fetched {len(steam_ids)} steam ids, current time: {datetime.now()}")
            tasks = [self.record_play_time(steam_id) for steam_id in steam_ids]
            data: tuple[Result[UserHoursData]] = await asyncio.gather(*tasks)
            await self.logger.info(
                f"Finished fetching playtime for {len(data)} steam ids, current time: {datetime.now()}")

    async def record_play_time(self, steam_id) -> Result[UserHoursData]:
        play_times_result = await self.fetcher.fetch_play_time(steam_id)
        if play_times_result.is_failure():
            return Result.failure(play_times_result.message)
        await self.save_hours_data(play_times_result.data)
        return Result.success(play_times_result.data)

    async def save_hours_data(self, play_times_result: UserHoursData):

        async with self.session_manager.session() as session:
            steam_id = play_times_result.steam_id
            user: UserData = await self.crud.get_or_create(session, UserData, steam_id=steam_id)
            two_week_sum = 0
            forever_sum = 0
            for raw_game in play_times_result.game_hours:
                game_model: GameData = await self.crud.get_or_create(session, GameData, id=raw_game.game_id)
                game_model.name = raw_game.game_name
                played_time = PlayedTime(steam_id=user.steam_id,
                                         game_id=game_model.id,
                                         playtime_two_weeks=raw_game.playtime_two_weeks,
                                         playtime_forever=raw_game.playtime_forever)
                two_week_sum += raw_game.playtime_two_weeks
                forever_sum += raw_game.playtime_forever
                await self.crud.insert_any(session, played_time)

                assert isinstance(session, AsyncSession)
            user.total_playtime = forever_sum
            user.total_playtime_two_weeks = two_week_sum
            user.last_updated = datetime.now()
            user.is_dead_account = two_week_sum == 0
            session.add(user)
            await session.commit()
            await self.logger.info(f"Saved playtime for {steam_id}")

        return
