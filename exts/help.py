from utils.functions import get_group_help
from utils.constants import Colours
from discord.ext import commands
import discord
import typing


class help_command(commands.HelpCommand):
    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(
            title="Command help: `{}`".format(command),
            description="```{}```\n{}".format(
                await self.get_command_signature(command),
                command.description if command.description else ''
            ),
            color=Colours.invisible,
        )
        await self.context.send(embed=embed)

    async def send_group_help(self, group: commands.Group):
        return await get_group_help(self.context, group)

    async def get_command_signature(
        self, command: typing.Union[commands.Command, commands.Group]
    ):
        signature = "{}{} {}".format(
            self.context.prefix,
            command.qualified_name,
            command.signature.replace("_", " "),
        )

        return signature


def setup(bot: commands.Bot):
    bot.help_command = help_command()
