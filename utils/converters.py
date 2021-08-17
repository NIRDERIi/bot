import discord
from discord.ext import commands
from bot import Bot, CustomContext
from utils.errors import ProcessError
import pathlib
import inspect
from utils.constants import General


class Limit(commands.Converter):
    def __init__(self, char_limit: int = None):
        self.char_limit = char_limit

    async def convert(self, ctx: CustomContext, argument: str):

        if self.char_limit:
            if len(argument) > self.char_limit:
                raise ProcessError(
                    f"You exceeded the set char limit: `{self.char_limit}`"
                )

        # Can always add more restrictions
        return argument


class TimeConverter(commands.Converter):
    async def convert(self, ctx: CustomContext, argument: str):

        if argument.isdigit() or argument.isnumeric():
            raise ProcessError("Time must have one time extension: (s, m, h, d, w)")

        time_extensions = {
            "s": 1,
            "m": 60,
            "h": 60 * 60,
            "d": 60 * 60 * 24,
            "w": 60 * 60 * 24 * 7,
        }

        arg_extension = argument[-1].lower()
        arg_number = int(argument[:-1])

        if arg_extension not in time_extensions:
            raise ProcessError(
                "Time extension should be either: s, m, h, d, w (got extension: {})".format(
                    arg_extension
                )
            )

        return arg_number * time_extensions[arg_extension]


class SourceConverter(commands.Converter):

    async def convert(self, ctx: CustomContext, argument: str):

        results = {} #{'name': {description: 'something', 'repo_link': 'link'}}
        
        bot: Bot = ctx.bot

        command: commands.Command = bot.get_command(argument.lower())
        if command:
            lines, starting_line = inspect.getsourcelines(inspect.unwrap(command.callback))
            ending_line = len(lines) + starting_line - 1
            command_filename = inspect.getsourcefile(inspect.unwrap(command.callback)).split('\\')[-1]
            iterable = pathlib.Path().glob(f'**/{command_filename}')
            pathlib_path = [path_data for path_data in iterable][0]
            short_path = '/'.join(pathlib_path.parts)
            
            full_link = f'{General.basic_repo}/blob/master/{short_path}#L{starting_line}-L{ending_line}'
            results[command.qualified_name] = {'description': command.description, 'repo_link': full_link}
        return results


