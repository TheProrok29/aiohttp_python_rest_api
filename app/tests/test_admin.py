import aiohttp
from aiohttp import test_utils
from aiohttp import web

from app import app


class AdminAPITestCase(test_utils.AioHTTPTestCase):
    async def get_application(self) -> web.Application:
        return await app.init_app()

    @test_utils.unittest_run_loop
    async def test_requires_admin(self) -> None:
        resp = await self.client.request(
            "GET",
            '/admin/users',
            auth=aiohttp.BasicAuth('helion', 'helion'),
        )
        self.assertEqual(403, resp.status)

    @test_utils.unittest_run_loop
    async def test_works_for_admin(self) -> None:
        resp = await self.client.request(
            "GET",
            '/admin/users',
            auth=aiohttp.BasicAuth('tomasz', 'tomasz'),
        )
        self.assertEqual(200, resp.status)
