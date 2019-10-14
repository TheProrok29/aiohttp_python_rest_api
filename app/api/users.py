import logging

from aiohttp import web

LOG = logging.getLogger(__name__)


class Users(web.View):
    async def post(self) -> web.Response:
        LOG.info('Creating new user')
        raise web.HTTPNotImplemented()

    async def get(self) -> web.Response:
        LOG.info('Getting a list of all users')
        raise web.HTTPNotImplemented()


class User(web.View):
    async def get(self) -> web.Response:
        LOG.info('Getting a single user')
        raise web.HTTPNotImplemented( )

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing user')
        raise web.HTTPNotImplemented()