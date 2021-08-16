from bot import Bot

bot = Bot(
    command_prefix="m!",
    help_command=None,
    description="Discord bot developed in discord.py.",
)

bot.run(token=bot.retrieve_token, reconnect=True)
