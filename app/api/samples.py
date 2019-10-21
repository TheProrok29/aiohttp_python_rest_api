import asyncio
import itertools
import logging
from pathlib import Path
import typing as tp

from aiohttp import web

from app.model import bird_sample

LOG = logging.getLogger(__name__)

BIRD_SAMPLES: tp.List[bird_sample.BirdSample] = []
CHUNK_SIZE = 4096

SERVER_DOWNLOAD_DIR = Path.cwd() / 'data'
SERVER_DOWNLOAD_DIR.mkdir(exist_ok=True)


def parse_param_as_bool(arg: tp.Optional[str] = None) -> tp.Optional[bool]:
    if arg is None:
        return None
    elif arg.lower() == 'true':
        return True
    elif arg.lower() == 'false':
        return False
    else:
        raise web.HTTPBadRequest(text=f'{arg} is neither "true" nor "false"')


# aiohttp.web.View
class BirdSamples(web.View):
    async def put(self) -> web.Response:
        LOG.info('Uploading a new sample')
        sample_name = self.request.match_info['sample_name']
        sample_filename = f'{sample_name}.mp3'

        loop = asyncio.get_running_loop()
        # run_in_executor

        sample_file = SERVER_DOWNLOAD_DIR / sample_filename
        await loop.run_in_executor(
            None,
            sample_file.touch,
            0o666,
            True,
        )

        sample_content = self.request.content

        with (await loop.run_in_executor(None, sample_file.open,
                                         'wb')) as handler:
            async for chunk in sample_content.iter_chunked(CHUNK_SIZE):
                await loop.run_in_executor(None, handler.write, chunk)

        global BIRD_SAMPLES
        BIRD_SAMPLES.append(
            bird_sample.BirdSample(
                name=sample_name,
                download_count=0,
                path=sample_file.absolute(),
            ))

        return web.Response(status=201)

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing sample')
        global BIRD_SAMPLES

        sample_name = self.request.match_info['sample_name']
        BIRD_SAMPLES = list(
            itertools.filterfalse(lambda bs: bs.name == sample_name,
                                  BIRD_SAMPLES))

        return web.Response(status=204)

    async def get(self) -> web.Response:
        LOG.info('Getting an existing sample')
        raise web.HTTPNotImplemented()


async def list_all(request: web.Request) -> web.Response:
    # sorted=True|False
    # noDownloads=True|False
    LOG.info('Getting a list of all bird samples')

    sort_by_downloads = parse_param_as_bool(request.query.get('sorted', None))
    filter_no_downloads = parse_param_as_bool(
        request.query.get('noDownloads', None))

    filtered_samples = filter(
        lambda bs: bs.download_count == 0
        if filter_no_downloads else bs.download_count > 0,
        BIRD_SAMPLES,
    ) if filter_no_downloads is not None else BIRD_SAMPLES

    sorted_and_filtered_data = sorted(
        filtered_samples,
        key=lambda bs: bs.download_count,
    ) if sort_by_downloads is True else filtered_samples

    return web.json_response(
        data=[bs.dict(exclude={'path'}) for bs in sorted_and_filtered_data])
