from bot import Bot
from discord.ext import commands

class moderation(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    # Code here


def setup(bot: Bot):
    bot.add_cog(moderation(bot))