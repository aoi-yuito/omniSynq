from __future__ import annotations

import asyncio
import functools
import typing as t

import aiofiles
import asyncpg
from apscheduler.triggers.cron import CronTrigger

from backend import Config


class Database:
    def __init__(self, app) -> None:
        self.app = app
        self.db = Config.PG_DB
        self.host = Config.PG_HOST
        self.user = Config.PG_USER
        self.password = Config.PG_PASS
        self.port = Config.PG_PORT
        self.schema = f"{self.app._static}/build.sql"
        self._calls = 0

        self.app.scheduler.add_job(self.commit, CronTrigger(second=0))

    async def connect(self) -> None:

        self.pool: asyncpg.Pool = await asyncpg.create_pool(
            user=self.user,
            host=self.host,
            port=self.port,
            database=self.db,
            password=self.password,
            loop=asyncio.get_running_loop(),
        )

        await self.executescript(self.schema)
        await self.commit()

    async def close(self) -> None:
        await self.commit()
        await self.pool.close()

    @staticmethod
    def with_connection(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]:

        @functools.wraps(func)
        async def wrapper(self: Database, *args: t.Any) -> t.Any:
            async with self.pool.acquire() as conn:
                self._calls += 1
                return await func(self, *args, conn=conn)

        return wrapper

    @with_connection
    async def commit(self, conn: asyncpg.Connection) -> None:
        async with conn.transaction() as tr:
            await self.execute("UPDATE app SET Value = CURRENT_TIMESTAMP WHERE Key = 'last commit'")

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

    @with_connection
    async def executescript(self, path: str, conn: asyncpg.Connection) -> None:
        async with aiofiles.open(path, "r", encoding="utf-8") as script:
            await conn.execute((await script.read()))