from discord.ext import commands
from dotenv import load_dotenv
from utils.errors import EnvError

import typing
import aiohttp
import warnings
import os
import time

load_dotenv()

class Bot(commands.Bot):
    def __init__(
        self,
        default_prefix: str,
        help_command: commands.HelpCommand,
        description: str,
        **options
    ) -> None:
        super().__init__(
            default_prefix,
            help_command=help_command,
            description=description,
            **options
        )
        self.allowed_users = [876834244167622677, 480404983372709908]
        self.session: typing.Optional[aiohttp.ClientSession] = None

    async def login(self, token: str) -> None:
        await super().login(token)
        self.session = aiohttp.ClientSession()

    def run(self, debug=False) -> None:
        if debug:
            self.load_extension("jishaku")
            
        self.start_time = time.time()
        super().run(self.retrieve_token, reconnect=True)

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await super().close()

    async def on_ready(self) -> None:
        print("Logged in.")

    def load_extensions(self) -> None:

        files = [
            "exts.{}".format(file.replace(".py", ""))
            for file in os.listdir("exts/")
            if file.endswith(".py") and "__" not in file
        ]

        for file in files:

            self.load_extension(file)

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
        return dsn
