import logging
import os

import typing as tp

from aiohttp import web
from asyncpg import pool

LOG = logging.getLogger(__name__)


def setup(app: web.Application) -> None:
    app.cleanup_ctx.append(db_setup)


async def db_setup(app: web.Application) -> tp.AsyncIterator[None]:
    LOG.info('Initializing database connection')
    app['db_pool'] = db_pool = await pool.create_pool(
        user=os.getenv('HELION_DB_USER', 'helion'),
        password=os.getenv('HELION_DB_PASSWORD', 'helion'),
        database=os.getenv('HELION_DB_NAME', 'helion'),
        host=os.getenv('HELION_DB_HOST', '127.0.0.1'),
        port=int(os.getenv('HELION_DB_PORT', 5432)),
    )

    yield

    LOG.info('Closing database connection')
    await db_pool.close()