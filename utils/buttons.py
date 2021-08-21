from bot import CustomContext
from utils.constants import Emojis
from utils.errors import ProcessError
import discord
import typing
import contextlib


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
        check: typing.Callable[..., bool] = None,
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
        check: typing.Callable[..., bool] = None,
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
        check: typing.Callable[..., bool] = None,
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
    async def cancel(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = False
        self.stop()


class Calculator:
    def __init__(
        self,
        ctx: CustomContext,
        *,
        check: typing.Callable[..., bool] = None,
        timeout: typing.Optional[float] = None,
    ):

        self.ctx = ctx
        if not check:

            async def check(interaction: discord.Interaction):
                return interaction.user.id == self.ctx.author.id

        self.check = check
        self.timeout = timeout

    async def run(self, content: str = None, *, embed: discord.Embed = None):

        """Calling buttons class."""
        button_calculator = ButtonCalculator(
            self.ctx, embed, self.check, timeout=self.timeout
        )
        await self.ctx.send(content=content, embed=embed, view=button_calculator)
        return button_calculator


class ButtonCalculator(discord.ui.View):
    def __init__(
        self,
        ctx: CustomContext,
        embed: discord.Embed,
        check: typing.Callable[..., bool],
        *,
        timeout: typing.Optional[float] = None,
    ):

        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.check = check
        self.expression = ""
        self.base_embed = embed
        self.base_embed.description = "```>```"

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        bool_check = await self.check(interaction=interaction)
        if not bool_check:
            await interaction.response.send_message(content='This is not your calculator session, please make your own.', ephemeral=True)
            return False
        return True

    async def set_embed(
        self, interaction: discord.Interaction, description: str = None
    ):  # Sets an embed with description inside ```
        description = description or self.expression
        description = f"```> {description}```" if description else "```>```"
        self.base_embed.description = f"{description}"
        await interaction.response.edit_message(embed=self.base_embed)

    def len_check(self):
        if len(self.expression) > 25:
            self.stop()
            raise ProcessError("The expression can't be longer than 15 chars.")

    @discord.ui.button(label="C", row=0)
    async def clear(self, button: discord.Button, interaction: discord.Interaction):
        self.expression = ""
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="(", row=0)
    async def add_start_brace(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label=")", row=0)
    async def add_ending_brace(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="%", row=0, style=discord.ButtonStyle.primary)
    async def add_precentage(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="1", row=1)
    async def one(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="2", row=1)
    async def two(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="3", row=1)
    async def three(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="*", row=1, style=discord.ButtonStyle.primary)
    async def multiplication(
        self, button: discord.Button, interaction: discord.Interaction
    ):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="4", row=2)
    async def four(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="5", row=2)
    async def five(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="6", row=2)
    async def six(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="-", row=2, style=discord.ButtonStyle.primary)
    async def minus(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="7", row=3)
    async def seven(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="8", row=3)
    async def eight(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="9", row=3)
    async def nine(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="+", row=3, style=discord.ButtonStyle.primary)
    async def plus(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="Close", row=4, style=discord.ButtonStyle.red)
    async def Close(self, button: discord.Button, interaction: discord.Interaction):
        await interaction.message.delete()

    @discord.ui.button(label="0", row=4)
    async def zero(self, button: discord.Button, interaction: discord.Interaction):
        self.expression += f"{button.label}"
        self.len_check()
        await self.set_embed(interaction=interaction)

    @discord.ui.button(label="=", row=4, style=discord.ButtonStyle.green)
    async def Equals(self, button: discord.Button, interaction: discord.Interaction):
        output = ""
        try:
            output = eval(self.expression)
        except SyntaxError:
            output = "Invalid expression syntax."
        self.base_embed.set_footer(text="Calculator closed.")
        await self.set_embed(interaction=interaction, description=f'{self.expression} = {output}')
        self.stop()

        await interaction.message.edit(view=None)

    @discord.ui.button(emoji=Emojis.backspace, row=4)
    async def backspace(self, button: discord.Button, interaction: discord.Interaction):
        self.expression = self.expression[:-1]
        await self.set_embed(interaction=interaction)