import itertools
import logging
import typing as tp

import pydantic as pd

from aiohttp import web

from app.model import user

LOG = logging.getLogger(__name__)

USERS: tp.List[user.User] = [
    user.User(name='tomasz', password='tomasz', role=user.UserRole.ADMIN),
    user.User(name='helion', password='helion', role=user.UserRole.USER),
]


class Users(web.View):
    async def post(self) -> web.Response:
        LOG.info('Creating new user')
        global USERS

        try:
            new_user = user.User.parse_obj(await self.request.json())
            if next(filter(lambda u: u.name == new_user.name, USERS), None):
                LOG.error(f'Attempted to duplicate user {new_user.name}')
                raise web.HTTPConflict(
                    text=f'User {new_user.name} already exists')
        except pd.ValidationError:
            LOG.exception('Invalid new user request body')
            raise web.HTTPBadRequest(text='Invalid new user')

        USERS.append(new_user)
        return web.json_response(status=201, data=new_user.dict())

    async def get(self) -> web.Response:
        LOG.info('Getting a list of all users')
        return web.json_response(data=[u.dict() for u in USERS])


class User(web.View):
    async def get(self) -> web.Response:
        LOG.info('Getting a single user')
        try:
            username = self.request.match_info['username']
            found_user = next(filter(lambda u: u.name == username, USERS))
            return web.json_response(data=found_user.dict())
        except StopIteration:
            LOG.exception(f'Failed to find user {username}')
            raise web.HTTPNotFound(text=f'User {username} does not exist')

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing user')
        global USERS
        username = self.request.match_info['username']
        USERS = list(itertools.filterfalse(lambda u: u.name == username,
                                           USERS))
        return web.Response(status=204)
         