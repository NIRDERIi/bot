from bot import CustomContext, Bot
from utils.errors import ProcessError
from utils.constants import Time, Emojis
from discord.ext import commands
import datetime
import re


class Tags(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: CustomContext, *, name: str) -> None:
        async with self.bot.pool.acquire(timeout=Time.db_time) as conn:
            name = name.lower()
            query = "SELECT tag_content FROM tags WHERE owner_id=$1 AND guild_id=$2 AND tag_title=$3"
            results = await conn.fetchrow(query, ctx.author.id, ctx.guild.id, name)

            if not results:
                return await ctx.send(
                    f"{Emojis.custom_denial} No such tag named: `{name}`."
                )

            await ctx.send(results[0])

    @tag.command()
    async def create(self, ctx: CustomContext, name: str, *, content: str):
        async with self.bot.pool.acquire(timeout=Time.db_time) as conn:
            name = name.lower()
            regex = re.compile(r"<@!?([0-9]+)>$")

            if not name.isascii:
                return await ctx.send(
                    f"{Emojis.custom_denial} Must not have non-ascii characters in tag name."
                )

            query = "SELECT tag_content FROM tags WHERE owner_id=$1 AND guild_id=$2 AND tag_title=$3"
            results = await conn.fetchrow(query, ctx.author.id, ctx.guild.id, name)

            if results:
                return await ctx.send(f"{Emojis.custom_denial} Tag already exist.")

            query = "INSERT INTO tags (guild_id, owner_id, tag_title, tag_content, uses, created_at, updated_at) VALUES ($1, $2, $3, $4, $5, $6, $7)"
            results = await conn.execute(
                query,
                ctx.guild.id,
                ctx.author.id,
                name,
                content,
                0,
                datetime.datetime.now(),
                datetime.datetime.now(),
            )
            await ctx.send(
                f"{Emojis.custom_approval} Succesfully created tag `{name}`."
            )


def setup(bot: commands.Bot):
    bot.add_cog(Tags(bot))
