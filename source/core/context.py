from ..utilities import constants, errors
from discord.ext import commands
import discord
import typing


class ConfirmButtonBuild(discord.ui.View):
    def __init__(
        self,
        *,
        timeout: typing.Optional[float],
        ctx,
        check: typing.Callable[..., bool] = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self.ctx = ctx
        if check:
            self.interaction_check = check
        self.value = None

    @discord.ui.button(
        label="Approve", style=discord.ButtonStyle.blurple, emoji=constants.Emojis.custom_approval
    )
    async def approval(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = True
        self.stop()

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.blurple,
        emoji=constants.Emojis.custom_denial,
    )
    async def cancel(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ) -> None:
        self.value = False
        self.stop()


class CustomContext(commands.Context):
    async def send_confirm(
        self, *args, check: typing.Callable[..., bool] = None, **kwargs
    ) -> typing.Tuple[discord.Message, typing.Optional[discord.ui.View]]:
        if not kwargs.get("view"):
            view = ConfirmButtonBuild(
                timeout=20, ctx=self, check=check
            )
            message = await self.send(*args, **kwargs, view=view)
            await view.wait()
            if view.value is None:
                raise errors.ProcessError("Timed out!")

            return view, message
        else:
            return super().send(*args, **kwargs)