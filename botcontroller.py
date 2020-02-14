"""
Controller class that has all the methods which are required by the bot to perform its functionality.
All methods are concurrent.
The main part of the controller is the database instance property.
"""
import emailhandler
from entities.record import Record
import asyncdb
import aiosmtplib
import tokengenerator
import re
from pymysql.err import IntegrityError
from constants import EMAIL_REGEX
from log import getLogger

"""
Exceptions which the controller raises
"""
class InvalidEmailException(Exception):
    pass
class UsernameExistsException(Exception):
    def __init__(self, message, emailExists: bool, senderUserPending: bool, emailUserPending: bool):
        super().__init__(message)
        self.emailExists = emailExists
        self.senderUserPending = senderUserPending
        self.emailUserPending = emailUserPending

class UsernameNonExistentException(Exception):
    def __init__(self, message, emailExists: bool, emailUserPending: bool):
        super().__init__(message)
        self.emailExists = emailExists
        self.emailUserPending = emailUserPending
    
class ValidationException(Exception):
    pass
class DeregisterException(Exception):
    pass
class BlacklistException(Exception):
    pass
class EmailException(Exception):
    pass

class BotController:
    def __init__(self, db: asyncdb.AsyncDb):
        self.dbInstance = db

    async def userNameExists(self, user: Record) -> bool:
        ret = await self.dbInstance.userNameExists(user)
        await self.dbInstance.commit()
        return ret

    async def emailExists(self, user: Record) -> bool:
        ret = await self.dbInstance.emailExists(user)
        await self.dbInstance.commit()
        return ret

    async def isRegistered(self, user: Record) -> bool:
        ret = await self.dbInstance.isRegistered(user)
        await self.dbInstance.commit()
        return ret

    async def isPending(self, user: Record) -> bool:
        ret = await self.dbInstance.isPending(user)
        await self.dbInstance.commit()
        return ret

    async def setPending(self, user: Record):
        ret = await self.dbInstance.setPending(user)
        await self.dbInstance.commit()
        return ret
    
    async def getToken(self, user: Record) -> str:
        ret = await self.dbInstance.getToken(user)
        await self.dbInstance.commit()
        return ret
    
    async def getRecords(self, record: Record):
        #Discordid, Email, Token, Time, Type, Status
        tmp = await self.dbInstance.getRecords(record)
        ret = []
        for x in tmp:
            discordid, email, token, time, _type, status = x
            r = Record(discordid=discordid, email=email, token=token, time=time, _type=_type, status=status)
            ret.append(r)
        await self.dbInstance.commit()
        return ret

    async def helperInsertRecord(self, user: Record):
        token = tokengenerator.getToken()
        user.token = token
        await self.dbInstance.insertRecord(user)
        try:
            await emailhandler.sendToken([user.email], token)
        except Exception as e:
            raise EmailException(e)
    
    async def getRoleForUser(self, user: Record):
        ret = await self.dbInstance.getRoleForUser(user)
        await self.dbInstance.commit()
        return ret

    async def register(self, user: Record):
        if not (await self.isEmailValid(user.email)):
            raise InvalidEmailException()
        
        userExists = await self.userNameExists(Record(discordid=user.discordid))
        emailExists = await self.emailExists(Record(email=user.email))
        if userExists:
            isPendingSenderUser = await self.isPending(Record(discordid=user.discordid))
            strPendingSender = "pending" if isPendingSenderUser else "registered"
            if emailExists:
                isPendingEmailUser = await self.isPending(Record(email=user.email))
                strPendingEmailUser = "pending" if isPendingEmailUser else "registered"
                if isPendingSenderUser and isPendingEmailUser:
                    #delete both the record which shares the discord id (and is pending) and the other record which shares the email (and is pending)
                    await self.dbInstance.deleteRecord(Record(discordid=user.discordid))
                    await self.dbInstance.deleteRecord(Record(email=user.email))
                    try:
                        await self.helperInsertRecord(user)
                    except EmailException as e:
                        await self.dbInstance.rollback()
                        raise e
                    await self.dbInstance.commit()
                raise UsernameExistsException(f"Register error: Discord ID {user.discordid} exists, state '{strPendingSender}' | email {user.email} exists, state '{strPendingEmailUser}'",  True, isPendingSenderUser, isPendingEmailUser)

            else: #user exists, but email record doesn't exist
                if isPendingSenderUser:
                    await self.dbInstance.deleteRecord(Record(discordid=user.discordid))
                    try:
                        await self.helperInsertRecord(user)
                    except EmailException as e:
                        await self.dbInstance.rollback()
                        raise e
                    await self.dbInstance.commit()
                raise UsernameExistsException(f"Register error: Discord ID {user.discordid} exists, state '{strPendingSender}' | email {user.email} doesn't exist", False, isPendingSenderUser, None)
        
        else: #user doesn't exist
            isPendingEmailUser = await self.isPending(Record(email=user.email))
            strPendingEmailUser = "pending" if isPendingEmailUser else "registered"
            if emailExists:
                if isPendingEmailUser:
                    await self.dbInstance.deleteRecord(Record(email=user.email))
                    try:
                        await self.helperInsertRecord(user)
                    except EmailException as e:
                        await self.dbInstance.rollback()
                        raise e
                    await self.dbInstance.commit()
                raise UsernameNonExistentException(f"Register error: Discord ID {user.discordid} doesn't exists | email {user.email} exists", True, isPendingEmailUser)
            
            else: #user doesn't exist, email doesn't exist. Everything is fine
                try:
                    await self.helperInsertRecord(user)
                except EmailException as e:
                    await self.dbInstance.rollback()
                    raise e
                await self.dbInstance.commit()

    async def validate(self, user: Record):
        if await self.userNameExists(user) and await self.isPending(user):
            if await self.getToken(user) == user.token:
                await self.dbInstance.setRegistered(user)
                return
            raise ValidationException("Error: wrong token by user {}".format(user.discordid))
        raise ValidationException("Error with validating ID {}. User doesn't exist in database or is already in 'registered' state.".format(user.discordid))

    async def isEmailValid(self, email: str) -> bool:
        check = await self.isInBlacklist(email)
        if check:
            getLogger(__name__).warning("A blacklisted email {} tried to register.".format(email))
        return re.search(EMAIL_REGEX, email) and not check

    async def deregister(self, user: Record):
        if await self.userNameExists(user) and await self.isRegistered(user):
            cnt = await self.dbInstance.deleteRecord(user)
            if cnt < 1:
                raise Exception("deregister() error: deleteRecord() database call deleted nothing.")
        else:
            raise DeregisterException("User with ID {} isn't registered.".format(user.discordid))
        

    async def addToBlacklist(self, *emails: str) -> str:
        try:
            await self.dbInstance.insertIntoBlacklist(*emails)
            await self.dbInstance.commit()

        except IntegrityError:
            raise BlacklistException("addToBlacklist() error: email already in blacklist.")

    async def removeFromBlacklist(self, *emails: str):
        cnt = await self.dbInstance.deleteFromBlacklist(*emails)
        await self.dbInstance.commit()
        if cnt < 1:
            raise BlacklistException("removeFromBlacklist() error: removeFromBlacklist() database call deleted nothing.")

    async def getBlacklist(self):
        ret = await self.dbInstance.getBlacklist()
        await self.dbInstance.commit()
        tmp = [e for e, in ret]
        return tmp

    async def isInBlacklist(self, email: str) -> bool:
        ret = await self.dbInstance.isInBlacklist(email)
        await self.dbInstance.commit()
        return ret

#driver test
if __name__ == "__main__":
    pass