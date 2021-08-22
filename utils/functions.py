from utils.errors import ProcessError
import discord
from discord.ext import commands
from utils.buttons import Paginator
from bot import CustomContext, Bot
import more_itertools
import re
import difflib
import traceback
from utils.constants import Time, General
import datetime
import contextlib

MYSTB_DOCUMENTS = "https://mystb.in/documents"
MYSTB_FORMAT = "https://mystb.in/{key}"


async def get_group_help(ctx: CustomContext, group: commands.Group):
    async def check(interaction: discord.Interaction) -> None:
        return interaction.user.id == ctx.author.id

    paginator = Paginator(ctx, embeds=[], timeout=20.0, check=check)
    iterable = more_itertools.sliced(tuple(group.commands), 5)
    commands_lst__tuples = [command_tuple for command_tuple in iterable]
    for command_tuple in commands_lst__tuples:

        embed = discord.Embed(
            title=f"{group.qualified_name} commands group.",
            description="Subcommands:\n",
            color=discord.Colour.blurple(),
        )

        for command in command_tuple:

            embed.description += (
                f"> {command.name} {command.signature.replace('_', ' ')}\n"
            )
        embed.set_footer(text="run !help {} <subcommand>".format(group.qualified_name))

        paginator.add_embed(embed=embed)

    await paginator.run()


def get_divmod(seconds: int):

    days, hours = divmod(seconds, 86400)
    hours, minutes = divmod(hours, 3600)
    minutes, seconds = divmod(minutes, 60)

    days, hours, minutes, seconds = (
        round(days),
        round(hours),
        round(minutes),
        round(seconds),
    )
    return days, hours, minutes, seconds


async def paste(bot: Bot, text: str):

    data = bytes(text, encoding="utf-8")
    async with bot.session.post(url=MYSTB_DOCUMENTS, data=data) as response:

        if response.status != 200:
            raise ProcessError(f"Unexpected error with return status {response.status}")
        raw_json = await response.json(content_type=None, encoding="utf-8")
        key = raw_json.get("key")
        full_link = MYSTB_FORMAT.format(key=key)
        return full_link


async def error_handler(ctx: CustomContext, error: commands.CommandError):
    bot: Bot = ctx.bot
    new_error = getattr(error, "original", error)
    embed = discord.Embed(
        title=re.sub(
            "(?<!^)(?=[A-Z])", " ", str(type(new_error).__name__)
        ).capitalize(),
        color=discord.Colour.red(),
    )
    if isinstance(error, commands.MissingRequiredArgument):
        signature = "{}{} {}".format(
            ctx.prefix,
            ctx.command.qualified_name,
            ctx.command.signature.replace("_", " "),
        )
        embed.description = f"How to use: `{signature}`"
    elif isinstance(error, commands.TooManyArguments):
        embed.description = str(error.args[0])
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
            possibilities=[command.name for command in bot.commands],
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
        traceback.print_exception(
            type(error), error, error.__traceback__
        )  # So it won't print the error, optional
        async with bot.pool.acquire(timeout=Time.db_time) as conn:
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
        embed.title = re.sub(
            "(?<!^)(?=[A-Z])", " ", str(type(error).__name__)
        ).capitalize()
        embed.description = f"Unknown error. Please report it in [support server]({General.support_guild_invite}).\n**Bug id:** {bug_id}"

    with contextlib.suppress(
        discord.HTTPException, discord.Forbidden, discord.NotFound
    ):
        await ctx.send(embed=embed)
