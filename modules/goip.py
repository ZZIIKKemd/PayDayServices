from datetime import datetime, timedelta
from random import randint

import aiohttp
from dateutil.tz import gettz

from modules.logger import log_error, log_info


class SmsRelay:
    def __init__(self, config):
        self.url = 'http://{}:{}/default/en_US/send.html'.format(
            config['host'], config['port'])
        self.user = config['user']
        self.pw = config['password']
        self.sims = config['simcount']
        self.texts = config['messages']
        self.tele2Nums = [
            '900', '901', '902', '904', '908',
            '950', '951', '952', '953', '958',
            '977', '978', '979', '991', '992',
            '993', '994', '995', '996', '999']

    def tele2_phone(self, phone):
        return phone[1:4] in self.tele2Nums

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

    async def __send(self, msgData):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url, params=msgData) as resp:
                    pass
        except aiohttp.ServerDisconnectedError as resp:
            if not resp.message.code == 200:
                log_error('GoIP не отвечает!')
                return

            if 'ERROR' in resp.message.reason:
                text = 'Не получилось отправить смс {} на номер {}'
                text += '\nОшибка: {}'
                log_error(text.format(
                    msgData['m'], msgData['p'], resp.message.reason))
            else:
                log_info('Смс {} на номер {} отправлено'.format(
                        msgData['m'], msgData['p']))

    async def send_specific_sim(self, sim, msg, phone):
        sendData = {
            'u': self.user,
            'p': self.pw,
            'l': str(sim),
            'n': str(phone),
            'm': msg}
        await self.__send(sendData)

    async def send_random_sim(self, msg, phone):
        sendData = {
            'u': self.user,
            'p': self.pw,
            'l': randint(1, self.sims),
            'n': str(phone),
            'm': msg}
        await self.__send(sendData)

    async def test_send(self, phone):
        textIndex = 0
        for sim in range(self.sims):
            await self.send_specific_sim(sim+1, self.texts[textIndex], phone)
            textIndex += 1
            if textIndex == len(self.texts):
                textIndex = 0