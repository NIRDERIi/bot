from utils.errors import ProcessError
import discord
from discord.ext import commands
from utils.buttons import Paginator
from bot import CustomContext, Bot
import more_itertools

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
        embed.set_footer(text="run !help <subcommand>")

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
