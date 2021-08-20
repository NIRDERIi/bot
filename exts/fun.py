import discord
from utils.errors import ProcessError
from utils.functions import paste
from discord.ext import commands

from bot import Bot, CustomContext
from utils.converters import CodeConverter
from utils.buttons import Calculator


class Fun(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.snekbox_url = "http://localhost:8060/eval"
        self.running_calc = []

    @commands.command(description="Runs Python code.", aliases=["exec", "execute"])
    async def run(self, ctx: CustomContext, *, code: CodeConverter):

        async with self.bot.session.post(
            url=self.snekbox_url, json={"input": code}
        ) as response:

            if response.status != 200:

                raise ProcessError(
                    f"Calling snekbox returned a bad status code: `{response.status}`"
                )
            data = await response.json()
            stdout: str = data.get("stdout")
            return_code = data.get("returncode")
            lines = stdout.splitlines()
            too_long = False
            if len(lines) > 10:
                too_long = True
            output = "\n".join(
                [
                    f"{str(index + 1).zfill(3)} | {line}"
                    for index, line in enumerate(lines[:10])
                ]
            )
            if return_code == 0:
                emoji = ":white_check_mark:"
            else:
                emoji = ":x:"
            if not output:
                output = "[No output]"
                emoji = ":warning:"
            if return_code == 137:
                content = (
                    f"{ctx.author.mention} {emoji}, your eval job ran out of memory."
                )
            else:
                content = f"{ctx.author.mention} {emoji}, your eval job returned code {return_code}."
            if too_long:
                output += "\n... | (too many lines)"
            if stdout == "":
                output = "[No output]"
            content += f"\n```\n{output}\n```"
            if too_long:
                url = await paste(
                    self.bot, "\n".join([line for _, line in enumerate(lines)])
                )
                content += f"\nFull output in: {url}"
            await ctx.send(content=content)

    @commands.command(
        name="calculator", description="Displays button calculator.", aliases=["calc"]
    )
    async def _calculator(self, ctx: CustomContext):
        if ctx.author.id in self.running_calc:
            raise ProcessError("You already have a running calculator.")

        calculator = Calculator(ctx, timeout=20.0)
        self.running_calc.append(ctx.author.id)
        view: discord.ui.View = await calculator.run(
            embed=discord.Embed(title="Math genius.", color=discord.Colour.blurple())
        )
        await view.wait()
        self.running_calc.remove(ctx.author.id)


def setup(bot: Bot):
    bot.add_cog(Fun(bot))
