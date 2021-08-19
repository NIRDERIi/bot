from utils.converters import Limit
from utils.functions import get_divmod
from utils.constants import General, Emojis
from bot import Bot, CustomContext
from discord.ext import commands
import datetime
import discord
import time


class Info(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(
        description="Sends general info about the bot.",
        aliases=["info", "ping", "latency"],
    )
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def status(self, ctx: CustomContext) -> None:
        # Getting api latency
        api_start_time = time.time()
        message = await ctx.send("Testing latency...")
        api_end_time = time.time()
        api_ms = round((api_end_time - api_start_time) * 1000)

        # Getting WebSocket latency and database's
        latency = round(self.bot.latency * 1000)

        # db_start_time = time.time()
        # async with self.bot.pool.acquire(timeout=10.0) as conn:
        #     await conn.fetch('''SELECT * FROM guilds_config''')
        # db_end_time = time.time()
        # db_ms = round((db_end_time - db_start_time) * 1000)

        # Defining guilds/users count
        guilds_count = len(self.bot.guilds)
        users_count = len(self.bot.users)

        # Defining the uptime message
        days, hours, minutes, seconds = get_divmod(
            (datetime.datetime.utcnow() - self.bot.uptime).total_seconds()
        )
        uptime_message = ""

        if days:
            uptime_message += f"{days}d, "
        if hours:
            uptime_message += f"{hours}h, "
        if minutes:
            uptime_message += f"{minutes}m, "
        if seconds:
            uptime_message += f"{seconds}s ago."

        # Sending the embed

        embed = discord.Embed(
            title="Bot informations:",
            description=f"➥ Started: {uptime_message}\n"
            f"➥ Servers: {guilds_count}\n"
            f"➥ Users: {users_count}\n"
            f"➥ Latency:\n"
            f"- Discord API: `{api_ms}ms`\n"
            f"- Discord WebSocket: `{latency}ms`\n"
            f"[Support server]({General.support_guild_invite}) - [Invite link]({General.invite_link})",
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        try:
            await message.edit(content=None, embed=embed)
        except discord.NotFound:
            await ctx.send(embed=embed)

    @commands.command(aliases=["report", "suggest"])
    @commands.cooldown(1, 10, commands.BucketType.member)
    async def contact(self, ctx: CustomContext, *, bug: Limit(125)):
        reports_channel = General.support_guild(self.bot).get_channel(
            877633500780593273
        )
        if not reports_channel:
            return

        try:

            await reports_channel.send(
                embed=discord.Embed(
                    description=bug,
                    timestamp=datetime.datetime.now(),
                    color=discord.Colour.blurple(),
                ).set_author(name=ctx.author, icon_url=ctx.author.avatar.url)
            )
            await ctx.send(":mailbox_with_mail: {} Thanks for the feedback, we'll check it as soon as possible!".format(Emojis.custom_approval))
        except:
            pass


def setup(bot: Bot):
    bot.add_cog(Info(bot))
