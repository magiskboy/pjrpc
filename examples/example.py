import asyncio
from pjrpc import RPCApplication, RPCClient


class PingRPCApplication(RPCApplication):
    async def ping(self, name: str):
        return {
            'message': 'hello',
            'name': name,
        }

class PingRPCClient(RPCClient):
    async def ping(self, name: str):
        pass


if __name__ == '__main__':
    import time
    async def run():
        client = PingRPCClient()
        g = []
        for _ in range(200):
            g.append(client.ping(name='Thanh'))
        r = await asyncio.gather(*g)


    a = time.time()
    asyncio.run(run())
    print(time.time() - a)
