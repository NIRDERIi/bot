import discord
from discord.ext import commands
import typing
import aiohttp
import os
from dotenv import load_dotenv
from utils.errors import EnvError


load_dotenv()


class Bot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        help_command: commands.HelpCommand,
        description: str,
        **options
    ) -> None:
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            **options
        )
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
    def retrieve_token(self) -> str:

        token = os.getenv("TOKEN")
        if not token:
            raise EnvError("Fetching the TOKEN failed.")
        return token

    @property
    def retrieve_dsn(self) -> str:

        dsn = os.getenv("DSN")
        if not dsn:
            raise EnvError("Fetching the DSN failed.")

    def load_extensions(self):

        files = [
            file[:3]
            for file in os.listdir("exts")
            if file.endswith(".py") and "__" not in file
        ]

        for file in files:

            self.load_extension(file)
