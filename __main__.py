"""
MIT License (read LICENSE for details)

Copyright (c) 2021 NIRDERIi, gr-imm
"""

from discord.ext import commands
from discord import Intents
from bot import Bot

intents = Intents.default()
intents.members = (
    True  # disabled precense since we don't use that and it's using more memory
)

options = {
    "command_prefix": commands.when_mentioned_or("."),
    "intents": intents,
    "description": "Discord bot developed in discord.py.",
    "help_command": commands.DefaultHelpCommand(),
    "case_insensitive": True,
}

bot = Bot(**options)

bot.load_extensions()
bot.run(bot.retrieve_token)
