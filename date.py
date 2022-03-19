

def getLastTimeOfDay(now , timeOfDay, zoneOffset=8):
    return int((now - timeOfDay + zoneOffset*3600) // 86400 * 86400) + timeOfDay - zoneOffset*3600


def getLastTimeOfWeek(now, dayOfWeek, timeOfDay, zoneOffset=8):
    return int((now - (dayOfWeek*86400+timeOfDay) + zoneOffset*3600 + 86400 * 4) // 604800 * 604800) + (dayOfWeek*86400+timeOfDay) - zoneOffset*3600 - 86400 * 4

