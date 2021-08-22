import discord
from utils.errors import ProcessError
from utils.functions import paste
from discord.ext import commands

import random, os
from string import ascii_letters
from randfacts import get_fact
from bot import Bot, CustomContext
from utils.converters import CodeConverter
from utils.constants import Colours, Emojis
from utils.buttons import Calculator


class Fun(commands.Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.snekbox_url = "http://localhost:8060/eval"
        self.running_calc = []

    @commands.command(description="Runs Python code.", aliases=["exec", "execute"])
    async def run(self, ctx: CustomContext, *, code: CodeConverter):
        try:
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
                    content = f"{ctx.author.mention} {emoji}, your eval job ran out of memory."
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
        except:
            raise ProcessError("Docker container is currently down.")

    @commands.command(
        name="calculator", description="Displays button calculator.", aliases=["calc"]
    )
    async def _calculator(self, ctx: CustomContext):
        if ctx.author.id in self.running_calc:
            raise ProcessError("You already have a running calculator.")

        calculator = Calculator(ctx, timeout=20.0)
        self.running_calc.append(ctx.author.id)
        view: discord.ui.View = await calculator.run(
            embed=discord.Embed(
                title="Math genius.", color=discord.Colour.blurple()
            ).set_thumbnail(url=self.bot.user.avatar.url)
        )
        await view.wait()
        self.running_calc.remove(ctx.author.id)

    @commands.command()
    async def password(self, ctx: CustomContext):
        generated_password = "".join([random.choice(ascii_letters) for _ in range(15)])

        try:
            embed = discord.Embed(
                title="Here's your password:",
                description=f"`{generated_password}`, keep it safe!",
                color=Colours.invisible,
            )
            await ctx.author.send(embed=embed)
            await ctx.send(f"{Emojis.custom_approval} Successfully sent the password!")
        except:
            await ctx.send(f"{Emojis.custom_denial} Could not DM you the password...")

    @commands.command()
    async def news(self, ctx: CustomContext, *keywords):
        url = f"https://api.currentsapi.services/v1/search?apiKey={os.getenv('CURRENTS_API')}&language=en&limit=20"

        if keywords:
            url += f"&keywords={' '.join(keywords)}"

        async with self.bot.session.get(url) as res:
            json_data = await res.json()

            if not json_data["status"] == "ok":
                return await ctx.send(f"{Emojis.custom_denial} No news found.")

            news = random.choice(json_data["news"])
            url = news.get("url")
            time = news.get("published").split(" ")
            time = f"{time[0].replace('-', '/')} {time[1]}"
            title = news.get("title")
            image = news.get("image")
            content = news.get("description")

        embed = discord.Embed(
            title=title, url=url, description=content, color=discord.Colour.blurple()
        )
        if image:
            embed.set_image(url=image)
        if time:
            embed.set_footer(text=f"Published at {time}")

        await ctx.send(embed=embed)
    
    @commands.command()
    async def fact(self, ctx: CustomContext):
        generated_fact = get_fact()

        embed = discord.Embed(
            description=generated_fact,
            color=Colours.invisible
        )

        await ctx.send(embed=embed)

    @commands.command()
    async def iq(self, ctx: CustomContext, member: discord.Member) -> None:
        rates = {
            1: {
                "from": 1,
                "to": 50
            },
            2: {        
                "from": 51,
                "to": 100   
            },
            3: {        
                "from": 101,
                "to": 150   
            },
            4: {        
                "from": 151,
                "to": 200 
            },
            5: {        
                "from": 201,
                "to": 200 
            },
            6: {        
                "from": 251,
                "to": 300 
            },
        }
        rate = random.choice(rates)
        iq_rate = random.randint(rates[rate]["from"], rates[rate]["to"])

        await ctx.send(iq_rate)


def setup(bot: Bot):
    bot.add_cog(Fun(bot))
