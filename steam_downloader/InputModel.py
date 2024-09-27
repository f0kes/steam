from typing import TypedDict


class GameHoursData:
    game_id: int
    game_name: str
    playtime_forever: int
    playtime_two_weeks: int

    def __init__(self, game_id: int, playtime_forever: int, playtime_two_weeks: int, game_name: str = ""):
        self.game_id = game_id
        self.playtime_forever = playtime_forever
        self.playtime_two_weeks = playtime_two_weeks
        self.game_name = game_name

    def __str__(self):
        return (f"Game ID: {self.game_id}, Playtime: {self.playtime_forever},"
                f" Playtime in last two weeks: {self.playtime_two_weeks}")


class UserHoursData:
    steam_id: int
    game_hours: list[GameHoursData]

    def __init__(self, steam_id: int, game_hours: list[GameHoursData]):
        self.steam_id = steam_id
        self.game_hours = game_hours
