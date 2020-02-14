"""Main module

Main program, bot is being ran by bot.py

"""
import discord
from discord.ext import commands
import constants
import asyncio
from asyncdb import AsyncDb
from botcontroller import BotController
import cogs.dm.base as base
import cogs.dm.dev as dev


async def run(loop):
    """
    Main coroutine that is being ran when the program starts
    """
    db = AsyncDb(loop)
    await db.initConnection()
    controller = BotController(db)
    bot = Bot(command_prefix=constants.BOT_COMMAND_PREFIX, description=constants.BOT_DESC, controller=controller)

    bot.add_cog(base.BaseCog(bot))
    bot.add_cog(dev.DevCog(bot))
    try:
        await bot.start(constants.TOKEN)
    except KeyboardInterrupt:
        await bot.logout()

class Bot(commands.Bot):
    """
    Subclass of commands.Bot class which is modified so it can accept
    our controller and store it inside the property variable.
    Later, after adding cogs to this bot class we can reference the controller inside the cog class.
    """
    def __init__(self, **kwargs):
        super().__init__(
            command_prefix = kwargs.pop("command_prefix"),
            description = kwargs.pop("description")
        )
        self.controller = kwargs.pop("controller")

    async def on_ready(self):
        print(f"\nLogged in as: {self.user.name} - {self.user.id}\n")

loop = asyncio.get_event_loop()
loop.run_until_complete(run(loop))