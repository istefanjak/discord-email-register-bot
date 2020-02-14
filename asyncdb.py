"""Database management module

Module contains AsyncDb class which is responsible for obtaining the connection
with the database.
We are using asyncio module and aiomysql dependency for executing defined database coroutines.
For this project we used MySQL database.
"""
import asyncio
import aiomysql
import constants
from datetime import datetime
from entities.record import Record

class AsyncDb:
    """
    Main AsyncDb class
    After an instance of this class has been constructed, before calling any coroutines, it is important
    to call initConnection() only once, which is responsible for obtaining the connection reference with the database.
    After calling any of the coroutines, it is important to call commit() or rollback(), depending whether we want
    to perform the transaction or not.
    """
    def __init__(self, loop):
        self.loop = loop
        self.connection: aiomysql.Connection = None
    
    def __del__(self):
        if self.connection is not None:
            self.connection.close()

    async def initConnection(self):
        self.connection = await aiomysql.connect(
            host=constants.HOST,
            port=constants.PORT,
            user=constants.USER,
            password=constants.PASS,
            db=constants.DB_NAME,
            loop=self.loop
            )

    async def commit(self):
        await self.connection.commit()

    async def rollback(self):
        await self.connection.rollback()

    
    #util
    async def createDB(self):
        query = "CREATE DATABASE " + constants.DB_NAME
        async with self.connection.cursor() as cursor:
            await cursor.execute(query)
    
    #util
    async def rebuildTable(self):
        queryDrop = "DROP TABLE IF EXISTS {}".format(constants.TABLE_NAME)
        queryCreate = '''CREATE TABLE {table_name} (
            Tokenid int NOT NULL AUTO_INCREMENT,
            Discordid varchar(127) NOT NULL,
            Email varchar(127) NOT NULL,
            Token varchar(64) NOT NULL,
            Time datetime NOT NULL,
            Type enum({vars}),
            Status enum('pending', 'registered'),
            PRIMARY KEY (Tokenid)
        )'''.format(table_name=constants.TABLE_NAME, vars=", ".join(["%s" for x in range(len(constants.REGISTERED_ROLE_NAMES))]))
        async with self.connection.cursor() as cursor:
            await cursor.execute(queryDrop)
            await cursor.execute(queryCreate, tuple(constants.REGISTERED_ROLE_NAMES))

    async def insertRecord(self, record: Record):
        query = "INSERT INTO {} (Discordid, Email, Token, Time, Type, Status) VALUES (%s, %s, %s, now(), %s, 'pending')".format(constants.TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, (record.discordid, record.email, record.token, record._type))

    async def getRecords(self, record: Record):
        params = {}
        query = "SELECT Discordid, Email, Token, Time, Type, Status FROM {} WHERE "
        tmp = []
        if record.discordid:
            tmp.append("Discordid=%(discordid)s")
            params.update(discordid=record.discordid)
        if record.email:
            tmp.append("Email=%(email)s")
            params.update(email=record.email)
        if record.token:
            tmp.append("Token=%(token)s")
            params.update(token=record.token)
        if record.time:
            tmp.append("Time=%(time)s")
            params.update(time=str(record.time))
        if record._type:
            tmp.append("Type=%(_type)s")
            params.update(_type=record._type)
        if record.status:
            tmp.append("Status=%(status)s")
            params.update(status=record.status)
        query += " AND ".join(tmp)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
        return cursor.fetchall().result()


    async def setStatus(self, record: Record, status: str):
        params = {"status": status}
        query = "UPDATE {} SET Status=%(status)s WHERE ".format(constants.TABLE_NAME)
        tmp = []
        if record.discordid:
            tmp.append("Discordid=%(discordid)s")
            params.update(discordid=record.discordid)
        if record.email:
            tmp.append("Email=%(email)s")
            params.update(email=record.email)
        if record.token:
            tmp.append("Token=%(token)s")
            params.update(token=record.token)
        if record.time:
            tmp.append("Time=%(time)s")
            params.update(time=str(record.time))
        if record._type:
            tmp.append("Type=%(_type)s")
            params.update(_type=record._type)
        if record.status:
            tmp.append("Status=%(status)s")
            params.update(status=record.status)
        query += " AND ".join(tmp)

        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            rowcnt = cursor.rowcount
        return rowcnt

    async def getStatus(self, record: Record) -> str:
        params = {}
        query = "SELECT Status FROM {} WHERE ".format(constants.TABLE_NAME)
        tmp = []
        if record.discordid:
            tmp.append("Discordid=%(discordid)s")
            params.update(discordid=record.discordid)
        if record.email:
            tmp.append("Email=%(email)s")
            params.update(email=record.email)
        if record.token:
            tmp.append("Token=%(token)s")
            params.update(token=record.token)
        if record.time:
            tmp.append("Time=%(time)s")
            params.update(time=str(record.time))
        if record._type:
            tmp.append("Type=%(_type)s")
            params.update(_type=record._type)
        if record.status:
            tmp.append("Status=%(status)s")
            params.update(status=record.status)
        query += " AND ".join(tmp)


        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = cursor.fetchall()

        rows = rows.result()
        if len(rows) != 1:
            return None
        for row in rows:
            return row[0]

    async def setRegistered(self, record: Record):
        return await self.setStatus(record, "registered")

    async def setPending(self, record: Record):
        return await self.setStatus(record, "pending")

    async def isRegistered(self, record: Record) -> bool:
        return (await self.getStatus(record)) == "registered"

    async def isPending(self, record: Record) -> bool:
        return (await self.getStatus(record)) == "pending"

    async def deleteRecord(self, record: Record):
        params = {}
        query = "DELETE FROM {} WHERE ".format(constants.TABLE_NAME)
        tmp = []
        if record.discordid:
            tmp.append("Discordid=%(discordid)s")
            params.update(discordid=record.discordid)
        if record.email:
            tmp.append("Email=%(email)s")
            params.update(email=record.email)
        if record.token:
            tmp.append("Token=%(token)s")
            params.update(token=record.token)
        if record.time:
            tmp.append("Time=%(time)s")
            params.update(time=str(record.time))
        if record._type:
            tmp.append("Type=%(_type)s")
            params.update(_type=record._type)
        if record.status:
            tmp.append("Status=%(status)s")
            params.update(status=record.status)
        query += " AND ".join(tmp)

        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            rowcnt = cursor.rowcount
        return rowcnt
        
    async def exists(self, record: Record) -> bool:
        params = {}
        query = "SELECT * FROM {} WHERE ".format(constants.TABLE_NAME)
        tmp = []
        if record.discordid:
            tmp.append("Discordid=%(discordid)s")
            params.update(discordid=record.discordid)
        if record.email:
            tmp.append("Email=%(email)s")
            params.update(email=record.email)
        if record.token:
            tmp.append("Token=%(token)s")
            params.update(token=record.token)
        if record.time:
            tmp.append("Time=%(time)s")
            params.update(time=str(record.time))
        if record._type:
            tmp.append("Type=%(_type)s")
            params.update(_type=record._type)
        if record.status:
            tmp.append("Status=%(status)s")
            params.update(status=record.status)
        query += " AND ".join(tmp)

        async with self.connection.cursor() as cursor:
            await cursor.execute(query, params)
            rows = cursor.fetchall()

        if len(rows.result()) < 1:
            return False
        return True

    async def getToken(self, record: Record):
        query = "SELECT Token FROM {} WHERE Discordid=%s".format(constants.TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, record.discordid)
            rows = cursor.fetchall()
        rows = rows.result()
        if len(rows) != 1:
            return
        for row in rows:
            return row[0]

    async def getRoleForUser(self, record: Record):
        query = "SELECT Type FROM {} WHERE Discordid=%s".format(constants.TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, record.discordid)
            rows = cursor.fetchall()
        rows = rows.result()
        if len(rows) != 1:
            return
        for row in rows:
            return row[0]

    async def userNameExists(self, record: Record) -> bool:
        return await self.exists(Record(discordid=record.discordid))

    async def emailExists(self, record: Record) -> bool:
        return await self.exists(Record(email=record.email))
    

    #blacklist
    #util
    async def rebuildBlacklistTable(self):
        queryDrop = "DROP TABLE IF EXISTS {}".format(constants.BLACKLIST_TABLE_NAME)
        queryBuild = '''CREATE TABLE {} (
            Email varchar(255) NOT NULL,
            PRIMARY KEY (Email)
        )'''.format(constants.BLACKLIST_TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(queryDrop)
            await cursor.execute(queryBuild)

    async def insertIntoBlacklist(self, *emails: str):
        data = []
        for email in emails:
            data.append((email,))
        query = "INSERT INTO {} (Email) VALUES (%s)".format(constants.BLACKLIST_TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.executemany(query, data)

    async def deleteFromBlacklist(self, *emails: str) -> int:
        data = []
        for email in emails:
            data.append((email,))
        query = "DELETE FROM {} WHERE Email=%s".format(constants.BLACKLIST_TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.executemany(query, data)
            rowcnt = cursor.rowcount
        return rowcnt

    async def isInBlacklist(self, email: str) -> bool:
        query = "SELECT * FROM {} WHERE Email=%s".format(constants.BLACKLIST_TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query, (email,))
            rows = cursor.fetchall()
        if len(rows.result()) < 1:
            return False
        return True

    async def getBlacklist(self) -> [(str, )]:
        query = "SELECT Email FROM {} ORDER BY Email ASC".format(constants.BLACKLIST_TABLE_NAME)
        async with self.connection.cursor() as cursor:
            await cursor.execute(query)
            rows = cursor.fetchall()
        return rows.result()


#Driver test
async def run(loop):
    db = AsyncDb(loop)
    #await db.initConnection()

    #await db.createDB()
    #wait db.rebuildTable()
    #await db.rebuildBlacklistTable()
    #await db.commit()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))