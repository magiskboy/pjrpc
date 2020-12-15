import asyncio
from pjrpc import Service, Client


class PingService:
    async def ping(self, name: str):
        return NotImplemented


class PingServer(PingService, Service):
    async def ping(self, name: str):
        await asyncio.sleep(1)
        return f'Hello {name}'


class PingClient(PingService, Client):
    def ping(self, name: str, **kwargs):
        pass


if __name__ == '__main__':
    async def main():
        client = PingClient()
        async with client:
            ret = await asyncio.gather(
                client.ping(name='David'),
                client.ping(name='John'),
                client.ping(name='Steve'),
            )

            print(ret)

    asyncio.run(main())
