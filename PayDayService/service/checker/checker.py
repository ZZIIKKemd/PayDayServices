from modules.postgres import DataBase
from modules.telegram import Telegram

class Checker:
    def __init__(self, dbConfig, telegramConfig):
        self.db = DataBase(dbConfig)
        self.tg = Telegram(telegramConfig)

    async def init(self):
        await self.db.start_pool()
        
    async def check(self):
        message = str()

        ports = await self.db.get_ports()
        for port in ports:
            count = await self.db.count_sms_by_port(port['number_port'])
            message += 'На шлюзе ' + str(port['number_port']) + ' '
            message += 'осталось ' + str(count) + ' сообщений.\n'
        await self.tg.send_msg(message)