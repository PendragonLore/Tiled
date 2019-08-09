# -*- coding: utf-8 -*-

import inspect

import discord


def control(reaction):
    def inner(func):
        func.__map_reaction__ = reaction

        return func

    return inner


class MapSession:
    def __init__(self, ctx, map_array):
        self.ctx = ctx

        self.current_pos = [0, 0]
        self.msg = None
        self._task = None

        def is_control(thing):
            return inspect.ismethod(thing) and hasattr(thing, "__map_reaction__")

        self.controls = {
            emoji: func
            for emoji, func in [(x.__map_reaction__, x) for _, x in inspect.getmembers(self, is_control)]
        }

        self.original_map = map_array
        self.map_copy = map_array.copy()

    @property
    def alive(self):
        return not self._task.done()

    def start(self):
        self._task = self.ctx.bot.loop.create_task(self.task())

    async def cancel(self):
        self._task.cancel()
        del self.ctx.bot.sessions[f"{self.ctx.author.id}-{self.ctx.guild.id}"]

        if self.msg is not None:
            try:
                await self.msg.edit(content="Session cancelled.", embed=None)
            except discord.HTTPException:
                pass

            try:
                await self.msg.clear_reactions()
            except discord.HTTPException:
                try:
                    await self.msg.delete()
                except discord.HTTPException:
                    pass

    def check(self, payload):
        return (str(payload.emoji) in self.controls
                and payload.user_id == self.ctx.author.id
                and payload.message_id == self.msg.id)

    def make_embed(self):
        embed = discord.Embed(description=self.render_map())

        embed.add_field(
            name="Current tile",
            value=f"You landed on a **{self.original_map[self.current_pos[0]][self.current_pos[1]]}** tile!"
        )

        return embed

    @control("\U000025b6")
    def right(self):
        if not self.current_pos[1] == (len(self.original_map[self.current_pos[0]]) - 1):
            self.current_pos[1] += 1

    @control("\U0001f53d")
    def down(self):
        if not self.current_pos[0] == (len(self.map_copy) - 1):
            self.current_pos[0] += 1

    @control("\U000025c0")
    def left(self):
        if not self.current_pos[1] == 0:
            self.current_pos[1] -= 1

    @control("\U0001f53c")
    def up(self):
        if not self.current_pos[0] == 0:
            self.current_pos[0] -= 1

    @control("\U000023f9")
    async def stop(self):
        await self.cancel()

    async def task(self):
        self.map_copy[0][0] = 200

        self.msg = await self.ctx.send(embed=self.make_embed())

        for reaction in sorted(self.controls.keys(), reverse=True):
            await self.msg.add_reaction(reaction)

        while True:
            payload = await self.ctx.bot.wait_for("raw_reaction_add", check=self.check)

            pos = self.current_pos
            self.map_copy[pos[0]][pos[1]] = self.original_map[pos[0]][pos[1]]

            func = self.controls[str(payload.emoji)]

            if inspect.iscoroutinefunction(func):
                await func()
            else:
                func()

            self.map_copy[self.current_pos[0]][self.current_pos[1]] = 200

            await self.msg.edit(embed=self.make_embed())

    def render_map(self):
        fmt = ""

        for line in self.map_copy:
            for tile in line:
                if tile == 200:
                    fmt += "<:player:609140893563355137>"
                    continue
                fmt += f"{tile}\N{combining enclosing keycap}"
            fmt += "\n"

        return fmt
