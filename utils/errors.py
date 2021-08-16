import discord
from discord.ext import commands


class StartError(Exception):
    
    pass

class StartUpError(StartError):

    pass

class EnvError(StartError):

    pass

class ProcessError(commands.CommandError):
    
    pass