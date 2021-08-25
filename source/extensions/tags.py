from discord.ext import commands
from datetime import datetime
import discord
import typing
import time


class Tags(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx: commands.Context, *, name: str) -> None:
        async with self.bot.pool.acquire(timeout=20) as conn:
            name = name.lower()
            row = await conn.fetchrow(
                """
                SELECT content
                FROM tags
                WHERE title=$1 AND guild=$2
            """,
                name,
                ctx.guild.id,
            )
            if row:
                await conn.execute(
                    """
                    UPDATE tags
                    SET uses=uses+1
                    WHERE title=$1 AND guild=$2
                """,
                    name,
                    ctx.guild.id,
                )

                await ctx.send(row[0])
            else:
                await ctx.send(f":x: No tag found named `{name}`")

    @tag.command()
    async def create(
        self, ctx: commands.Context, *, name: str
    ) -> typing.Union[discord.Message, None]:
        async with self.bot.pool.acquire(timeout=20) as conn:
            name = name.lower()
            check = await conn.fetchrow(
                """
                SELECT *
                FROM tags
                WHERE title=$1 AND guild=$2
            """,
                name,
                ctx.guild.id,
            )

            if check:
                return await ctx.send(f"Tag `{name}` already exists.")

            await ctx.send("You've 60 seconds to write the tag content..")
            try:
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=60,
                )

                if len(message.content) > 2000:
                    return await ctx.send("Content must be 2000 characters or less.")

                await conn.execute(
                    """
                    INSERT INTO tags
                    VALUES ($1, $2, $3, $4, to_timestamp($5), $6)
                """,
                    name,
                    message.content,
                    ctx.author.id,
                    ctx.guild.id,
                    round(time.time()),
                    0,
                )

                await ctx.send(f":white_check_mark: Successfully created tag `{name}`!")
            except:
                await ctx.send(":warning: Time is out! Process canceled.")

    @tag.command()
    async def delete(
        self, ctx: commands.Context, name: str
    ) -> typing.Union[discord.Message, None]:
        async with self.bot.pool.acquire(timeout=20) as conn:
            check = await conn.fetchrow(
                """
                SELECT *
                FROM tags
                WHERE title=$1 AND author=$2 AND guild=$3
            """,
                name,
                ctx.author.id,
                ctx.guild.id,
            )

            if not check:
                return await ctx.send(f":x: You don't own a tag named `{name}`")

            await conn.execute(
                """
                DELETE FROM tags
                WHERE title=$1 AND author=$2 AND guild=$3
            """,
                name,
                ctx.author.id,
                ctx.guild.id,
            )

            await ctx.send(f":white_check_mark: Successfully deleted tag `{name}`")

    @tag.command()
    async def edit(self, ctx: commands.Context, *, name: str) -> None:
        async with self.bot.pool.acquire(timeout=20) as conn:
            name = name.lower()
            check = await conn.fetchrow(
                """
                SELECT *
                FROM tags
                WHERE title=$1 AND guild=$2 AND author=$3
            """,
                name,
                ctx.guild.id,
                ctx.author.id,
            )

            if not check:
                return await ctx.send(f"You don't own a tag named `{name}`")

            await ctx.send("You've 60 seconds to write the new tag content..")
            try:
                message = await self.bot.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel,
                    timeout=60,
                )

                if len(message.content) > 2000:
                    return await ctx.send("Content must be 2000 characters or less.")

                await conn.execute(
                    """
                    UPDATE tags
                    SET content=$1
                    WHERE author=$2 AND guild=$3 AND title=$4
                """,
                    message.content,
                    ctx.author.id,
                    ctx.guild.id,
                    name,
                )

                await ctx.send(f":white_check_mark: Successfully edited tag `{name}`!")
            except:
                await ctx.send(":warning: Time is out! Process canceled.")

    @tag.command()
    async def info(self, ctx: commands.Context, name: str) -> None:
        async with self.bot.pool.acquire(timeout=20) as conn:
            name = name.lower()
            row = await conn.fetchrow(
                """
                SELECT author, created_at, uses
                FROM tags
                WHERE title=$1 AND guild=$2
            """,
                name,
                ctx.guild.id,
            )
            if row:
                created_at = row[1].strftime("%x, %X")
                author = (
                    f"created at `{created_at}` by `{ctx.guild.get_member(row[0])}` and"
                    if ctx.guild.get_member(row[0])
                    else f"created at `{created_at}`"
                )
                await ctx.send(f"> tag `{name}`{author} used `{row[2]}` times.")
            else:
                await ctx.send(f":x: No tag found named `{name}`")


def setup(bot: commands.Bot):
    bot.add_cog(Tags(bot))
