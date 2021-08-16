import discord
from discord.ext import commands


class EnvError(Exception):

    pass


class ProcessError(commands.CommandError):

    pass
