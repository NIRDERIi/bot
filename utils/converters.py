import discord
from discord.ext import commands
from bot import CustomContext
from utils.errors import ProcessError


class Limit(commands.Converter):
    def __init__(self, char_limit: int = None):
        self.char_limit = char_limit

    async def convert(self, ctx: CustomContext, argument: str):

        if self.char_limit:
            if len(argument) > self.char_limit:
                raise ProcessError(
                    f"You exceeded the set char limit: `{self.char_limit}`"
                )

        # Can always add more restrictions
        return argument


class TimeConverter(commands.Converter):
    
    async def convert(self, ctx: CustomContext, argument: str):

        if argument.isdigit() or argument.isnumeric():
            raise ProcessError("Time must have one time extension: (s, m, h, d, w)")

        time_extensions = {
            "s": 1,
            "m": 60,
            "h": 60*60,
            "d": 60*60*24,
            "w": 60*60*24*7,
        }

        arg_extension = argument[-1].lower()
        arg_number = int(argument[:-1])
        
        if arg_extension not in time_extensions:
            raise ProcessError('Time extension should be either: s, m, h, d, w (got extension: {})'.format(arg_extension))

        return arg_number * time_extensions[arg_extension]