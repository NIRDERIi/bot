from discord.ext import commands
from bot import Bot
import os

bot = Bot(
    command_prefix="!",
    help_command=commands.DefaultHelpCommand(),
    description="Discord bot developed in discord.py.",
)

bot.load_extensions()
bot.run(bot.retrieve_token, reconnect=True)
