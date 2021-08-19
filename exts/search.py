from utils.buttons import Paginator
from utils.functions import get_group_help, get_divmod
from utils.constants import Colours, General
from utils.converters import Limit, SourceConverter
from utils.errors import ProcessError
from discord.ext import commands
from dateutil.parser import parse
from bot import Bot, CustomContext
from youtubesearchpython import (
    VideosSearch,
)
import discord


statuses = {
    400: "Response status code indicates that the server cannot or will not process the request",
    401: "The request has not been applied because it lacks valid authentication credentials for the target resource. This is from our side, feel free to report!",
    403: "The request is forbidden from this action from our side. Feel free to report so we can fix it!",
    404: "Couldn't find any match from these credentials.",
    429: "We are being rate limited.",
    500: "The server encountered an unexpected condition that prevented it from fulfilling the request.",
}


class Search(commands.Cog):
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
        search_result = VideosSearch(search_query, limit=10)
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
                video_title = result["title"][:30].replace("[", "").replace("]", "")
                video_title += "..." if len(result["title"]) > 30 else ""
                video_link = result["link"]

                embed_description += "➥ [{}]({})".format(video_title, video_link)
                embed_description += (
                    " - {}\n".format(result["duration"]) if result["duration"] else "\n"
                )

        embed = discord.Embed(
            title="Search results - Youtube",
            description=embed_description,
            color=discord.Colour.blurple(),
            url="https://www.youtube.com/results?search_query={}".format(
                "+".join(search_query.split(" "))
            ),
        )

        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True, ignore_extra=False, aliases=["git"])
    async def github(self, ctx: CustomContext) -> None:
        await get_group_help(ctx, ctx.command)

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
        created_at = discord.utils.format_dt(parse(created_at_time), style="f")
        updated_at = discord.utils.format_dt(parse(updated_at_time), style="f")
        embed = discord.Embed(
            title="Github user info.",
            description=f"➥ User ID: {user_id}\n"
            f"➥ Bio: {bio}\n"
            f"➥ followers: {followers}\n"
            f"➥ following: {following}\n",
            color=discord.Colour.blurple(),
        )
        embed.add_field(
            name="Other informations:",
            value=f"> Public repos: {repos}\n"
            f"> Public gists: {gists}\n"
            f"> created at: {created_at}\n"
            f"> updated at: {updated_at}\n",
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

            repo_description = (
                data.get("description")[:50] if data.get("description") else "None"
            )
            repo_description += "..." if len(repo_description) > 50 else ""

            created_at = discord.utils.format_dt(
                parse(data.get("created_at")), style="f"
            )
            updated_at = discord.utils.format_dt(
                parse(data.get("updated_at")), style="f"
            )
            pushed_at = discord.utils.format_dt(parse(data.get("pushed_at")), style="f")
            license = data.get("license")
            license = license.get("name") if license else None
            embed = discord.Embed(
                title=data.get("full_name"),
                description=f"➥ Repository ID: {data.get('id')}\n"
                f"➥ Description: {repo_description}\n"
                f"➥ Homepage: {data.get('homepage') if not data.get('homepage') == '' else None}\n"
                f"➥ Language: {data.get('language')}\n",
                url=data.get("html_url"),
                color=discord.Colour.blurple(),
            )
            embed.add_field(
                name="Other informations:",
                value=f"> Open issues: {data.get('open_issues')}\n"
                f"> Watched by: {data.get('watchers')} users\n"
                f"> Is fork: {data.get('fork')}\n"
                f"> Forks: {data.get('forks')}\n",
            )
            embed.add_field(
                name="_ _",
                value=f"> Created at: {created_at}\n"
                f"> Updated at: {updated_at}\n"
                f"> Pushed at: {pushed_at}\n"
                f"> Default branch: {data.get('default_branch')}\n",
            )
            embed.set_author(
                name=data["owner"]["login"],
                url=data["owner"]["html_url"],
                icon_url=data["owner"]["avatar_url"],
            )
            embed.set_footer(text=license)
            await ctx.send(embed=embed)

    @commands.command(description="Searches for source data.")
    async def source(self, ctx: CustomContext, *, source_item: SourceConverter):
        print(source_item)

        async def check(interaction: discord.Interaction):
            return interaction.user.id == ctx.author.id

        paginator = Paginator(ctx=ctx, embeds=[], timeout=20.0, check=check)
        for name, data in source_item.items():
            repo_link = data.get("repo_link")
            description = f"[Click here]({repo_link}) for source link."
            embed = discord.Embed(
                title=name, description=description, color=Colours.invisible
            )
            embed.set_thumbnail(url=General.github_icon)
            paginator.add_embed(embed)

        await paginator.run()


def setup(bot: Bot):
    bot.add_cog(Search(bot))
