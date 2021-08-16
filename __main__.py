from discord.ext import commands
from discord import Intents
from bot import Bot

intents = Intents.default()
intents.members = True

options = {
    "intents": intents,
    "description": "Discord bot developed in discord.py.",
    "help_command": commands.DefaultHelpCommand(),
    "case_insensitive": True,
    "strip_after_prefix": True,
}

bot = Bot(**options)

bot.load_extensions()
bot.run(bot.retrieve_token, reconnect=True)
