from unittest import IsolatedAsyncioTestCase
from pjrpc import utils
import asyncio


class UtilsTestCase(IsolatedAsyncioTestCase):
    async def test_to_async(self):
        def sync_fn():
            return 'foo'

        async_fn = utils.to_async()(sync_fn)
        ret = await async_fn()

        self.assertTrue(asyncio.iscoroutinefunction(async_fn))
        self.assertEqual(ret, 'foo')


    def test_load_app_from_string(self):
        from unittest import TestCase

        app_path = 'unittest:TestCase'
        app = utils.load_app_from_string(app_path)
        self.assertEqual(app, TestCase)
