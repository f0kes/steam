from id_providers.SteamIdProvider import SteamIdProvider


class CompositeSteamIDProvider(SteamIdProvider):

    def __init__(self, providers: dict[SteamIdProvider, float]):
        self.providers = providers
        self.total_weight = sum(providers.values())
        self.providers = {k: v / self.total_weight for k, v in providers.items()}

    async def get_ids(self, n=100) -> set[int]:
        provider_resuests = {k: int(v * n) for k, v in self.providers.items()}
        total = []
        for provider, requests in provider_resuests.items():
            total.extend(await provider.get_ids(requests))
        return set(total[:n])
