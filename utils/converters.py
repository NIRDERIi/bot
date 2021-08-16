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
