import asyncio
from datetime import datetime

from aiohttp import web
from dateutil.tz import gettz

from logger import log_error
from postgres import DataBase
from routes import Routes
from unisender import Api


class Server():
    def __init__(self, dbConfig, apiConfig):
        self.app = web.Application()

        self.app['db'] = DataBase(
            dbConfig['ssl'], dbConfig['host'], dbConfig['port'],
            dbConfig['user'], dbConfig['password'],
            dbConfig['dbname'], dbConfig['tinname'], dbConfig['toutname'])
        self.app['api'] = Api(apiConfig['key'], apiConfig['list'])

        handlers = Routes()
        self.app.add_routes(handlers.routes)

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
            app['sender'] = asyncio.get_event_loop().create_task(
                send_loop(app))

        async def cleanup_background_tasks(app):
            app['sender'].cancel()

        #self.app.on_startup.append(start_background_tasks)
        self.app.on_cleanup.append(cleanup_background_tasks)

        web.run_app(self.app)
