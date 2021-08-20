from utils.errors import ProcessError
from discord.ext import commands

from bot import Bot, CustomContext
from utils.converters import CodeConverter


class Fun(commands.Cog):

    def __init__(self, bot: Bot):
        self.bot = bot
        self.snekbox_url = 'http://localhost:8060/eval'

    @commands.command(description='Runs Python code.')
    async def run(self, ctx: CustomContext, *, code: CodeConverter):
        print(code)

        async with self.bot.session.post(url=self.snekbox_url, json={'input': code}) as response:

            if response.status != 200:

                raise ProcessError(f'Calling snekbox returned a bad status code: `{response.status}`')

            data = await response.json()
            print(data)
            stdout = data.get('stdout')
            print(stdout)
            return_code = data.get('returncode')
            content = f'{ctx.author.mention} :white_check_mark:, your eval job returned code {return_code}.'
            content += f'\n```{stdout}```'
            await ctx.send(content=content)


def setup(bot: Bot):
    bot.add_cog(Fun(bot))