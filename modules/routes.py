from datetime import datetime

from aiohttp import web
from dateutil.tz import gettz


class Routes:
    def __init__(self):
        self.routes = [
            web.get('/add_entry', self.add_entry),
            web.get('/remove_day', self.remove_day),
            web.get('/add_raw_data', self.add_raw_data)
        ]

    async def add_entry(self, request):
        data = request.query
        db = request.app['db']

        if 'name' in data:
            name = data['name']
        else:
            name = None

        if 'email' in data:
            email = data['email']
        else:
            return web.Response(text='В запросе не указана почта')

        if 'phone' in data:
            phone = data['phone']
        else:
            phone = None

        if 'time' in data:
            time = data['time']
        else:
            return web.Response(text='В запросе не указано время отправки')

        if 'list' in data:
            listId = data['list']
        else:
            return web.Response(text='В запросе не указан ID списка в Unisender')

        try:
            await db.add_entry(name, email, phone, time, listId)
        except Exception as e:
            return web.Response(text='Ошибка: {}'.format(str(e)))

        return web.Response(text='Адрес поставлен в очередь')

    async def remove_day(self, request):
        data = request.query
        db = request.app['db']

        if 'day' in data:
            day = data['day']
        else:
            return web.Response(text='В запросе не указан день очистки')

        try:
            await db.clear_day(day)
        except Exception as e:
            return web.Response(text='Ошибка: {}'.format(str(e)))

        return web.Response(text='День очищен от запросов')

    async def add_raw_data(self, request):
        data = request.query
        db = request.app['db']
        relay = request.app['sms']
        api = request.app['api']

        if 'name' in data:
            name = data['name']
        else:
            return web.Response(text='В запросе не указано имя')

        if 'email' in data:
            email = data['email']
        else:
            return web.Response(text='В запросе не указана почта')

        if 'phone' in data:
            phone = data['phone']
        else:
            return web.Response(text='В запросе не указан телефон')

        try:
            await db.add_raw_entry(name, email, phone)
        except Exception as e:
            return web.Response(text='Ошибка: {}'.format(str(e)))

        try:
            await api.add(name, email, phone)
        except Exception as e:
            return web.Response(text='Ошибка: {}'.format(str(e)))

        if relay.tele2_phone(phone):
            smsData = relay.form_messages(name)
            try:
                await db.add_sms(smsData[0][0], '8'+phone[1:], smsData[0][1])
                await db.add_sms(smsData[1][0], '8'+phone[1:], smsData[1][1])
            except Exception as e:
                return web.Response(text='Ошибка: {}'.format(str(e)))

        return web.Response(text='Данные записаны')
