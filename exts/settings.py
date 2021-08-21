from bot import Bot
from discord.ext import commands


class settings(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Code here


def setup(bot: Bot):
    bot.add_cog(settings(bot))
