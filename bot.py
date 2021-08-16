import os
from discord.ext import commands
from dotenv import load_dotenv

import typing
import aiohttp
import yaml  # you need to pip install PyYaml

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

    def run(self): # no arguments required
        ignored_extensions = []

        [
            self.load_extension("exts.{}".format(ext.replace(".py", "")))
            for ext in os.listdir("exts/")
            if ext.endswith(".py") and not ext in ignored_extensions
        ]

        super().run(self.retrieve_token, reconnect=True)

    @property
    def retrieve_token(self):
        with open("config.yaml") as f:
            config = yaml.load(f, yaml.FullLoader)
        return config.get("token")
