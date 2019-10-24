import asyncio
import itertools
import logging
from pathlib import Path
import typing as tp

import aiohttp
from aiohttp import web
from aiohttp import hdrs

from app.model import bird_sample

LOG = logging.getLogger(__name__)

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

        content_type = self.request.content_type
        LOG.debug(f'Processing request with content type = {content_type}')

        sample_name = self.request.match_info['sample_name']
        if await bird_sample.fetch_one(db_pool=self.request.app['db_pool'],
                                       name=sample_name) is not None:
            LOG.error(
                f'Sample {sample_name} has been already uploaded, skipping...')
            raise web.HTTPConflict(text=f'Sample {sample_name} already exists')
        sample_filename = f'{sample_name}.mp3'

        is_full_read_enabled = parse_param_as_bool(
            self.request.headers.get('X-Read-Full', None))

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

        if content_type == 'audio/mpeg':
            if is_full_read_enabled:
                with (await loop.run_in_executor(None, sample_file.open,
                                                 'wb')) as handler:
                    await loop.run_in_executor(
                        None,
                        handler.write,
                        await self.request.read(),
                    )
            else:
                with (await loop.run_in_executor(None, sample_file.open,
                                                 'wb')) as handler:
                    async for chunk in sample_content.iter_chunked(CHUNK_SIZE):
                        await loop.run_in_executor(None, handler.write, chunk)
        elif content_type == 'multipart/form-data':
            if is_full_read_enabled:
                data = await self.request.post()
                sample = data[
                    'sample']  # type: t.Union[str, bytes, web.FileField]
                if isinstance(sample, web.FileField):
                    if sample.headers[hdrs.CONTENT_TYPE] != 'audio/mpeg':
                        raise web.HTTPUnsupportedMediaType()
                    else:
                        with (await
                              loop.run_in_executor(None, sample_file.open,
                                                   'wb')) as handler:
                            await loop.run_in_executor(
                                None,
                                handler.write,
                                sample.file.read(),
                            )
                else:
                    raise web.HTTPBadRequest(
                        text=f'Sample {sample_name} is not a file')
            else:
                # aiohttp.MultipartReader
                part: tp.Optional[tp.Union[aiohttp.MultipartReader, aiohttp.
                                           BodyPartReader]] = None
                reader = await self.request.multipart()
                async for part in reader:
                    if isinstance(part, aiohttp.BodyPartReader):
                        part_content_type = part.headers[hdrs.CONTENT_TYPE]
                        part_name = part.name

                        if part_content_type == 'audio/mpeg' and part_name == 'sample':
                            with (await
                                  loop.run_in_executor(None, sample_file.open,
                                                       'wb')) as handler:
                                chunk = await part.read_chunk(CHUNK_SIZE)
                                while chunk:
                                    await loop.run_in_executor(
                                        None,
                                        handler.write,
                                        chunk,
                                    )
                                    chunk = await part.read_chunk(CHUNK_SIZE)
                        else:
                            raise web.HTTPBadRequest(
                                text='Failed to find mp3 sample')
                    else:
                        raise web.HTTPBadRequest(
                            text='Nasted Multiparts are not supported')
        else:
            raise web.HTTPUnsupportedMediaType()

        await bird_sample.save(
            db_pool=self.request.app['db_pool'],
            name=sample_name,
            path=sample_file,
        )

        return web.Response(status=201)

    async def delete(self) -> web.Response:
        LOG.info('Deleting an existing sample')

        sample_name = self.request.match_info['sample_name']
        sample = await bird_sample.fetch_one(
            db_pool=self.request.app['db_pool'],
            name=sample_name,
        )
        if sample:
            await bird_sample.remove(
                db_pool=self.request.app['db_pool'],
                name=sample_name,
            )
            sample.path.unlink()

        return web.Response(status=204)

    async def get(self) -> web.FileResponse:
        LOG.info('Getting an existing sample')
        sample_name = self.request.match_info['sample_name']

        found_sample = await bird_sample.fetch_one(
            db_pool=self.request.app['db_pool'],
            name=sample_name,
        )
        if not found_sample:
            raise web.HTTPNotFound(text=f'Sample {sample_name} does not exist')
        else:
            await bird_sample.increment_download_count(
                db_pool=self.request.app['db_pool'],
                name=found_sample.name,
                current_download_count=found_sample.download_count,
            )

            resp = web.FileResponse(
                path=found_sample.path,
                chunk_size=CHUNK_SIZE,
                headers={
                    hdrs.CONTENT_DISPOSITION: f'filename="{sample_name}.mp3"',
                },
            )
            resp.enable_compression()
            return resp


async def upload_many(request: web.Request) -> web.Response:
    LOG.info('Uploading many samples from multipart request')
    content_type = request.content_type
    if content_type == 'multipart/form-data':
        reader = await request.multipart()
        new_samples: tp.List[bird_sample.BirdSample] = []

        async for part in reader:
            if isinstance(part, aiohttp.BodyPartReader):
                part_content_type = part.headers[hdrs.CONTENT_TYPE]
                part_name = part.name

                if part_content_type == 'audio/mpeg' and part_name.startswith(
                        'sample_'):
                    sample_name = part_name.replace('sample_', '')

                    if await bird_sample.fetch_one(
                            db_pool=request.app['db_pool'], name=sample_name):
                        LOG.debug('Sample {sample_name} already uploaded')
                        continue

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

                    with (await loop.run_in_executor(None, sample_file.open,
                                                     'wb')) as handler:
                        chunk = await part.read_chunk(CHUNK_SIZE)
                        while chunk:
                            await loop.run_in_executor(
                                None,
                                handler.write,
                                chunk,
                            )
                            chunk = await part.read_chunk(CHUNK_SIZE)

                    new_samples.append(
                        await bird_sample.save(
                            db_pool=request.app['db_pool'],
                            name=sample_name,
                            path=sample_file.absolute(),
                        ), )
            else:
                raise web.HTTPBadRequest(
                    text='Nasted Multiparts are not supported')

        return web.json_response(
            status=201 if new_samples else 200,
            data=[nbd.dict(exclude={'path'}) for nbd in new_samples])
    else:
        raise web.HTTPUnsupportedMediaType()


async def list_all(request: web.Request) -> web.Response:
    # sorted=True|False
    # noDownloads=True|False
    LOG.info('Getting a list of all bird samples')

    all_samples = await bird_sample.fetch_all(db_pool=request.app['db_pool'])

    sort_by_downloads = parse_param_as_bool(request.query.get('sorted', None))
    filter_no_downloads = parse_param_as_bool(
        request.query.get('noDownloads', None))

    filtered_samples = filter(
        lambda bs: bs.download_count == 0
        if filter_no_downloads else bs.download_count > 0,
        all_samples,
    ) if filter_no_downloads is not None else all_samples

    sorted_and_filtered_data = sorted(
        filtered_samples,
        key=lambda bs: bs.download_count,
    ) if sort_by_downloads is True else filtered_samples

    return web.json_response(
        data=[bs.dict(exclude={'path'}) for bs in sorted_and_filtered_data])
