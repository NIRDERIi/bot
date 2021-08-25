from discord.ext import commands
from discord import Intents
from ..utilities import functions
import configparser
import discord
import asyncpg
import aiohttp
import typing
import time
import os


class Bot(commands.Bot):
    def __init__(self) -> None:
        self.startup = time.time()

        intents = Intents.default()
        intents.members = True

        options = {
            "intents": intents,
            "owner_id": 842418069732196372,
            "command_prefix": self.get_prefix,
            "case_insensitive": True,
        }

        super().__init__(**options)
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("settings.cfg")

        def predicate(ctx: commands.Context):
            if not ctx.guild and not ctx.author.id == self.owner_id:
                return

            return True

        self.check(predicate)
        self.database_section = self.config_parser["PostgreSQL Keys"]
        self.cached_prefixes = {}
        self.pool = self.loop.run_until_complete(asyncpg.create_pool(self.dsn))

    async def on_command_error(self, context, exception):
        return await functions.error_handler(context, exception)

    async def get_prefix(
        self, message: discord.Message
    ) -> typing.Union[typing.List[str], str]:
        """gets the prefix from database"""
        if not message.guild:
            return "//"

        if message.guild.id in self.cached_prefixes:
            return self.cached_prefixes[message.guild.id]

        async with self.pool.acquire(timeout=20) as conn:
            prefix = await conn.fetchrow(
                """
                SELECT prefix
                FROM prefixes
                WHERE guild=$1
            """,
                message.guild.id,
            )
            if not prefix:
                await conn.execute(
                    """
                    INSERT INTO prefixes
                    VALUES ($1, $2)
                    """,
                    message.guild.id,
                    "//",
                )
                self.cached_prefixes[message.guild.id] = "//"
                return self.cached_prefixes[message.guild.id]
            self.cached_prefixes[message.guild.id] = prefix[0]
            return self.cached_prefixes[message.guild.id]

    async def build_tables(self) -> None:
        """makes required tables in database."""
        with open("builder.sql", "r") as file:
            queries = file.read()

        async with self.pool.acquire() as conn:
            await conn.execute(queries)

    async def on_ready(self):
        await self.build_tables()
        print("Bot ready.")

    async def login(self, token: str, **kwargs) -> None:

        await super().login(token=token, **kwargs)

        self.session = aiohttp.ClientSession()

    def run(self):
        """loads required extensions before running the bot"""
        for extension in self.initial_extensions:
            self.load_extension(extension)
        self.load_extension("jishaku")
        super().run(self.token, reconnect=True)

    @property
    def initial_extensions(self) -> typing.List[str]:
        """all needed extensions"""
        return [
            f"source.extensions.{i[:-3]}"
            for i in os.listdir("source/extensions")
            if not i[:-3] in self.ignored_extensions and i.endswith(".py")
        ]

    @property
    def ignored_extensions(self) -> typing.List[str]:
        """all ignored extensions"""
        return ["__init__"]

    @property
    def uptime(self) -> float:
        """the bot uptime in seconds."""
        return time.time() - self.startup

    @property
    def repository(self) -> str:
        """the bot's Github repository."""
        return "https://github.com/gr-imm/discord-bot/"

    @property
    def server(self) -> str:
        """the bot's official server."""
        return "https://discord.gg/rShMhH8asE"

    @property
    def token(self) -> str:
        """retrieve the bot token from settings.cfg"""
        return self.config_parser["API Keys"]["DISCORD_API"]

    @property
    def invite(self) -> str:
        """invite for the bot"""
        return f"https://discord.com/api/oauth2/authorize?client_id={self.user.id}&permissions=8&scope=bot"

    @property
    def dsn(self) -> str:
        """retrieve the bot dsn from settings.cfg"""
        return "postgresql://{}:{}@{}:{}/{}".format(
            self.database_section["USERNAME"],
            self.database_section["PASSWORD"],
            self.database_section["HOST"],
            self.database_section["PORT"],
            self.database_section["DATABASE"],
        )
