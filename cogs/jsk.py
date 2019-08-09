# -*- coding: utf-8 -*-

import jishaku.cog


class Jsk(jishaku.cog.Jishaku):
    pass


def setup(bot):
    bot.add_cog(Jsk(bot))
