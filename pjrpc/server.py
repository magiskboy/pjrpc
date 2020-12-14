import typing as T
import asyncio
from asyncio.streams import StreamReader, StreamWriter
from . import transport
from . import application
from . import errors
from . import stub
from . import spec


class RPCServer:
    """This includes the stub and the runtime for the rpc server"""

    default_host: str = '127.0.0.1'

    default_port: int = 6969

    default_app_cls: T.Type = application.RPCApplication

    default_buffer_size: int = 4096

    default_stub_cls: T.Type = stub.StubServer

    def __init__(
        self,
        host: T.Optional[str] = 'localhost',
        port: T.Optional[int] = 6969,
        buffer_size: T.Optional[int] = None,
        app_cls: T.Optional[T.Type] = None,
        stub: T.Optional[T.Type] = None,
    ):

        self._host = host or self.default_host
        self._port = port or self.default_port
        self._buffer_size = buffer_size or self.default_buffer_size
        self._app_cls = app_cls or self.default_app_cls

        self._stub: stub.Stub = None
        if stub:
            self._stub = stub
        else:
            self._stub = self.default_stub_cls()

    async def full_dispatch_request(self, reader: StreamReader, writer: StreamWriter):
        trans = transport.Transport(writer, reader)

        try:
            in_data = await trans.receive(self._buffer_size)
            request = self._stub.unpack(in_data)

            app = self._app_cls()
            response = await app(request)

            out_data = self._stub.pack(response)
            await trans.send(out_data)

        except errors.PJRPCException as error:

            err_resp = spec.ResponseMessage(
                error=spec.Error(
                    code=error.code,
                    message=error.message,
                )
            )

            try:
                err_resp.id = request.id
            except UnboundLocalError:
                pass

            await trans.send(self._stub.pack(err_resp))

        finally:
            await trans.close()

    async def start(self):

        server = await asyncio.start_server(self.full_dispatch_request, self._host, self._port)

        async with server:
            await server.serve_forever()
