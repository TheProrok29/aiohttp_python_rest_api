import typing as tp

import aiohttp

from aiohttp import web


def setup(app: web.Application) -> None:
    # web.middleware => no for persistent session
    # signals
    # -> on_response_prepare(request)
    # -> on_startup i on_cleanup
    # -> cleanup_ctx

    app.cleanup_ctx.append(persistent_session)


async def persistent_session(app: web.Application) -> tp.AsyncIterator[None]:
    app['persistent_session'] = session_1 = aiohttp.ClientSession()
    app['persistent_aws_session'] = session_2 = aiohttp.ClientSession(
        headers={'X-FAKE-AUTH': 'MY_TOKEN'})
    app['persistent_company_service_session'] = session_3 = aiohttp.ClientSession(
        auth=aiohttp.BasicAuth('tomasz', 'tomasz'))
    app['persistent_internal_session'] = session_4 = aiohttp.ClientSession()

    yield

    for session in [session_1, session_2, session_3, session_4]:
        await session.close()
