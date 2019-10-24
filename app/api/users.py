import logging

import pydantic as pd

from aiohttp import web
import asyncpg
from app.model import user

LOG = logging.getLogger(__name__)


class Users(web.View):
    async def post(self) -> web.Response:
        LOG.info('Creating new user')
        try:
            new_user = user.User.parse_obj(await self.request.json())
            await user.save(
                db_pool=self.request.config_dict['db_pool'],
                name=new_user.name,
                password=new_user.password,
                role=new_user.role,
            )
        except pd.ValidationError:
            LOG.exception('Invalid new user request body')
            raise web.HTTPBadRequest(text='Invalid new user')
        except asyncpg.exceptions.UniqueViolationError:
            LOG.exception(f'Attempted to duplicate user {new_user.name}')
            raise web.HTTPConflict(text=f'User {new_user.name} already exists')

        return web.json_response(status=201, data=new_user.dict())

    async def get(self) -> web.Response:
        LOG.info('Getting a list of all users')
        users = await user.fetch_all(db_pool=self.request.config_dict['db_pool'])
        return web.json_response(data=[u.dict() for u in users])


class User(web.View):
    async def get(self) -> web.Response:
        LOG.info('Getting a single user')
        username = self.request.match_info['username']
        found_user = await user.fetch_one(
            db_pool=self.request.config_dict['db_pool'],
            name=username,
        )
        if found_user:
            return web.json_response(data=found_user.dict())
        else:
            LOG.exception(f'Failed to find user {username}')
            raise web.HTTPNotFound(text=f'User {username} does not exist')

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing user')
        username = self.request.match_info['username']
        if username == self.request['user'].name:
            raise web.HTTPBadRequest(
                text='You should not try to remove yourself')
        await user.remove(db_pool=self.request.config_dict['db_pool'], name=username)
        return web.Response(status=204)
