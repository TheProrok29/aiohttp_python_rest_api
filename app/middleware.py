import base64
import logging
import typing as tp
import asyncio
from aiohttp import hdrs
from aiohttp import web
from app.model import user as user_model

AIOHTTP_HANDLER = tp.Callable[[web.Request], tp.Awaitable[web.
                                                          StreamResponse], ]

AIOHTTP_MIDDLEWARE = tp.Callable[[web.Request, AIOHTTP_HANDLER], tp.
                                 Coroutine[tp.Any, tp.Any, web.
                                           StreamResponse], ]
LOG = logging.getLogger(__name__)


@web.middleware
async def authorize(
        request: web.Request,
        handler: AIOHTTP_HANDLER,
) -> web.StreamResponse:
    LOG.debug('before_request_handler')
    authorization = request.headers.get(hdrs.AUTHORIZATION, '')
    if not authorization:
        raise web.HTTPUnauthorized(headers={
            hdrs.WWW_AUTHENTICATE:
            'Basic realm="Access to Bird Samples"'
        }, )
    else:
        # AUTHORIZATION: {authorization_type} \s {credentials}
        # credentials: username:password
        _, credentials = authorization.split(' ')
        username, password = base64.b64decode(
            credentials.encode('utf-8')).decode('utf-8').split(':')

        user = await user_model.fetch_one(
            db_pool=request.app['db_pool'],
            name=username,
        )

        if user and user.password == password:
            request['user'] = user
            response = await handler(request)
            LOG.debug('after_request_handler')
            return response
        else:
            raise web.HTTPForbidden()


@web.middleware
async def sign_off(request: web.Request,
                   handler: AIOHTTP_HANDLER) -> web.StreamResponse:
    try:
        LOG.debug('before_request_handler')
        response = await handler(request)
        LOG.debug('after_request_handler')
    except web.HTTPException as ex:
        LOG.debug('after_request_handler_exception')
        ex.headers['X-BIRD-SAMPLES'] = 'aiohttp - performant HTTP server'
        raise
    else:
        response.headers['X-BIRD-SAMPLES'] = 'aiohttp - performant HTTP server'
        return response


@web.middleware
async def shield_mutating_request(
        request: web.Request,
        handler: AIOHTTP_HANDLER,
) -> web.StreamResponse:
    if request.method in ('POST', 'PUT', 'PATCH', 'DELETE'):
        return await asyncio.shield(handler(request))
    else:
        return await handler(request)

@web.middleware
async def requires_admin_access(
    request: web.Request,
    handler: AIOHTTP_HANDLER,
) -> web.StreamResponse:
    current_user = request.get('user', None)
    if not current_user or current_user.role != user_model.UserRole.ADMIN:
        raise web.HTTPForbidden()
    else:
        return await handler(request)