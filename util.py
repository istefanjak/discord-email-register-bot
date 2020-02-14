def getFromListCaseIgnored(s: str, lst: [str]) -> str:
    for e in lst:
        if e.lower() == s.lower():
            return e
    return None
