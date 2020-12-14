import typing as T
import asyncio
import inspect
from functools import lru_cache
from contextlib import asynccontextmanager
from . import spec
from .transport import Transport
from . import stub
from . import errors


class RPCClient:
    _request_id: int = 0

    _buffer_size: int = 4096

    _default_stub_cls: stub.Stub = stub.StubClient

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 6969,
        stub: T.Optional[T.Type] = None
    ):
        self._host = host
        self._port = port
        self._stub = stub or self._default_stub_cls()

    def __getattribute__(self, name: str):
        member = object.__getattribute__(self, name)

        if name.startswith('_'):
            return member

        if inspect.iscoroutinefunction(member) or callable(member):
            wrap = object.__getattribute__(self, '_convert_to_rpc_call')
            return wrap()(member)

        return member

    def _convert_to_rpc_call(self, timeout=None):
        @lru_cache
        def call_wrapper(func):
            async def decorator(**kwargs):
                nonlocal func

                request = await self._make_request(func, kwargs)
                in_data = self._stub.pack(request)

                async with self._create_transport() as transport:

                    await transport.send(in_data)
                    out_data = await transport.receive(self._buffer_size)

                    response = self._stub.unpack(out_data)

                    if response.error:
                        self._raise_error(response.error)

                    return response.result

            return decorator
        return call_wrapper

    async def _make_request(self, original_func, params) -> spec.RequestMessage:
        if inspect.iscoroutinefunction(original_func):
            map_params = await original_func(**params)
        else:
            map_params = original_func(**params)

        request = spec.RequestMessage(
            id = self._request_id,
            method = original_func.__name__,
        )
        self._request_id += 1

        if map_params is None:
            request.params = params
        else:
            request.params = map_params

        return request

    def _raise_error(self, error: spec.Error):
        e_class = errors.get_error_by_code(error.code)
        if e_class:
            raise e_class(error.message)

        raise Exception('Unexpected error')

    @asynccontextmanager
    async def _create_transport(self):
        reader, writer = await asyncio.open_connection(self._host, self._port)
        async with Transport(writer, reader) as transport:
            yield transport
