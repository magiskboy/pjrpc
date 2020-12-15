import unittest
from pjrpc import Service
from pjrpc.spec import CallingMessage
from pjrpc.errors import MethodNotFoundError


class ServiceTestCase(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        class PingService(Service):
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
        request = CallingMessage(id=1, method='async_ping')
        response = await self.app(request)
        self.assertEqual(response.result, {'message': 'pong'})

    async def test_sync_handler(self):
        request = CallingMessage(id=1, method='sync_ping')
        response = await self.app(request)
        self.assertEqual(response.result, {'message': 'pong'})

    async def test_not_exist_handler(self):
        try:
            request = CallingMessage(id=1, method='not_found_method')
            await self.app(request)
        except MethodNotFoundError:
            pass
