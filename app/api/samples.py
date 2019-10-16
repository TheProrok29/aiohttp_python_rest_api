import logging
from pathlib import Path
import typing as tp

from aiohttp import web

from app.model import bird_sample

LOG = logging.getLogger(__name__)

BIRD_SAMPLES: tp.List[bird_sample.BirdSample] = []
for download_count, f in enumerate((Path.home() / 'Pobrane' / 'birds_sample').glob('*.mp3')):
    if f.exists():
        BIRD_SAMPLES.append(
            bird_sample.BirdSample(
                name=f.name.replace('.mp3', ''),
                download_count=download_count,
                path=f.absolute(),
            ),
        )


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
    return web.json_response(data=[bs.dict(exclude={'path'}) for bs in BIRD_SAMPLES])