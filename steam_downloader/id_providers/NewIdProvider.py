import time

from redis import Redis

from AlchCrud import AlchCrud
from AlchSessionManager import AlchSessionManager
from AsyncLogger import GenericLogger
from id_providers.SteamIdProvider import SteamIdProvider


class NewIdProvider(SteamIdProvider):
    def __init__(self, redis_conn: Redis,
                 crud: AlchCrud,
                 session_manager: AlchSessionManager,
                 logger: GenericLogger):
        self.redis_conn = redis_conn
        self.crud = crud
        self.session_manager = session_manager
        self.id_set = self.redis_conn.smembers("stack")
        self.id_set = list([int(i) for i in self.id_set])
        self.logger = logger
        self.next_index = 0

    async def get_ids(self, n=15) -> set[int]:
        async with self.session_manager.session() as session:
            total = set()

            to_check = list()
            await self.logger.info(f"Total unchkecked ids exisitng: {len(self.id_set)}")
            while len(total) < n:
                for i in range(n - len(total)):
                    if self.id_set:
                        to_check.append(self.id_set[self.next_index % len(self.id_set)])
                        self.next_index += 1
                start = time.time()
                non_existing = await self.crud.filter_non_existing_users(session, to_check)
                await self.logger.info(f"Time taken to check {n} ids: {time.time() - start}")
                total.update(non_existing)
            return set(list(total)[:n])
