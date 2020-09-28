import asyncio
from datetime import datetime

from aiohttp import web
from dateutil.tz import gettz

from modules.goip import SmsRelay
from modules.logger import log_error
from modules.postgres import DataBase
from modules.routes import Routes
from modules.unisender import Api


class Server():
    def __init__(self, servConfig, dbConfig, apiConfig, smsConfig):
        self.app = web.Application()

        self.app['db'] = DataBase(dbConfig)
        self.app['api'] = Api(apiConfig)
        self.app['sms'] = SmsRelay(smsConfig)

        handlers = Routes()
        self.app.add_routes(handlers.routes)

        self.config = servConfig

    def start(self):
        asyncio.get_event_loop().run_until_complete(
            self.app['db'].start_pool())

        async def send_loop(app):
            while True:
                try:
                    await asyncio.sleep(1)

                    nextMsg = await app['db'].get_next()
                    nextSms = await app['db'].get_next_sms()
                    if not nextMsg and not nextSms:
                        continue

                    now = datetime.now(gettz('Europe/Moscow'))

                    if nextMsg:
                        if now >= nextMsg['time']:
                            try:
                                await app['api'].add(
                                    nextMsg['name'], nextMsg['email'],
                                    nextMsg['phone'], nextMsg['list'])
                            except:
                                pass
                            else:
                                await app['db'].remove_entry(nextMsg['id'])

                    if nextSms:
                        if now >= nextSms['time']:
                            try:
                                await app['sms'].send_random_sim(
                                    nextSms['text'], nextSms['phone'])
                            except Exception as e:
                                pass
                            else:
                                await app['db'].remove_sms(nextSms['id'])

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

        self.app.on_startup.append(start_background_tasks)
        self.app.on_cleanup.append(cleanup_background_tasks)

        web.run_app(self.app, port=self.config['port'])
