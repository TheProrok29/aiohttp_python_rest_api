import logging
import typing as tp

from aiohttp import web

from app.api import user

LOG = logging.getLogger(__name__)

USERS: tp.List[user.User] = [
    user.User(name='tomasz', password='tomasz', role=user.UserRole.ADMIN),
    user.User(name='helion', password='helion', role=user.UserRole.USER),
]


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
        raise web.HTTPNotImplemented()

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing user')
        raise web.HTTPNotImplemented()
