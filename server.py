import asyncio
from datetime import datetime

from aiohttp import web
from dateutil.tz import gettz

from logger import log_error
from postgres import DataBase
from unisender import Api


class RoutesHandlers:
    async def add_entry(self, request):
        data = request.query
        db = request.app['db']

        if 'email' in data:
            email = data['email']
        else:
            return web.Response(text='В запросе не указана почта')

        if 'time' in data:
            time = data['time']
        else:
            return web.Response(text='В запросе не указано время отправки')

        try:
            await db.add_entry(email, time)
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


class Server():
    def __init__(self, dbConfig, apiConfig):
        self.app = web.Application()

        self.app['db'] = DataBase(
            dbConfig['host'], dbConfig['port'],
            dbConfig['user'], dbConfig['password'],
            dbConfig['dbname'], dbConfig['tname'])
        self.app['api'] = Api(apiConfig['key'], apiConfig['list'])

        handlers = RoutesHandlers()
        self.app.add_routes(
            [web.get('/add_entry', handlers.add_entry),
             web.get('/remove_day', handlers.remove_day)])

    def start(self):
        asyncio.get_event_loop().run_until_complete(
            self.app['db'].start_pool())

        async def send_loop(app):
            while True:
                try:
                    await asyncio.sleep(1)

                    nextMsg = await app['db'].get_next()
                    if not nextMsg:
                        continue
                    now = datetime.now(gettz('Europe/Moscow'))
                    if now >= nextMsg['time']:
                        try:
                            await app['api'].add(nextMsg['email'])
                        except:
                            pass
                        else:
                            await app['db'].remove_entry(nextMsg['id'])
                except asyncio.CancelledError:
                    break
                except Exception as e:
                    log_error('Неожиданная ошибка сервера: '+str(e))
                    break

        async def start_background_tasks(app):
            app['sender'] = asyncio.create_task(send_loop(app))

        async def cleanup_background_tasks(app):
            app['sender'].cancel()

        self.app.on_startup.append(start_background_tasks)
        self.app.on_cleanup.append(cleanup_background_tasks)

        web.run_app(self.app)
