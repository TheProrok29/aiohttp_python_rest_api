import logging
import typing as tp
from aiohttp import web

from app.model import bird_sample

LOG = logging.getLogger(__name__)

BIRD_SAMPLES: tp.List[bird_sample.BirdSample] = []


# aiohttp.web.View
class BirdSamples(web.View):
    async def put(self) -> web.Response:
        LOG.info('Uploading a new sample')
        raise web.HTTPNotImplemented()

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing sample')
        raise web.HTTPNotImplemented()

    async def get(self) -> web.Response:
        LOG.info('Getting an existing sample')
        raise web.HTTPNotImplemented()


async def list_all(request: web.Request) -> web.Response:
    LOG.info('Getting a list of all bird samples')
    raise web.HTTPNotImplemented()