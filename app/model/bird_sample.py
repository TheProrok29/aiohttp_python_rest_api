import typing as tp
from pathlib import Path

from asyncpg import pool
import pydantic as pd


class BirdSample(pd.BaseModel):
    name: str
    download_count: int
    path: pd.FilePath


async def fetch_one(
        db_pool: pool.Pool,
        name: str,
) -> tp.Optional[BirdSample]:
    maybe_db_row = await db_pool.fetchrow(
        'select name, download_count, path from public.bird_sample where name = $1',
        name,
    )
    return BirdSample(**maybe_db_row) if maybe_db_row is not None else None


async def save(
        db_pool: pool.Pool,
        name: str,
        path: Path,
) -> BirdSample:
    await db_pool.execute(
        'insert into public.bird_sample (name, path) values ($1, $2)',
        name,
        str(path.absolute()),
    )
    return BirdSample(
        name=name,
        download_count=0,
        path=path,
    )