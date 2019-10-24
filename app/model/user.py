import enum
import typing as tp

import pydantic as pd
from asyncpg import pool


class UserRole(str, enum.Enum):
    USER = 'user'
    ADMIN = 'admin'


class User(pd.BaseModel):
    name: str
    password: str
    role: UserRole


async def fetch_all(db_pool: pool.Pool) -> tp.List[User]:
    db_rows = await db_pool.fetch(
        'select name, password, role from public.user', )
    return [User(**row) for row in db_rows]


async def fetch_one(
        db_pool: pool.Pool,
        name: str,
) -> tp.Optional[User]:
    maybe_db_row = await db_pool.fetchrow(
        'select name, password, role from public.user where name = $1',
        name,
    )
    return User(**maybe_db_row) if maybe_db_row is not None else None
