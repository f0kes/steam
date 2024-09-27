import datetime

from redis import Redis

from AsyncLogger import GenericLogger
from Result import Result


class ApiKeyLedger:
    def __init__(self, data_list: list[str],
                 redis_conn: Redis,
                 requests: int,
                 logger: GenericLogger,
                 delay: datetime.timedelta = datetime.timedelta(days=1),
                 ):
        self.data_list = data_list
        self.redis_conn = redis_conn
        self.requests = requests
        self.usable_keys = data_list
        self.next_index = 0
        self.delay = delay
        self.logger = logger
        self.requests_remaining = {key: requests for key in data_list}
        self.timeouts = {key: datetime.datetime.now() for key in data_list}

        self.load()

    def load(self):
        for key in self.data_list:
            self.requests_remaining[key] = int((self.redis_conn.get(f"requests_remaining_{key}") or self.requests))
            timeout: bytes = self.redis_conn.get(f"wait_list_{key}")
            timeout_string = timeout.decode('utf-8') if timeout else str(datetime.datetime.now())
            self.timeouts[key] = datetime.datetime.strptime(timeout_string, '%Y-%m-%d %H:%M:%S.%f')

    def save(self):
        for key in self.data_list:
            self.redis_conn.set(f"requests_remaining_{key}", self.requests_remaining[key])
            self.redis_conn.set(f"wait_list_{key}", str(self.timeouts[key]))

    def set_to_zero(self, api_key: str) -> None:
        self.logger.warning(f"Rate limit reached unexpectedly for {api_key}")
        self.requests_remaining[api_key] = 0

    def check_wait_list(self) -> None:
        for (key, time) in self.timeouts.items():
            if time < datetime.datetime.now():
                self.requests_remaining[key] = self.requests
                self.timeouts[key] = datetime.datetime.now() + self.delay

    async def next(self) -> Result[str]:
        self.check_wait_list()
        usable_keys = [key for key in self.data_list if self.requests_remaining[key] > 0]

        if len(usable_keys) != 0:
            true_index = self.next_index % len(usable_keys)
            self.next_index += 1
            self.requests_remaining[usable_keys[true_index]] -= 1
            return Result.success(usable_keys[true_index])
        else:
            await self.logger.warning("All keys are exhausted")
        self.save()
        return Result.failure("All keys are exhausted")
