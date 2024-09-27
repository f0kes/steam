from abc import ABC, abstractmethod
from typing import AsyncIterator


class SteamIdProvider(ABC):
    @abstractmethod
    async def get_ids(self, n=100) -> set[int]:
        pass


