from redis import Redis

from Fetcher import Fetcher


class UserFinder:
    def __init__(self, fetcher: Fetcher, redis: Redis):
        self.fetcher = fetcher
        self.redis = redis

    async def dfs(self, default_steam_id):
        stack = self.redis.smembers("stack")
        if not stack:
            stack = [default_steam_id]
            self.redis.sadd("stack", *stack)
        else:
            stack = list(stack)

        visited = self.redis.smembers("visited")
        if not visited:
            visited = set()
        else:
            visited = set(visited)

        while stack:
            current_steam_id = int(stack.pop())
            if current_steam_id not in visited:
                visited.add(current_steam_id)
                self.redis.sadd("visited", current_steam_id)
                friends = await self.fetcher.fetch_friends(current_steam_id)
                if friends.is_failure():
                    continue
                for friend in friends.data:
                    if friend not in visited:
                        stack.append(friend)
                        # Update stack in Redis
                        self.redis.sadd("stack", friend)

        # Update visited in Redis after traversal

        return visited
