from discord.ext import commands
from dateutil.parser import parse
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
    async def youtube(self, ctx, *, search_query: str) -> None:
        searchResult = VideosSearch(search_query, limit=10)
        searchResult = searchResult.result()
        searchResult = searchResult["result"]

        if len(searchResult) <= 0:
            return await ctx.send(
                embed=discord.Embed(
                    description="No result matches `{}`".format(search_query),
                    color=discord.Colour.red(),
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

        await ctx.send(embed=embed)

    @commands.group(aliases=["git"], invoke_without_command=True, ignore_extra=False)
    async def github(self, ctx) -> None:
        embed = discord.Embed(
            title="Github commands",
            description="➥ Subcommands:\n" "- user\n" "- repository\n",
            color=0x2F3136,
        )
        embed.set_thumbnail(
            url="https://images-ext-1.discordapp.net/external/Wv3a3cxRzc7jnIgHtU7_yZpnRWPU4_r4BlfNaaYQ6Tc/%3Fs%3D200%26v%3D4/https/avatars.githubusercontent.com/u/9919?width=80&height=80"
        )
        embed.set_footer(text="run !github <subcommand>")

        await ctx.send(embed=embed)

    @github.command(aliases=["find"], description="Get a github user info.")
    async def user(self, ctx, *, user_name: str) -> None:
        async with self.bot.session.get(
            f"https://api.github.com/users/{user_name}"
        ) as res_:
            res = await res_.json()

            if res_.status == 404:
                return await ctx.send(
                    embed=discord.Embed(
                        description="User not found: `{}`".format(user_name),
                        color=discord.Colour.red(),
                    )
                )

        embed = discord.Embed(
            title=res["login"],
            url="https://github.com/{}/".format(user_name),
            description=f"❯ github id: {res['id']}\n"
            f"❯ public repos: {res['public_repos']}\n"
            f"❯ public gists: {res['public_gists']}\n",
            color=0x2F3136,
        )
        embed.set_thumbnail(url=res["avatar_url"])
        embed.add_field(
            name="Other informations:",
            value=f"- followers: {res['followers']}\n"
            f"- following: {res['following']}\n"
            f"- created at: {parse(res['created_at']).strftime('%d/%m/%y %H:%M')}\n"
            f"- updated at: {parse(res['updated_at']).strftime('%d/%m/%y %H:%M')}\n"
            f"- bio: {res['bio']}",
        )
        await ctx.send(embed=embed)

    @github.command(
        aliases=["repo"], description="Search github for a specific repository."
    )
    async def repository(self, ctx, repo_name: str):
        if len(repo_name.split("/")) != 2:
            return await ctx.send(
                embed=discord.Embed(
                    description="that's not a valid repository, please follow this format: `username/repository`",
                    color=discord.Colour.red(),
                )
            )

        async with self.bot.session.get(
            f"https://api.github.com/repos/{repo_name.split('/')[0]}/{repo_name.split('/')[1]}"
        ) as res_:
            res = await res_.json()
            if res_.status == 404:
                return await ctx.send(
                    embed=discord.Embed(
                        description="Repository not found: `{}`".format(repo_name),
                        color=0x2F3136,
                    )
                )

        license_ = res.get("license")
        if license_:
            license_ = license_.get("key")

        embed = discord.Embed(
            title=res.get("full_name"),
            url=res.get("html_url"),
            description=f"❯ github id: {res.get('id')}\n"
            f"❯ description: {res.get('description')}\n"
            f"❯ homepage: {res.get('homepage')}\n"
            f"❯ license: {license_}\n",
            color=0x2F3136,
        )
        embed.set_thumbnail(url=res.get("owner").get("avatar_url"))
        embed.add_field(
            name="Other informations:",
            value=f"- created at: {parse(res['created_at']).strftime('%d/%m/%y %H:%M')}\n"
            f"- updated at: {parse(res['updated_at']).strftime('%d/%m/%y %H:%M')}\n"
            f"- pushed at: {parse(res['pushed_at']).strftime('%d/%m/%y %H:%M')}\n"
            f"- language: {res['language']}\n",
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(search(bot))
