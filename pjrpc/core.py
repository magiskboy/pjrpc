import typing as T
import asyncio
import logging
import inspect
from functools import lru_cache
from . import types
from . import transport as _transport
from . import errors
from . import stub
from . import utils
from . import spec


logger = logging.getLogger('pjrpc.server')


class Service:
    """Receive request, routing, process and response to server"""

    def _method_predicate(self, meth):
        return inspect.iscoroutinefunction(meth) or callable(meth)

    @lru_cache(maxsize=1024)
    def _get_func(self, f_name: str):
        for name, func in inspect.getmembers(self, self._method_predicate):
            if name == f_name:
                return func

        raise errors.MethodNotFoundError()

    def _check_args(self, args: T.Dict[str, T.Type], func: T.Callable):
        #TODO: check default value
        annotations = func.__annotations__

        for k, v in args.items():
            if k in annotations:
                if type(v) is not annotations[k]:
                    raise errors.InvalidParamError()

    async def __call__(
        self,
        request: types.Request,
    ) -> T.Union[spec.ErrorResponseMessage, spec.SuccessResponseMessage]:

        target = self._get_func(request.method)
        params = request.params or {}

        self._check_args(params, target)

        if not inspect.iscoroutinefunction(target):
            target = utils.to_async()(target)

        ret = await target(**params)

        if not isinstance(request, spec.Notification):
            return utils.make_response_from_data(
                id=request.id,
                result=ret,
            )


class Server:

    def __init__(
        self,
        app_path: str,
        host: str = '127.0.0.1',
        port: int = 6969,
        compress: bool = False,
    ):

        self._app_cls = utils.load_app_from_string(app_path)
        self._host = host
        self._port = port
        self._stub = stub.Stub(compress)
        self._loop = asyncio.get_event_loop()
        self._futures = {}

    async def connection_handler(
        self,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ):
        transport = _transport.ServerTransport(reader, writer, interval=2, alive=5)

        async def dispatch_request(request):
            if isinstance(request, list):
                async def batch_request(requests):
                    app = self._app_cls()

                    tasks = []
                    for request in requests:
                        if isinstance(request, spec.Notification):
                            self._loop.create_task(app(request))
                        else:
                            f = self._loop.create_task(app(request))
                            tasks.append(f)

                    if len(tasks) == 0:
                        return None

                    responses = asyncio.wait(tasks)
                    return responses

                return await batch_request(request)

            return await self._app_cls()(request)

        def on_request_done(fut):
            err = fut.exception()
            if err:
                ret = utils.make_response_from_data(
                    error={'code': err.code, 'message': err.message})
            else:
                ret = fut.result()
            self._loop.create_task(transport.send_message(self._stub.pack(ret)))

        async for in_data in transport.messages():
            try:
                request = self._stub.unpack(in_data)

            except errors.ParseError as error:
                err_resp = utils.make_response_from_data(
                    error={'code': error.code, 'message': error.message})
                out_data = self._stub.pack(err_resp)
                self._loop.create_task(transport.send_message(out_data))

            f = self._loop.create_task(dispatch_request(request))
            f.add_done_callback(on_request_done)

    def protocol_factory(self):
        reader = asyncio.StreamReader(limit=1024, loop=self._loop)
        protocol = asyncio.StreamReaderProtocol(
            reader, self.connection_handler, loop=self._loop)
        return protocol

    async def start(self):
        server = await self._loop.create_server(self.protocol_factory, self._host, self._port)

        async with server:
            logger.info('Server is starting on port %d ...', self._port)
            await server.serve_forever()
