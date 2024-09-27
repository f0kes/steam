from datetime import datetime

import aiohttp
import asyncio

from AsyncLogger import GenericLogger
from Ledger import ApiKeyLedger
from InputModel import GameHoursData, UserHoursData
from Result import Result


class Fetcher:
    def __init__(self, ledger: ApiKeyLedger, requests_per_second: int, logger: GenericLogger):
        self.ledger = ledger
        self.semaphore = asyncio.Semaphore(requests_per_second)
        self.session = aiohttp.ClientSession(connector=aiohttp.TCPConnector(limit=200))
        self.logger = logger

    async def fetch_play_time(self, steam_id: int) -> Result[UserHoursData]:
        async with self.semaphore:
            api_key = await self.ledger.next()
            if api_key.is_failure():
                return Result.failure("All keys exhausted")
            api_key = api_key.data
            # api_url = f"https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={api_key}&steamid={steam_id}&format=json"
            api_url = f"https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/?key={api_key}&steamid={steam_id}&format=json"
            async with self.session.get(api_url) as response:
                if response.status == 429:
                    await self.logger.warning(f"Met 429 for {api_key}")
                    self.ledger.set_to_zero(api_key)
                    return Result.failure("Rate limit reached")
                hours_data = await response.json()
                hours_data = hours_data.get("response", {}).get("games", [])
                parsed_hours_data = [GameHoursData(game_id=game["appid"],
                                                   playtime_forever=game["playtime_forever"],
                                                   playtime_two_weeks=game.get("playtime_2weeks", 0),
                                                   game_name=game.get("name", ""))
                                     for game in hours_data]
                return Result.success(UserHoursData(steam_id=steam_id, game_hours=parsed_hours_data))

    async def fetch_friends(self, steam_id: int) -> Result[list[int]]:
        async with self.semaphore:
            api_key = await self.ledger.next()
            if api_key.is_failure():
                return Result.failure("All keys exhausted")
            api_key = api_key.data
            api_url = f"https://api.steampowered.com/ISteamUser/GetFriendList/v1/?key={api_key}&steamid={steam_id}"
            async with self.session.get(api_url) as response:
                if response.status == 429:
                    await self.logger.warning(f"Met 429 for for {api_key}")
                    self.ledger.set_to_zero(api_key)
                    return Result.failure("Rate limit reached")
                try:
                    json_response = await response.json()
                except Exception as e:
                    await self.logger.error(f"Error fetching friends, {e}")
                    return Result.failure(f"Error fetching friends, {e}")
                friend_data = json_response.get("friendslist", {}).get("friends", [])
                if len(friend_data) == 0:
                    await self.logger.warning(f"No friends for {steam_id}")
                    return Result.failure(f"No friends for {steam_id}")
                # print(f"Friends for {steam_id}, current time: {datetime.now()}")
                await self.logger.info(f"Friends for {steam_id}, current time: {datetime.now()}")
                return Result.success([friend["steamid"] for friend in friend_data])
