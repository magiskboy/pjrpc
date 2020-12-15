import typing as T
import asyncio
import inspect
from functools import lru_cache
from contextlib import asynccontextmanager
from . import spec
from . import transport as _transport
from . import stub
from . import errors
from . import types


class Client:
    _request_id: int = 0

    _fn_without_rpc_method = {'close', 'setup'}

    def __init__(
        self,
        host: str = '127.0.0.1',
        port: int = 6969,
        compress: bool = False,
    ):
        self._host = host
        self._port = port
        self._transport = None
        self._stub = stub.Stub(compress)
        self._loop = asyncio.get_event_loop()
        self._futures = {}

    def __getattribute__(self, name):
        member = object.__getattribute__(self, name)

        if name.startswith('_') or name in self._fn_without_rpc_method:
            return member

        if inspect.iscoroutinefunction(member) or callable(member):
            wrap = object.__getattribute__(self, '_convert_to_rpc_call')
            return wrap(member)

        return member

    async def _message_serving(self):
        async for data in self._transport.messages():
            response = self._stub.unpack(data)

            f = self._futures.pop(response.id)
            if f:
                if isinstance(response, spec.ErrorResponseMessage):
                    f.set_exception(
                        errors.get_error_by_code(response.code)(response.message))
                else:
                    f.set_result(response.result)

    @lru_cache
    def _convert_to_rpc_call(self, func):
        def decorator(**kwargs):
            nonlocal func

            request = self._make_request(func, kwargs)
            in_data = self._stub.pack(request)

            self._loop.create_task(self._transport.send_message(in_data))

            if isinstance(request, spec.CallingMessage):
                f = asyncio.Future()
                self._futures[request.id] = f
                return f

        return decorator

    def _make_request(self, local_fn, params):
        map_params = local_fn(**params)

        is_notify = params.pop('_notify', False)
        if is_notify:
            request = spec.Notification(method=local_fn.__name__)
        else:
            request = spec.CallingMessage(
                id = self._request_id,
                method = local_fn.__name__,
            )
            self._request_id += 1

        if map_params is None:
            request.params = params
        else:
            request.params = map_params

        return request

    async def __aenter__(self):
        reader, writer = await asyncio.open_connection(
            self._host, self._port)
        self._transport = _transport.ClientTransport(reader, writer)
        self._loop.create_task(self._message_serving())

    async def __aexit__(self, exc_type, exc, tb):
        await self._transport._send(self._transport.pack(b'CLOSE'))
        await self._transport.close()
