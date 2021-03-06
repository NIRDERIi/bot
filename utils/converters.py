import discord
from discord.ext import commands
from bot import Bot, CustomContext
from utils.errors import ProcessError
import pathlib
import inspect
from utils.constants import General
import typing
import importlib


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
    async def convert(self, ctx: CustomContext, argument: str) -> int:

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

        if ".env" in argument:
            raise ProcessError("Your messages contains a forbidden file.")

        results = {}  # {'name': {description: 'something', 'repo_link': 'link'}}

        bot: Bot = ctx.bot

        command: typing.Optional[commands.Command] = bot.get_command(argument.lower())
        if command:
            lines, starting_line = inspect.getsourcelines(
                inspect.unwrap(command.callback)
            )
            ending_line = len(lines) + starting_line - 1
            command_filename = inspect.getsourcefile(
                inspect.unwrap(command.callback)
            ).split("\\")[-1]
            iterable = pathlib.Path().glob(f"**/{command_filename}")
            pathlib_path = [path_data for path_data in iterable][0]
            short_path = "/".join(pathlib_path.parts)

            full_link = f"{General.basic_repo}/blob/master/{short_path}#L{starting_line}-L{ending_line}"
            results[f"Command: {command.qualified_name}"] = {
                "description": command.description,
                "repo_link": full_link,
            }

        cog: typing.Optional[commands.Cog] = bot.get_cog(argument)
        if cog:
            filename = cog.qualified_name
            iterable = pathlib.Path().glob(f"**/{filename}.py")
            pathlib_path = [path_data for path_data in iterable][0]
            short_path = "/".join(pathlib_path.parts).lower()

            full_link = f"{General.basic_repo}/blob/master/{short_path}"
            results[f"Cog: {cog.qualified_name}"] = {
                "description": cog.__doc__,
                "repo_link": full_link,
            }

        glob_check = f"**/{argument.lower()}"
        if not argument.endswith(".py"):
            glob_check += f".py"
        iterable = pathlib.Path().glob(glob_check)
        pathlib_paths_list = [i for i in iterable]
        if pathlib_paths_list:
            short_path = "/".join(pathlib_paths_list[0].parts)
            full_link = f"{General.basic_repo}/blob/master/{short_path}"
            filename_source = short_path.split("/")[-1]
            results[f"File: {filename_source}"] = {
                "description": None,
                "repo_link": full_link,
            }

        file_modules: list = []
        all_classes = []
        all_functions = []

        for module in pathlib.Path().glob(f"**/*.py"):

            if module.name != pathlib.Path(__file__).name:
                file_modules.append(
                    importlib.import_module(".".join(module.parts)[:-3])
                )

        for module in file_modules:
            for name, _class in inspect.getmembers(module, inspect.isclass):

                if name == argument:
                    all_classes.append(_class)

            for name, function in inspect.getmembers(module, inspect.isfunction):
                if name == argument:
                    all_functions.append(function)

        all_classes = list(set(all_classes))
        all_functions = list(set(all_functions))

        if not all_classes and not all_functions and not results:
            raise ProcessError(
                f"Could not convert {argument} to a valid command, cog, file, function or a class."
            )

        for _class in all_classes:
            filename = inspect.getsourcefile(inspect.unwrap(_class)).split("\\")[-1]
            iterable = pathlib.Path().glob(f"**/{filename}")
            pathlib_path = [pathlib_path for pathlib_path in iterable][0]
            short_path = "/".join(pathlib_path.parts)

            lines, starting_line = inspect.getsourcelines(_class)
            ending_line = len(lines) + starting_line - 1

            full_link = f"{General.basic_repo}/blob/master/{short_path}#L{starting_line}-L{ending_line}"
            results[f"Class: {argument}"] = {
                "description": _class.__doc__,
                "repo_link": full_link,
            }

        for function in all_functions:
            filename = inspect.getsourcefile(inspect.unwrap(function)).split("\\")[-1]
            iterable = pathlib.Path().glob(f"**/{filename}")
            pathlib_path = [pathlib_path for pathlib_path in iterable][0]
            short_path = "/".join(pathlib_path.parts)

            lines, starting_line = inspect.getsourcelines(_class)
            ending_line = len(lines) + starting_line - 1

            full_link = f"{General.basic_repo}/blob/master/{short_path}#L{starting_line}-L{ending_line}"
            results[f"Function: {argument}"] = {
                "description": _class.__doc__,
                "repo_link": full_link,
            }
        return results


class CodeConverter(commands.Converter):
    async def convert(self, ctx: CustomContext, argument: str):
        if argument.startswith("```py") and argument.endswith("```"):
            argument = argument[5:-3]

        return argument
