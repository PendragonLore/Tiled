# -*- coding: utf-8 -*-

import traceback
import pathlib

from discord.ext import commands, tasks

import config


class TiledBot(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(command_prefix=commands.when_mentioned_or("tile "), **kwargs)

        self.load_initial_cogs.start()

    @tasks.loop(count=1)
    async def load_initial_cogs(self):
        await self.wait_until_ready()

        for path in pathlib.Path("cogs").glob("[!_]*.py"):
            try:
                self.load_extension(f"{path.parent}.{path.stem}")
            except commands.ExtensionError:
                traceback.print_exc()

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")


if __name__ == "__main__":
    bot = TiledBot()

    bot.run(config.token)
