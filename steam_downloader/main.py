import asyncio
import datetime
import time

from redis import Redis

from AlchCrud import AlchCrud
from AlchSessionManager import AlchSessionManager
from AsyncLogger import AsyncLogger, GenericLogger
from Ledger import ApiKeyLedger
from Fetcher import Fetcher
from PlayTimeRecorder import PlayTimeRecorder
from id_providers.CompositeSteamIDProvider import CompositeSteamIDProvider
from id_providers.NewIdProvider import NewIdProvider
from UserFinder import UserFinder
from id_providers.TrackingSteamIDProvider import TrackingSteamIDProvider
from id_providers.UntrackedIdProvider import UntrackedIdProvider
from settings import *


def wait_list_checker(ledger: ApiKeyLedger):
    while True:
        ledger.check_wait_list()
        time.sleep(60)  # Check every minute


async def find_friends(user_finder: UserFinder, steam_id: int, logger: GenericLogger):
    while True:
        try:
            await user_finder.dfs(76561198035864385)
        except Exception as e:
            await logger.error(e)
            continue


async def collect_times(recorder: PlayTimeRecorder, logger: GenericLogger):
    await recorder.start_collecting()
    while True:
        try:
            await recorder.start_collecting()
        except Exception as e:
            await logger.error(e)
            continue


async def main():
    api_keys = [
        
    ]

    requests = requests_per_key
    logger = AsyncLogger(log_file='app.log')
    redis = Redis(host=redis_host, port=redis_port, db=redis_db)
    ledger = ApiKeyLedger(api_keys, redis, requests, logger, delay=datetime.timedelta(seconds=requests_timeout))
    fetcher = Fetcher(ledger, requests_per_second, logger)
    user_finder = UserFinder(fetcher, redis)
    session_manager = AlchSessionManager(postgres_host,
                                         postgres_port,
                                         postgres_user,
                                         postgres_password,
                                         postgres_database)
    crud = AlchCrud(session_manager)
    await session_manager.create_all()
    # id_provider = NewIdProvider(redis, crud, session_manager, logger)
    id_providers = {TrackingSteamIDProvider(crud, session_manager): 0.8,
                    UntrackedIdProvider(crud, session_manager): 0.2}
    main_id_provider = CompositeSteamIDProvider(id_providers)
    play_time_recorder = PlayTimeRecorder(crud, redis, fetcher, main_id_provider, session_manager, logger)
    if mode == "time":
        await collect_times(play_time_recorder, logger)
    elif mode == "friends":
        await play_time_recorder.start_collecting(requests_per_second)


if __name__ == '__main__':
    asyncio.run(main())
    # checker_thread = threading.Thread(target=wait_list_checker)
    # checker_thread.daemon = True
    # checker_thread.start()
