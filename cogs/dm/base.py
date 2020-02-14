"""COG Class
Contains commands for the bot, intended to be used by everyone, over DM
"""
import discord
from discord.ext import commands
from discord import Member, Role
from botcontroller import (
    InvalidEmailException,
    UsernameExistsException,
    UsernameNonExistentException,
    ValidationException, 
    DeregisterException,
    BlacklistException,
    EmailException
    )
from entities.record import Record
import constants
from log import getLogger
from util import getFromListCaseIgnored

class BaseCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError):
        ignored = (commands.errors.PrivateMessageOnly, commands.CommandNotFound, commands.UserInputError)
        
        if isinstance(error, ignored):
            return
    
    @commands.command()
    @commands.dm_only()
    async def register(self, ctx: commands.Context, _type: str, email: str):
        _type = getFromListCaseIgnored(_type, constants.REGISTERED_ROLE_NAMES)
        if _type is None:
            raise commands.errors.BadArgument("Bad register command argument: invalid role name.")

        record = Record(discordid=ctx.author.id, email=email, _type=_type)
        try:
            await self.bot.controller.register(record)
            await ctx.channel.send("Email sent!")

        except InvalidEmailException as e:
            getLogger(__name__).warning(str(e))
            await ctx.channel.send("Email {} doesn't meet our requirements.\nCheck the server registration rules.".format(email))

        except UsernameExistsException as e:
            getLogger(__name__).warning(str(e))
            firstScenarioToResend = e.emailExists and e.emailUserPending and e.senderUserPending
            secondScenarioToResend = not e.emailExists and e.senderUserPending
            if not e.senderUserPending:
                await ctx.channel.send("You have already registered!")
            if firstScenarioToResend or secondScenarioToResend:
                await ctx.channel.send("Email sent!\nWarning: you have already tried registering this Discord ID. The old token is now invalid.")

        except UsernameNonExistentException as e:
            getLogger(__name__).warning(str(e))
            if e.emailExists:
                if e.emailUserPending:
                    #This email was pending registration from another user. Hijacking the email...
                    await ctx.channel.send("Email sent!")
                else:
                    await ctx.channel.send("This email belongs to a registered account.")

        except EmailException as e:
            getLogger(__name__).warning(str(e))
            await ctx.channel.send("An error occurred while attempting to send the email.\nTry again later or contact {}.".format(constants.ADMIN_USER))

        except Exception as e:
            getLogger(__name__).error(str(e))
            await ctx.channel.send("There is an error with the bot. Contact admin: {}".format(constants.ADMIN_USER))

    @register.error
    async def register_error_handler(self, ctx, error):
        desc = '''**Usage:**
```{style}
{prefix}register <{roles}> <email>```
**Example:**
```{style}
{prefix}register {roleeg} johndoe@gmail.com```'''.format(style=constants.CODE_STYLE, prefix=constants.BOT_COMMAND_PREFIX, roles="/".join(constants.REGISTERED_ROLE_NAMES), roleeg=constants.REGISTERED_ROLE_NAMES[0])
        await ctx.send(desc)


    @commands.command()
    @commands.dm_only()
    async def validate(self, ctx: commands.Context, token: str):
        record = Record(discordid=ctx.author.id, token=token)
        try:
            guild = self.bot.get_guild(constants.SERVERID)
            member = discord.utils.get(guild.members, id=ctx.author.id)
            roleName = await self.bot.controller.getRoleForUser(Record(discordid=ctx.author.id))
            role = discord.utils.get(guild.roles, name=roleName)

            await self.bot.controller.validate(record)
            try:
                await member.add_roles(role)
                await ctx.channel.send("Your account has been successfully validated.")
                await self.bot.controller.dbInstance.commit()
            except discord.errors.Forbidden:
                await self.bot.controller.dbInstance.rollback()
                await ctx.channel.send("Unable to validate because the bot doesn't have sufficient permissions to give roles. Contact: {}".format(constants.ADMIN_USER))

        except ValidationException as e:
            getLogger(__name__).error(str(e))
            await ctx.channel.send("Validation failed.")

    @validate.error
    async def validate_error_handler(self, ctx: commands.Context, error):
        desc = '''**Usage:**
```{style}
{prefix}validate <TOKEN>```
**Example:**
```{style}
{prefix}validate 123456789abcdefgh```'''.format(style=constants.CODE_STYLE, prefix=constants.BOT_COMMAND_PREFIX)
        await ctx.send(desc)


    @commands.command()
    @commands.dm_only()
    async def deregister(self, ctx: commands.Context):
        record = Record(discordid=ctx.author.id)

        try:
            guild = self.bot.get_guild(constants.SERVERID)
            member = discord.utils.get(guild.members, id=ctx.author.id)
            roleName = await self.bot.controller.getRoleForUser(Record(discordid=ctx.author.id))
            role = discord.utils.get(guild.roles, name=roleName.lower() if roleName is not None else None)

            await self.bot.controller.deregister(record)
            try:
                await member.remove_roles(role)
                await ctx.channel.send("Successfully deregistered.")
                await self.bot.controller.dbInstance.commit()
            except discord.errors.Forbidden:
                await self.bot.controller.dbInstance.rollback()
                await ctx.channel.send("Unable to deregister because the bot doesn't have sufficient permissions to give roles. Contact: {}".format(constants.ADMIN_USER))

        except DeregisterException as e:
            getLogger(__name__).warning(str(e))
            await ctx.channel.send("Your Discord ID has not been registered.")
        
        except Exception as e:
            getLogger(__name__).error(str(e))
            await ctx.channel.send("There is an error with the bot. Contact admin: {}".format(constants.ADMIN_USER))
    
    @deregister.error
    async def deregister_error_handler(self, ctx: commands.Context, error):
        desc = '''**Usage:**
```{style}
{prefix}deregister```'''.format(style=constants.CODE_STYLE, prefix=constants.BOT_COMMAND_PREFIX)
        await ctx.send(desc)

def setup(bot):
    bot.add_cog(BaseCog(bot))