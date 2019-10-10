import logging

from aiohttp import web

LOG = logging.getLogger(__name__)


async def index_handler(request: web.Request) -> web.Response:
    LOG.info('/ has been called, redirecting to /api')
    raise web.HTTPPermanentRedirect('/api')