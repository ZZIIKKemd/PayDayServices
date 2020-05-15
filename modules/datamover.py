import asyncio
from datetime import datetime, timedelta

from dateutil.tz import gettz

from modules.postgres import DataBase


async def move(dbConfig, uniConfig):
    db = DataBase(
        dbConfig['ssl'], dbConfig['host'], dbConfig['port'],
        dbConfig['user'], dbConfig['password'], dbConfig['db'],
        dbConfig['tinput'], dbConfig['tuni'])
    await db.start_pool()

    time = datetime.now(gettz('Europe/Moscow')) + timedelta(days=1)
    tomorrow = datetime.date(time)
    queue = await db.get_day(tomorrow)
    thirdOfNext = len(queue) // 3

    queue = await db.get_raw_fresh_unused()
    goods = list()
    for data in queue:
        email = data['email']
        isGood = email.endswith('@mail.ru') or email.endswith('@bk.ru')
        isGood = isGood or email.endswith('@inbox.ru')
        isGood = isGood or email.endswith('@list.ru')
        isGood = isGood and not email == str(data['phone'])+'@mail.ru'
        if isGood:
            goods.append(data)
        if len(goods) == thirdOfNext:
            break

    if len(goods) < 3:
        return
    third = len(goods) // 3
    y = tomorrow.year
    m = tomorrow.month
    d = tomorrow.day

    msec = 0
    mstep = 3600000 // third
    for i in range(third):
        goods[i]['time'] = get_iso_time(y, m, d, msec)
        msec += mstep

    msec = 3600000
    mstep = 5040000 // (len(goods)-third)
    for i in range(third, len(goods)):
        goods[i]['time'] = get_iso_time(y, m, d, msec)
        msec += mstep

    for entry in goods:
        await db.add_entry(
            entry['name'], entry['email'],
            None, entry['time'], uniConfig['pluslist'])
        await db.set_raw_used(entry['id'])


def get_iso_time(year, month, day, ms):
    h = ms // 360000
    remain = ms % 360000
    m = remain // 6000
    remain %= 6000
    s = remain // 100

    time = datetime(year, month, day, h, m, s)
    return time.isoformat(' ')
