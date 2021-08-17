from utils.functions import get_group_help, get_divmod
from utils.constants import General
from discord.ext import commands
from dateutil.parser import parse
from bot import Bot, CustomContext
from youtubesearchpython import (
    VideosSearch,
)
from utils.converters import Limit
import discord
from utils.errors import ProcessError


statuses = {
    400: "Response status code indicates that the server cannot or will not process the request",
    401: "The request has not been applied because it lacks valid authentication credentials for the target resource. This is from our side, feel free to report!",
    403: "The request is forbidden from this action from our side. Feel free to report so we can fix it!",
    404: "Couldn't find any match from these credentials.",
    429: "We are being rate limited.",
    500: "The server encountered an unexpected condition that prevented it from fulfilling the request.",
}


class search(commands.Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.statuses = statuses
        self.bad_status = "Couldn't fetch data, returned status: {status}"
        self.not_found = "Couldn't find any mathces to: {query}"
        self.stackoverflow_url = "https://api.stackexchange.com/2.2/search/advanced"
        self.realpython_url = "https://realpython.com/search/api/v1/?"
        self.realpython_basic_url = "https://realpython.com{url}"
        self.github_api = "https://api.github.com"
        self.lyrics_api = "https://some-random-api.ml/lyrics?title={title}"
        self.pypi_api = "https://pypi.org/pypi/{package}/json"

    @commands.command(
        aliases=["yt"],
        description="Sends the first 10 videos that matches the search query",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def youtube(
        self, ctx: CustomContext, *, search_query: Limit(char_limit=75)
    ) -> None:
        search_result = VideosSearch(
            search_query, limit=10
        )
        search_result = search_result.result()
        search_result = search_result["result"]

        if len(search_result) > 10:
            search_result = search_result[:10]

        if len(search_result) <= 0:
            return await ctx.send(
                embed=discord.Embed(
                    description=f"No result matches `{search_query}`",
                    color=discord.Colour.red(),
                )
            )  

        embed_description = ""

        for result in search_result:
            if result["type"] == "video":
                video_title = result["title"][:30]
                video_title += "..." if len(result["title"]) > 30 else ""
                video_link = result["link"]

                embed_description += "➥ [{}]({})".format(
                    video_title, video_link
                )
                embed_description += (
                    " - {}\n".format(result["duration"]) if result["duration"] else "\n"
                )

        embed = discord.Embed(
            title="Search results - Youtube",
            description=embed_description,
            color=0x2F3136,
            url="https://www.youtube.com/results?search_query={}".format(
                "+".join(search_query.split(" "))
            ),
        )

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, ignore_extra=False)
    async def github(self, ctx: CustomContext) -> None:
        await get_group_help(ctx=ctx, group=ctx.command)

    @github.command(name="user", description="Shows info about github user.")
    async def github_user(self, ctx: CustomContext, *, name: Limit(char_limit=50)):
        async with self.bot.session.get(
            url=f"{self.github_api}/users/{name}"
        ) as response:
            data = await response.json(content_type=None)
            if response.status != 200:
                message = self.statuses.get(response.status) or self.bad_status.format(
                    status=response.status
                )
                if data.get("retry_after"):
                    days, hours, minutes, seconds = get_divmod(
                        int(message.get("retry_after"))
                    )
                    message += (
                        f"Retry after: {days}d, {hours}h, {minutes}m and {seconds}s."
                    )

                raise ProcessError(message)
        login = data.get("login")
        user_id = data.get("id")
        avatar_url = data.get("avatar_url")
        url = data.get("html_url")
        bio = data.get("bio") or "None."
        repos = data.get("public_repos")
        gists = data.get("public_gists")
        followers = data.get("followers")
        following = data.get("following")
        created_at_time = data.get("created_at")
        updated_at_time = data.get("updated_at")
        created_at = discord.utils.format_dt(parse(created_at_time), style="F")
        updated_at = discord.utils.format_dt(parse(updated_at_time), style="F")
        description = f"**User id:** {user_id}\n**Bio:** {bio}\n**Public repos:** {repos}\n**Public gists:** {gists}\n**Followers:** {followers}\n**Following:** {following}\n**Created at:** {created_at}\n**Updated at:** {updated_at}"
        embed = discord.Embed(
            title="Github user info.",
            description=description,
            color=discord.Colour.blurple(),
        )
        embed.set_author(name=login, url=url, icon_url=avatar_url)
        embed.set_thumbnail(url=General.github_icon)
        await ctx.send(embed=embed)

    @github.command(
        name="repo",
        description="Shows info about a specific repo.",
        aliases=["repository"],
    )
    async def github_repo(self, ctx: CustomContext, *, query: Limit(char_limit=100)):
        if query.count("/") != 1:
            raise ProcessError(
                f"Invalid input. Please make sure this is the format you use: USERNAME/REPONAME"
            )
        async with self.bot.session.get(
            url=f"{self.github_api}/repos/{query}"
        ) as response:
            data = await response.json(content_type=None)
            if response.status != 200:
                message = self.statuses.get(response.status) or self.bad_status.format(
                    status=response.status
                )
                if data.get("retry_after"):
                    days, hours, minutes, seconds = get_divmod(
                        int(message.get("retry_after"))
                    )
                    message += (
                        f"Retry after: {days}d, {hours}h, {minutes}m and {seconds}s."
                    )

                raise ProcessError(message)
            repo_id = data.get("id")
            full_name = data.get("full_name")
            owner_url = data.get("owner").get("avatar_url")
            repo_url = data.get("html_url")
            repo_description = data.get("description")
            is_fork = data.get("fork")
            created_at = discord.utils.format_dt(
                parse(data.get("created_at")), style="F"
            )
            updated_at = discord.utils.format_dt(
                parse(data.get("updated_at")), style="F"
            )
            pushed_at = discord.utils.format_dt(parse(data.get("pushed_at")), style="F")
            language = data.get("language")
            forks = data.get("forks_count")
            opened_issue = data.get("open_issues_count")
            license = data.get("license") or None
            license = license.get("name") if license else None
            default_branch = data.get("default_branch")
            add = f"\n**Updated at:** {updated_at}\n**Pushed at:** {pushed_at}\n**Language:** {language}\n**Forks:** {forks}\n**Opened_issue:** {opened_issue}"
            description = f"**Repo id:** {repo_id}\n**Description:** {repo_description}\n**Is fork:** {is_fork}\n**Created at:** {created_at}"
            add2 = f"\n**License:** {license}\n**Default branch:** {default_branch}"
            description += add
            description += add2
            embed = discord.Embed(
                title="Repository info.",
                description=description,
                color=discord.Colour.blurple(),
            )
            embed.set_author(name=full_name, url=repo_url, icon_url=owner_url)
            await ctx.send(embed=embed)
            

def setup(bot):
    bot.add_cog(search(bot))
