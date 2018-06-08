from aiohttp import ClientSession


class Target(object):
    def __init__(self, url, headers=None):
        self.url = url
        self.headers = headers or {}

    async def fetch(self, session):
        async with session.get(self.url, headers=self.headers) as resp:
            return await resp.read()


def keep_warm(targets, times=5, interval=300):
    loop = asyncio.get_event_loop()

    for i in range(times):
        future = asyncio.ensure_future(run(targets))
        loop.run_until_complete(future)


async def run(targets):
    async with ClientSession() as session:
        tasks = [
            asyncio.ensure_future(target.fetch(session))
            for target in targets
        ]

        await asyncio.gather(*tasks)
