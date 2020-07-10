from modules.goip import SmsRelay
from modules.telegram import Telegram

class TestSender:
    def __init__(self, senderConfig, telegramConfig):
        self.phone = senderConfig['phone']
        self.tg = Telegram(telegramConfig)
        self.sms = list()
        for relayConfig in senderConfig['relays']:
            self.sms.append(SmsRelay(relayConfig))

    async def send(self):
        for relay in self.sms:
            await relay.test_send(self.phone)
        await self.tg.send_msg('Должны были быть отправлены смс Евгению')