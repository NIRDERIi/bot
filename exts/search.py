from discord.ext import commands
from youtubesearchpython import VideosSearch
import discord


class search(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        aliases=["yt"],
        description="Sends the first 10 videos that matches the search query",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def youtube(self, context: commands.Context, *, search_query: str) -> None:
        searchResult = VideosSearch(search_query, limit=10)
        searchResult = searchResult.result()
        searchResult = searchResult["result"]

        if len(searchResult) <= 0:
            return await context.send(
                embed=discord.Embed(
                    description="No result matches `{}`".format(search_query),
                    color=discord.Colour.red()
                )
            )

        embedDescription = ""

        for i in searchResult:
            if i["type"] == "video":
                videoTitle = i["title"][:30]
                videoTitle += "..." if len(i["title"]) > 30 else ""
                videoLink = i["link"]

                embedDescription += "➥ [{}]({})".format(videoTitle, videoLink)
                embedDescription += (
                    " - {}\n".format(i["duration"]) if i["duration"] else "\n"
                )

        embed = discord.Embed(
            title="Search results - Youtube",
            description=embedDescription,
            color=0x2F3136,
            url="https://www.youtube.com/results?search_query={}".format(
                "+".join(search_query.split(" "))
            ),
        )

        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(search(bot))