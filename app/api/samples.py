import logging
from pathlib import Path
import typing as tp

from aiohttp import web

from app.model import bird_sample

LOG = logging.getLogger(__name__)

BIRD_SAMPLES: tp.List[bird_sample.BirdSample] = []
for download_count, f in enumerate(
    (Path.home() / 'Pobrane' / 'birds_sample').glob('*.mp3')):
    if f.exists():
        BIRD_SAMPLES.append(
            bird_sample.BirdSample(
                name=f.name.replace('.mp3', ''),
                download_count=download_count,
                path=f.absolute(),
            ), )

LOG.debug(f'BIRD_SAMPLES has now {len(BIRD_SAMPLES)} samples')


def parse_param_as_bool(arg: tp.Optional[str] = None) -> tp.Optional[bool]:
    if arg is None:
        return None
    elif arg.lower() == 'true':
        return True
    elif arg.lower() == 'false':
        return False
    else:
        raise web.HTTPBadRequest(text=f'{arg} is neither "true" or "false"')


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
