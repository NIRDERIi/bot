from utils.constants import Time, General
from utils.errors import ProcessError
from bot import CustomContext, Bot
from discord.ext import commands
import contextlib
import traceback
import datetime
import discord
import difflib
import re


class Handler(commands.Cog):
    def __init__(self, bot):
        self.bot: Bot = bot

    @commands.Cog.listener(name="on_command_error")
    async def command_error_handler(
        self, ctx: CustomContext, error: commands.CommandError
    ):
        new_error = getattr(error, "original", error)
        embed = discord.Embed(
            title=re.sub("(?<!^)(?=[A-Z])", " ", str(type(new_error).__name__)),
            color=discord.Colour.red(),
        )
        if isinstance(error, commands.MissingRequiredArgument):
            embed.description = (
                f"`{error.param.name}` is a required argument that is missing."
            )
        elif isinstance(error, commands.TooManyArguments):
            embed.description = str(error.args)
        elif isinstance(error, commands.MessageNotFound):
            embed.description = (
                f"Could not find message by argument: `{error.argument}`"
            )
        elif isinstance(error, commands.MemberNotFound):
            embed.description = f"Could not find member by argument: `{error.argument}`"
        elif isinstance(error, commands.UserNotFound):
            embed.description = f"Could not find user by argument: `{error.argument}`"
        elif isinstance(error, commands.ChannelNotFound):
            embed.description = (
                f"Could not find channel by argument: `{error.argument}`"
            )
        elif isinstance(error, commands.ChannelNotReadable):
            embed.description = f"I can't read from {error.argument.name}"
        elif isinstance(error, commands.RoleNotFound):
            embed.description = f"Could not find role by argument: `{error.argument}`"
        elif isinstance(error, commands.EmojiNotFound):
            embed.description = error.args[0]
        elif isinstance(error, commands.ThreadNotFound):
            embed.description = f"Could not find thread by argument: `{error.argument}`"
        elif isinstance(error, commands.CommandNotFound):
            embed.description = f"Command `{ctx.invoked_with}` not found."
            options = difflib.get_close_matches(
                word=ctx.invoked_with,
                possibilities=[command.name for command in self.bot.commands],
            )
            if options:
                options_str = ", ".join([f"`{option}`" for option in options])
                embed.description += f"\n\n**Close matches:** {options_str}"
        elif isinstance(error, commands.MissingPermissions):
            permissions_missing = ", ".join(
                [f"`{permission}`" for permission in error.missing_permissions]
            )
            embed.description = permissions_missing
        elif isinstance(error, commands.BotMissingPermissions):
            permissions_missing = ", ".join(
                [f"`{permission}`" for permission in error.missing_permissions]
            )
            embed.description = permissions_missing
        elif isinstance(error, commands.DisabledCommand):
            embed.description = f"This command seems to be globally disabled."
        elif isinstance(error, commands.BadArgument):
            embed.description = str(error.args[0])
        elif isinstance(error, commands.BadUnionArgument):
            embed.description = str(error.args[0])
        elif (
            isinstance(error, ProcessError)
            or isinstance(new_error, ProcessError)
            or type(error) is ProcessError
            or type(error).__name__ == "ProcessError"
        ):
            embed.description = str(error.args[0])
        elif isinstance(error, commands.CheckFailure):
            embed.description = "You have no perms to use this command."
        elif isinstance(new_error, discord.NotFound):
            embed.description = f"{new_error.text}"
        elif isinstance(new_error, discord.Forbidden):
            embed.description = f"{new_error.text} Status {new_error.status}"
        else:
            traceback.print_exception(type(error), error, error.__traceback__)
            async with self.bot.pool.acquire(timeout=Time.BASIC_DBS_TIMEOUT()) as conn:
                bug_id = await conn.fetch(
                    """INSERT INTO bugs (guild_id, user_id, short_error, full_traceback, error_time) VALUES($1, $2, $3, $4, $5) RETURNING bug_id""",
                    ctx.guild.id,
                    ctx.author.id,
                    str(error),
                    "\n".join(
                        traceback.format_exception(
                            type(error), error, error.__traceback__
                        )
                    ),
                    datetime.datetime.utcnow(),
                )
            bug_id = bug_id[0]["bug_id"]
            embed.title = type(error).__name__
            embed.description = f"Unknown error. Please report it in [support server]({General.SUPPORT_SERVER()}).\n**Bug id:** {bug_id}"

        with contextlib.suppress(
            discord.HTTPException, discord.Forbidden, discord.NotFound
        ):
            await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Handler(bot))
