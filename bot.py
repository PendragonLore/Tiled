# -*- coding: utf-8 -*-

import sys
import asyncio
import logging
import pathlib

from discord.ext import commands, tasks

import config

LOG = logging.getLogger("bot")

stream = logging.StreamHandler(sys.stdout)
stream.setFormatter(
    logging.Formatter(
        "{asctime} | {levelname: <8} | {module}:{funcName}:{lineno} - {message}", datefmt="%Y-%m-%d %H:%M:%S", style="{"
    )
)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(stream)


class TiledBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or("tile "), **kwargs)

        self.load_initial_cogs.start()

    @tasks.loop(count=1)
    async def load_initial_cogs(self):
        await self.wait_until_ready()

        for path in pathlib.Path("cogs").glob("[!_]*.py"):
            ext = f"{path.parent}.{path.stem}"

            try:
                self.load_extension(ext)
            except commands.ExtensionError:
                LOG.exception("Failed to load %s", ext)
            else:
                LOG.info("Successfully loaded %s", ext)

    async def on_ready(self):
        LOG.info("Bot ready")


if __name__ == "__main__":
    bot = TiledBot()

    loop = bot.loop

    try:
        loop.run_until_complete(bot.start(config.token))
    except KeyboardInterrupt:
        pass
    finally:
        LOG.info("Shutting down")

        loop.run_until_complete(bot.close())

    to_cancel = list(filter(lambda x: not x.done(), set(asyncio.all_tasks(loop=loop))))

    LOG.info("Cleaning up %d task(s)", len(to_cancel))
    LOG.debug(to_cancel)

    for task in to_cancel:
        task.cancel()

    loop.run_until_complete(
        asyncio.gather(
            *filter(lambda x: x._coro.__name__ != "close_connection", to_cancel), loop=loop, return_exceptions=True
        )
    )

    loop.run_until_complete(loop.shutdown_asyncgens())

    loop.stop()
    loop.close()

    LOG.info("Bot closed")
