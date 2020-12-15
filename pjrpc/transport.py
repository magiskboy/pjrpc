import typing as T
import asyncio
import logging


SEP_C = b'\n\n'
HEADER_SIZE = 16

logger = logging.getLogger('pjrpc.server')


class Transport:
    __slots__ = ('_writer', '_reader', '_loop')

    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self._reader = reader
        self._writer = writer
        self._loop = asyncio.get_event_loop()

    def pack(
        self,
        header: bytes,
        data: T.Optional[bytes] = None,
    ) -> bytes:
        if data is None:
            return header.ljust(HEADER_SIZE, b' ') + SEP_C
        return header.ljust(HEADER_SIZE, b' ') + data + SEP_C

    def unpack(self, pack: bytes) -> tuple:
        header = pack[:HEADER_SIZE].strip()
        body = pack[HEADER_SIZE:-2]
        return header, body

    async def send_message(self, data: bytes):
        await self._send(self.pack(b'MESSAGE', data))

    async def messages(self):
        sleep_time = 0.01       #TODO: algorithm for calculating
        is_closing = self._writer.is_closing

        while not is_closing():
            try:
                data = await self._reader.readuntil(SEP_C)
                self._on_received_message(data)

                header, body = self.unpack(data)
                if header == b'MESSAGE':
                    yield body

            except asyncio.IncompleteReadError:
                pass

            except RuntimeError:
                break

            await asyncio.sleep(sleep_time)

    async def close(self):
        self._writer.close()
        await self._writer.wait_closed()

    async def _send(self, data):
        self._writer.write(data)
        await self._writer.drain()

    def _on_received_message(self, data):
        return NotImplementedError


class ServerTransport(Transport):
    __slots__ = ('_last_time_alive',)

    def __init__(self, *args, interval=5, alive=5, **kwargs):
        super().__init__(*args, **kwargs)
        self._last_time_alive = self._loop.time()
        self._loop.create_task(self._connection_checking(interval, alive))

    def _on_received_message(self, data):
        self._last_time_alive = self._loop.time()

    async def _connection_checking(self, interval=5, alive=5):
        if self._loop.time() - self._last_time_alive > alive:
            await self.close()

        else:
            await asyncio.sleep(interval)
            self._loop.create_task(self._connection_checking(interval, alive))


class ClientTransport(Transport):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._loop.create_task(self._ping_signal())

    async def _ping_signal(self, interval=5):
        await self._send(self.pack(b'PING'))
        await asyncio.sleep(interval)

        self._loop.create_task(self._ping_signal(interval))
