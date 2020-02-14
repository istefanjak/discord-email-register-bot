import secrets

def getToken():
    return secrets.token_urlsafe(32)