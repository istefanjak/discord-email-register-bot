from datetime import datetime

class Record:
    """
    Container class used for database entity
    """
    def __init__(self, discordid: str = None, email: str = None, token: str = None, time: datetime = None, _type: str = None, status: str = None):
        self.discordid = discordid
        self.email = email
        self.token = token
        self.time = time
        self._type = _type
        self.status = status

    def xstr(self, s: str) -> str:
        if s is None:
            return "None"
        return s

    def __str__(self):
        return self.xstr(self.discordid) + " " + self.xstr(self.email) + " " + self.xstr(self.token) + " " + self.xstr(str(self.time)) + " " + self.xstr(self.status)