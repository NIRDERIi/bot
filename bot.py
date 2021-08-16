import discord
from discord.ext import commands
import typing
import aiohttp
import os
from dotenv import load_dotenv


load_dotenv()


class Bot(commands.Bot):

    def __init__(self, command_prefix, help_command, description, **options):
        super().__init__(command_prefix, help_command=help_command, description=description, **options)
        self.allowed_users = [876834244167622677, 480404983372709908]
        self.session: typing.Optional[aiohttp.ClientSession] = None

    async def login(self, token: str, **kwargs):

        await super().login(token=token, **kwargs)
        
        self.session = aiohttp.ClientSession()

    async def close(self):
        if self.session:
            await self.session.close()
        await super().close()

    @property
    def retrieve_token(self):
        pass
