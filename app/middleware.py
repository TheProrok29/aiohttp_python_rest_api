import base64
import typing as tp

from aiohttp import hdrs
from aiohttp import web

AIOHTTP_HANDLER = tp.Callable[[web.Request], tp.Awaitable[web.
                                                          StreamResponse], ]

AIOHTTP_MIDDLEWARE = tp.Callable[[web.Request, AIOHTTP_HANDLER], tp.
                                 Coroutine[tp.Any, tp.Any, web.
                                           StreamResponse], ]


@web.middleware
async def authorize(
        request: web.Request,
        handler: AIOHTTP_HANDLER,
) -> web.StreamResponse:
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

        from app.api import users

        user = next(filter(lambda u: u.name == username, users.USERS), None)

        if user and user.password == password:
            request['user'] = user
            return await handler(request)
        else:
            raise web.HTTPForbidden()
