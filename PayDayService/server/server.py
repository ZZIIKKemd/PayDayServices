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

        async def start_background_tasks(app):
            app['sender'] = asyncio.get_event_loop().create_task(
                send_loop(app))

        async def cleanup_background_tasks(app):
            app['sender'].cancel()

        self.app.on_startup.append(start_background_tasks)
        self.app.on_cleanup.append(cleanup_background_tasks)

        web.run_app(self.app, port=self.config['port'])
