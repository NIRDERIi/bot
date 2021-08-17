import discord
from bot import CustomContext
import typing
import contextlib
from utils.constants import Emojis


class Paginator:

    """
    Button paginator set-up
    """

    def __init__(
        self,
        ctx: CustomContext,
        embeds: typing.List[discord.Embed],
        *,
        timeout: typing.Optional[float] = None,
        check: typing.Callable[..., bool] = None
    ) -> None:
        self.ctx = ctx
        self.embeds = embeds
        self.timeout = timeout
        self.check = check
        self.dict = {}
        self.counter = 0

    async def run(self) -> None:
        if len(self.embeds) == 1:
            await self.ctx.send(embed=self.embeds[0])
            return
        for embed in self.embeds:
            self.counter += 1
            self.dict[self.counter] = embed

        view = ButtonPaginator(
            embeds=self.embeds,
            dct=self.dict,
            ctx=self.ctx,
            timeout=self.timeout,
            check=self.check,
        )
        await self.ctx.send(embed=self.embeds[0], view=view)
        await view.wait()

    def add_embed(self, embed: discord.Embed):
        self.embeds.append(embed)


class ButtonPaginator(discord.ui.View):
    def __init__(
        self,
        *,
        embeds: typing.List[discord.Embed],
        dct: dict,
        ctx: CustomContext,
        timeout: typing.Optional[float],
        check: typing.Callable[..., bool] = None
    ) -> None:

        super().__init__(timeout=timeout)
        self.ctx = ctx
        if check:
            self.interaction_check = check
        self.value = None
        self.dct = dct
        self.page = 1
        self.embeds = embeds

    @discord.ui.button(emoji=Emojis.double_left_arrows)
    async def first_page_get(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.page = 1
        with contextlib.suppress(discord.HTTPException, discord.NotFound):
            await interaction.response.edit_message(embed=self.dct.get(self.page))

    @discord.ui.button(emoji=Emojis.left_arrow)
    async def get_page_down(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        page_get = self.page - 1
        embed = self.dct.get(page_get)
        if embed:
            self.page -= 1
            with contextlib.suppress(discord.HTTPException, discord.NotFound):
                await interaction.response.edit_message(embed=self.dct.get(self.page))

    @discord.ui.button(emoji=Emojis.garbage)
    async def stop_interaction(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        with contextlib.suppress(discord.HTTPException, discord.NotFound):
            await interaction.message.delete()

    @discord.ui.button(emoji=Emojis.right_arrow)
    async def get_page_up(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        page_get = self.page + 1
        embed = self.dct.get(page_get)
        if embed:
            self.page += 1
            with contextlib.suppress(discord.HTTPException, discord.NotFound):
                await interaction.response.edit_message(embed=self.dct.get(self.page))

    @discord.ui.button(emoji=Emojis.double_right_arrows)
    async def last_page_get(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.page = len(self.embeds)
        with contextlib.suppress(discord.HTTPException, discord.NotFound):
            await interaction.response.edit_message(embed=self.dct.get(self.page))


class ConfirmButtonBuild(discord.ui.View):
    def __init__(
        self,
        *,
        timeout: typing.Optional[float],
        ctx: CustomContext,
        check: typing.Callable[..., bool] = None
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        if check:
            self.interaction_check = check
        self.value = None

    @discord.ui.button(
        label="Approve", style=discord.ButtonStyle.blurple, emoji=Emojis.custom_approval
    )
    async def approval(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = True
        self.stop()

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.blurple,
        emoji=Emojis.custom_denial,
    )
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        self.value = False
        self.stop()
