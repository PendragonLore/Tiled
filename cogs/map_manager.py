# -*- coding: utf-8 -*-

import random

import numpy as np
from discord.ext import commands

import utils.maps


class MapManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.sessions = {}

        self.mapp = np.array([[random.randint(0, 9) for _ in range(10)] for _ in range(10)])

    @commands.command(name="play")
    async def play(self, ctx):
        fmt = f"{ctx.author.id}-{ctx.guild.id}"

        if fmt in self.bot.sessions:
            return await ctx.send("You already have a playing session running.")

        session = utils.maps.MapSession(ctx, self.mapp)

        self.bot.sessions[fmt] = session
        session.start()


def setup(bot):
    bot.add_cog(MapManager(bot))
