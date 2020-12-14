from asyncio.streams import StreamReader, StreamWriter


class Transport:
    def __init__(self, writer: StreamWriter, reader: StreamReader):
        self._writer = writer
        self._reader = reader

    async def send(self, data: bytes):
        self._writer.write(data)
        await self._writer.drain()

    async def receive(self, n: int = -1) -> bytes:
        return await self._reader.read(n)

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.close()
