"""COG Class
Contains commands for the bot, intended to be used by privileged users,
defined in the list DEVELOPER_ROLE_NAMES in constants.py
"""
import discord
from discord.ext import commands
import constants
from botcontroller import BlacklistException
from log import getLogger

class DevCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        ignored = (commands.errors.PrivateMessageOnly, commands.CommandNotFound, commands.UserInputError)
        
        if isinstance(error, ignored):
            return

    async def cog_check(self, ctx: commands.Context):
        guild = self.bot.get_guild(constants.SERVERID)
        member = discord.utils.get(guild.members, id=ctx.author.id)
        roles = []
        for role in constants.DEVELOPER_ROLE_NAMES:
            tmp = discord.utils.get(guild.roles, name=role)
            if tmp is not None:
                roles.append(tmp)
        if member is None or len(roles) == 0:
            return False
        for memberRole in member.roles:
            for role in roles:
                if memberRole == role:
                    return True
        return False


    @commands.command(pass_context=True)
    @commands.dm_only()
    async def stop(self, ctx: commands.Context):
        await self.bot.logout()


    @commands.command(pass_context=True)
    @commands.dm_only()
    async def postasbot(self, ctx: commands.Context, *, msg: str):
        guild = self.bot.get_guild(constants.SERVERID)
        botChannel = discord.utils.get(guild.channels, name=constants.BOT_CHANNEL)
        await botChannel.send(msg)


    @commands.command(pass_context=True)
    @commands.dm_only()
    async def postasbotdesc(self, ctx: commands.Context):
        msg = '''**How to complete the registration:**
Send commands to bot (right click on my name -> Message) over DM.
Commands are:
```{style}
{prefix}register <{roles}> <email>
{prefix}validate <TOKEN>
{prefix}deregister```

**Acceptable email address:**
- PLACEHOLDER

**Rules:**
- PLACEHOLDER

**Instructions:**
- PLACEHOLDER

In case of any problems, contact:
{contact0}'''.format(style=constants.CODE_STYLE, prefix=constants.BOT_COMMAND_PREFIX, contact0=constants.ADMIN_USER, roles="/".join(constants.REGISTERED_ROLE_NAMES))
        guild = self.bot.get_guild(constants.SERVERID)
        botChannel = discord.utils.get(guild.channels, name=constants.BOT_CHANNEL)
        await botChannel.send(msg)

    @commands.command(pass_context=True)
    @commands.dm_only()
    async def blacklist(self, ctx: commands.Context, *args):
        upute = '''**Usage:**
```fix
{prefix}blacklist <cmd> <arg>

<cmd>:
get - print the blacklist
add <...email(s)> - add one or more emails to the blacklist, separated by space character
remove <...email(s)> - remove one or more emails from the blacklist, separated by space character
check <email> - check if the email is in blacklist```'''.format(prefix=constants.BOT_COMMAND_PREFIX)

        if len(args) == 0:
            await ctx.channel.send(upute)
            return

        if args[0] == "get":
            if len(args) != 1:
                await ctx.channel.send(upute)
                return
            blacklist = await self.bot.controller.getBlacklist()
            if len(blacklist) == 0:
                await ctx.channel.send("Blacklist empty.")
                return
            lenSum = 0
            data = []
            for row in blacklist:
                lenSum += len(row)
                data.append(row)
                if lenSum > 1600:
                    await ctx.channel.send("\n".join(data))
                    data = []
                    lenSum = 0
            if len(data) > 0:
                await ctx.channel.send("\n".join(data))
            return

        elif args[0] == "add":
            if len(args) < 2:
                await ctx.channel.send(upute)
                return

            newArgs = args[1:]
            try:
                await self.bot.controller.addToBlacklist(*newArgs)
                await ctx.channel.send("Emails successfully added to blacklist.")
            
            except BlacklistException as e:
                getLogger(__name__).error(str(e))
                await ctx.channel.send("Error: email already in blacklist!")

            except Exception as e:
                getLogger(__name__).error(str(e))
                await ctx.channel.send("There is an error with the bot. Contact admin: {}".format(constants.ADMIN_USER))
            return

        elif args[0] == "remove":
            if len(args) < 2:
                await ctx.channel.send(upute)
                return

            newArgs = args[1:]
            try:
                await self.bot.controller.removeFromBlacklist(*newArgs)
                await ctx.channel.send("Emails successfully removed from blacklist.")

            except BlacklistException as e:
                getLogger(__name__).error(str(e))
                await ctx.channel.send("Error: email doesn't exist in blacklist. Nothing removed.")

            except Exception as e:
                getLogger(__name__).error(str(e))
                await ctx.channel.send("There is an error with the bot. Contact admin: {}".format(constants.ADMIN_USER))
            return

        elif args[0] == "check":
            if len(args) != 2:
                await ctx.channel.send(upute)
                return

            try:
                check = await self.bot.controller.isInBlacklist(args[1])
                await ctx.channel.send("Email {} {} in blacklist.".format(args[1], "is" if check else "is not"))

            except Exception as e:
                getLogger(__name__).error(str(e))
                await ctx.channel.send("There is an error with the bot. Contact admin: {}".format(constants.ADMIN_USER))
            return

def setup(bot):
    bot.add_cog(DevCog(bot))