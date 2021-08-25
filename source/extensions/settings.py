from ..utilities import converters
from discord.ext import commands
import discord
import typing
import time


class Settings(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.startup = time.time()
        self.bot = bot

    @property
    def uptime(self) -> float:
        """the cog's uptime in seconds"""
        return time.time() - self.startup

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> None:
        """sends the bot's prefix when mentioned"""
        if self.bot.user.mentioned_in(message) and not message.reference:
            prefix = await self.bot.get_prefix(message)
            await message.channel.send(
                f"My prefix here is `{prefix}`, need help? run `{prefix}help`"
            )

    @commands.group(name="set", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def set(self, ctx: commands.Context) -> None:
        """group for settings related commands"""
        await ctx.send_help(ctx.command)

    @set.command()
    async def prefix(
        self, ctx: commands.Context, new: converters.AsciiLimit(3)
    ) -> typing.Union[discord.Message, None]:
        """update the prefix for the context guild"""
        if isinstance(new, discord.Message):
            return

        if self.bot.cached_prefixes[ctx.guild.id] == new or ctx.prefix == new:
            return await ctx.send(f":warning: My prefix is already set to `{new}`")

        async with self.bot.pool.acquire(timeout=20) as conn:
            await conn.execute(
                """
                UPDATE prefixes
                SET prefix=$1
                WHERE guild=$2
            """,
                new,
                ctx.guild.id,
            )
            self.bot.cached_prefixes[ctx.guild.id] = new

        await ctx.send(f":white_check_mark: My prefix is now set to `{new}`")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Settings(bot))
