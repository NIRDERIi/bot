"""
MIT License (read LICENSE for details)

Copyright (c) 2021 NIRDERIi, gr-imm
"""

from discord.ext import commands
from discord import Intents
from bot import Bot

intents = Intents.default()
intents.members = True

options = {
    "command_prefix": commands.when_mentioned_or("!"),
    "intents": intents,
    "description": "Discord bot developed in discord.py.",
    "help_command": commands.DefaultHelpCommand(),
    "default_prefix": commands.when_mentioned_or("!"),
    "case_insensitive": True,
    "strip_after_prefix": True,
}  # So many stuff I don't know about needed, tf is default_prefix, and you forgot commad_prefix, I'll make a get_prefix soon. And added a bot mention as prefix

bot = Bot(**options)

bot.load_extensions()  # Thinking we could just use it in `bot.run` overwrite, but sure
bot.run(bot.retrieve_token)  # Unexcpected keyword debug
