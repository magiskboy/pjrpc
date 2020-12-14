import unittest
from pjrpc import RPCApplication
from pjrpc.spec import RequestMessage
from pjrpc.errors import MethodNotFoundError


class ApplicationTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        class PingService(RPCApplication):
            async def async_ping(self):
                return {
                    'message': 'pong',
                }

            def sync_ping(self):
                return {
                    'message': 'pong'
                }

        self.app = PingService()

    async def test_async_handler(self):
        request = RequestMessage(id=1, method='async_ping')
        response = await self.app(request)
        self.assertEqual(response.result, {'message': 'pong'})

    async def test_sync_handler(self):
        request = RequestMessage(id=1, method='sync_ping')
        response = await self.app(request)
        self.assertEqual(response.result, {'message': 'pong'})

    async def test_not_exist_handler(self):
        try:
            request = RequestMessage(id=1, method='not_found_method')
            await self.app(request)
        except MethodNotFoundError:
            pass
