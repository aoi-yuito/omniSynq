from __future__ import annotations

import asyncio
import functools
import typing as t

import asyncpg


class PostgreSQL:
    def __init__(self, db, host, user, password, port) -> None:
        self.db = db
        self.host = host
        self.user = user
        self.password = password
        self.port = port

    async def connect(self) -> None:

        self.pool: asyncpg.Pool = await asyncpg.create_pool(
            user=self.user,
            host=self.host,
            port=self.port,
            database=self.db,
            password=self.password,
            loop=asyncio.get_running_loop(),
        )

    async def close(self) -> None:
        await self.pool.close()

    @staticmethod
    def with_connection(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:

        @functools.wraps(func)
        async def wrapper(self: Database, *args: t.Any) -> t.Any:
            async with self.pool.acquire() as conn:
                return await func(self, *args, conn=conn)

        return wrapper

    @with_connection
    async def field(self, sql: str, *values: tuple[t.Any], conn: asyncpg.Connection) -> t.Any | None:
        query = await conn.prepare(sql)
        return await query.fetchval(*values)

    @with_connection
    async def record(self, sql: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Any]]:
        query = await conn.prepare(sql)
        if data := await query.fetchrow(*values):
            return [r for r in data]

        return None

    @with_connection
    async def dictionary(self, sql: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Any]]:
        query = await conn.prepare(sql)
        if data := await query.fetchrow(*values):
            return dict(data)

        return None

    @with_connection
    async def dictionaries(
        self, sql: str, *values: t.Any, conn: asyncpg.Connection
    ) -> t.Optional[t.List[t.Iterable[t.Any]]]:
        query = await conn.prepare(sql)
        if data := await query.fetch(*values):
            return [*map(lambda r: dict(r), data)]

        return None

    @with_connection
    async def records(
        self, sql: str, *values: t.Any, conn: asyncpg.Connection
    ) -> t.Optional[t.List[t.Iterable[t.Any]]]:
        query = await conn.prepare(sql)
        if data := await query.fetch(*values):
            return [*map(lambda r: tuple(r.values()), data)]

        return None

    @with_connection
    async def column(self, sql: str, *values: t.Any, conn: asyncpg.Connection) -> t.List[t.Any]:
        query = await conn.prepare(sql)
        return [r[0] for r in await query.fetch(*values)]

    @with_connection
    async def execute(self, sql: str, *values: t.Any, conn: asyncpg.Connection) -> None:
        query = await conn.prepare(sql)
        await query.fetch(*values)

    @with_connection
    async def executemany(self, sql: str, values: t.List[t.Iterable[t.Any]], conn: asyncpg.Connection) -> None:
        query = await conn.prepare(sql)
        await query.executemany(values)