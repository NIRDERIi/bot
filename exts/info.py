import datetime
from utils.constants import General
import discord
from discord.ext import commands
from bot import Bot, CustomContext
import time
from utils.functions import get_divmod


class Info(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(description="Sends genral info about the bot.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def status(self, ctx: CustomContext):
        api_start_time = time.time()

        message = await ctx.send("Testing latency...")
        api_end_time = time.time()
        api_ms = round((api_end_time - api_start_time) * 1000)

        latency = round(self.bot.latency * 1000)
        """
        db_start_time = time.time()
        async with self.bot.pool.acquire(timeout=10.0) as conn:
            await conn.fetch('''SELECT * FROM guilds_config''')
        db_end_time = time.time()
        db_ms = round((db_end_time - db_start_time) * 1000)"""
        guilds_count = len(self.bot.guilds)
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
        description = f"**Started:** {uptime_message}\n**Latency:**\n > __Discord API__: `{api_ms}ms`\n> __Discord websocket__: `{latency}ms`\n"
        description += f"Servers: {guilds_count}\nSupport server: [Invite Link]({General.support_guild_invite})"
        embed = discord.Embed(title="Bot info/status", description=description)
        try:
            await message.edit(content=None, embed=embed)
        except discord.NotFound:
            await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Info(bot))
