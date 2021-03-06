import asyncpg.pool
from discord.ext import commands


class Context(commands.Context):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._db: asyncpg.pool.PoolAcquireContext = None

    @property
    def db(self):
        if self._db is None:
            self._db = self.bot.pool.acquire()
        return self._db
