from utils.errors import ProcessError
from utils.functions import paste
from discord.ext import commands

from bot import Bot, CustomContext
from utils.converters import CodeConverter


class Fun(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.snekbox_url = "http://localhost:8060/eval"

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
            content += f"\n```{output}```"
            if too_long:
                url = await paste(
                    self.bot, "\n".join([line for _, line in enumerate(lines)])
                )
                content += f"\nFull output in: {url}"
            await ctx.send(content=content)


def setup(bot: Bot):
    bot.add_cog(Fun(bot))
