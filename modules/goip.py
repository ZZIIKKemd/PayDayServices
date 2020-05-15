from datetime import datetime, timedelta

import aiohttp
from dateutil.tz import gettz

from modules.logger import log_error, log_info


class SmsRelay:
    def __init__(self, host, port, user, password, simCount, messages):
        self.url = 'http://{}:{}/default/en_US/send.html'.format(host, port)
        self.port = port
        self.user = user
        self.pw = password
        self.sims = simCount
        self.texts = messages
        self.currSim = 1

    def form_messages(self, name):
        now = datetime.now(gettz('Europe/Moscow'))
        twoMinutes = now + timedelta(minutes=2)
        timeData = (now, twoMinutes)

        smsData = list()
        for i in range(2):
            smstext = self.texts[i]
            text = name + smstext
            if len(text) > 70:
                text = smstext[2].upper() + smstext[3:]
            smsData.append((text, timeData[i]))

        return smsData

    async def send(self, msg, phone):
        sendData = {
            'u': self.user,
            'p': self.pw,
            'l': self.currSim,
            'n': str(phone),
            'm': msg}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, params=sendData) as resp:
                    pass
        except aiohttp.ServerDisconnectedError as resp:
            if not resp.message.code == 200:
                log_error('GoIP не отвечает!')
                return

            if 'ERROR' in resp.message.reason:
                text = 'Не получилось отправить смс {} на номер {}'
                text += '\nОшибка: {}'
                log_error(text.format(msg, phone, resp.message.reason))
            else:
                log_info(
                    'Смс {} на номер {} отправлено'.format(msg, phone))
        
            self.currSim += 1
            if self.currSim > self.sims:
                self.currSim = 1