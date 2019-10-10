import logging

from aiohttp import web


LOG = logging.getLogger(__name__)

LOG.info('Initializing Python AioHTTP birds API')

app = web.Application()