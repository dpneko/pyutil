import time

def getLastTimeOfDay(now , timeOfDay, zoneOffset=8):
    return int((now - timeOfDay + zoneOffset*3600) // 86400 * 86400) + timeOfDay - zoneOffset*3600


def getLastTimeOfWeek(now, dayOfWeek, timeOfDay, zoneOffset=8):
    return int((now - (dayOfWeek*86400+timeOfDay) + zoneOffset*3600 + 86400 * 4) // 604800 * 604800) + (dayOfWeek*86400+timeOfDay) - zoneOffset*3600 - 86400 * 4

def get_day(timestamp):
    # get day of the time in China
    return time.strftime("%Y-%m-%d", time.localtime(timestamp))


def day_to_timestamp_at_eight(day):
    # get timestamp of 8:00 of the day in China
    return int(time.mktime(time.strptime(day, "%Y-%m-%d")) + 8 * 3600)


def get_date(timestamp):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))
