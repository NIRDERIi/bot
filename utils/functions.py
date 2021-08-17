import discord
from discord.ext import commands
from utils.buttons import Paginator
from bot import CustomContext
import more_itertools


async def get_group_help(ctx: CustomContext, group: commands.Group):
    async def check(interaction: discord.Interaction):
        return interaction.user.id == ctx.author.id

    paginator = Paginator(ctx, embeds=[], timeout=20.0, check=check)
    iterable = more_itertools.sliced(tuple(group.commands), 5)
    commands_lst__tuples = [command_tuple for command_tuple in iterable]
    for command_tuple in commands_lst__tuples:

        embed = discord.Embed(
            title=f"{group.qualified_name} commands.",
            description="Subcommands:\n",
        )

        for command in command_tuple:

            embed.description += (
                f"> {command.name} {command.signature.replace('_', ' ')}\n"
            )

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
