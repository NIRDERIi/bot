from discord.ext import commands
from dotenv import load_dotenv
import utils
import typing
import aiohttp
import pathlib
import datetime
import asyncpg
import discord
import os


load_dotenv()

class CustomContext(commands.Context):
    async def send_confirm(
        self, *args, check: typing.Callable[..., bool] = None, **kwargs
    ) -> typing.Tuple[discord.Message, typing.Optional[discord.ui.View]]:
        if not kwargs.get("view"):
            view = utils.buttons.ConfirmButtonBuild(
                timeout=utils.constants.Time.basic_timeout, ctx=self, check=check
            )
            message = await self.send(*args, **kwargs, view=view)
            await view.wait()
            if view.value is None:
                raise utils.errors.ProcessError("Timed out!")

            return view, message
        else:
            return super().send(*args, **kwargs)


class Bot(commands.Bot):
    def __init__(
        self,
        command_prefix: str,
        help_command: commands.HelpCommand,
        description: str,
        **options,
    ) -> None:
        super().__init__(
            command_prefix,
            help_command=help_command,
            description=description,
            **options,
        )
        self.pool = self.loop.run_until_complete(
            asyncpg.create_pool(dsn=self.retrieve_dsn, min_size=1, max_size=5)
        )
        self.allowed_users = [
            876834244167622677,
            480404983372709908,
            534403455201312793,
        ]
        self.session: typing.Optional[aiohttp.ClientSession] = None
        self.uptime = datetime.datetime.utcnow()

    async def login(self, token: str, **kwargs) -> None:

        await super().login(token=token, **kwargs)

        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        if self.session:
            await self.session.close()
        await super().close()

    @property
    def retrieve_token(self) -> str:

        token = os.getenv("TOKEN")
        if not token:
            raise utils.errors.EnvError("Fetching the TOKEN failed.")
        return token

    @property
    def retrieve_dsn(self) -> str:

        dsn = os.getenv("DSN")
        if not dsn:
            raise utils.errors.EnvError("Fetching the DSN failed.")
        return dsn

    def load_extensions(self) -> None:

        files = [
            file[:-3]
            for file in os.listdir("exts")
            if file.endswith(".py") and "__" not in file
        ]

        # Just to make sure loop.
        full_paths = []
        for file in files:
            iterable = pathlib.Path().glob(f"**/{file}.py")
            for option in iterable:
                path = ".".join(option.parts)
                path = path.replace(".py", "")
                full_paths.append(path)

        for file_path in full_paths:

            self.load_extension(file_path)
        self.load_extension("jishaku")

    async def get_context(self, message: discord.Message, *, cls=CustomContext):
        return await super().get_context(message, cls=cls)
