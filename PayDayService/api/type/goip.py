from random import randint
from typing import Dict, Union

import aiohttp
from api.abstract import Api, ApiException


class GoipApiException(ApiException):
    pass


class Goip(Api):
    _tele2numbers = [
        '900', '901', '902', '904', '908',
        '950', '951', '952', '953', '958',
        '977', '978', '979', '991', '992',
        '993', '994', '995', '996', '999']

    def __init__(self, name: str, config: Dict):
        """GoIP relay connection
        """
        super().__init__(name, config)

        correcthost = self._is_correct_field('host', str)
        correctport = self._is_correct_field('port', int)
        if correcthost and correctport:
            self._url = 'http://{}:{}/default/en_US/send.html'.format(
                config['host'], config['port'])

        if self._is_correct_field('user', str):
            self._user = config['user']

        if self._is_correct_field('password', str):
            self._password = config['password']

        if self._is_correct_field('simcount', int):
            self._sims = config['simcount']

    def is_tele2_phone(self, phone: str) -> bool:
        """Checks if the specified phone number operator is Tele2
        """
        return phone[1:4] in self._tele2numbers

    # def form_messages(self, name):
    #     now = datetime.now(gettz('Europe/Moscow'))
    #     twoMinutes = now + timedelta(minutes=2)
    #     timeData = (now, twoMinutes)

    #     smsData = list()
    #     for i in range(2):
    #         smstext = self._texts[i]
    #         text = name + smstext
    #         if len(text) > 70:
    #             text = smstext[2].upper() + smstext[3:]
    #         smsData.append((text, timeData[i]))

    #     return smsData

    async def _send(self, data: Dict[str, Union[int, str]]) -> None:
        """Sends message throught relay with the specified data
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self._url, params=data) as resp:
                    text = await resp.text()
                    if not text.startswith('Sending'):
                        s = 'Неожиданное поведение у GoIP API '
                        s += 'с идентификатором "{}". Шлюз вернул: "{}"'
                        s = s.format(self._name)
                        raise GoipApiException(s)
        except aiohttp.ServerDisconnectedError as resp:
            if not resp.message.code == 200:
                s = 'GoIP с идентификатором "{}" не отвечает'
                s = s.format(self._name)
                raise GoipApiException(s)

            if 'ERROR' in resp.message.reason:
                s = 'GoIP API с идентификатором "{}" не получилось '
                s += 'отправить смс {} на номер {}. Ошибка: "{}"'
                s = s.format(
                    self._name, data['m'],
                    data['p'], resp.message.reason)
                raise GoipApiException(s)

    async def send_specific_sim(
            self, sim: int, message: str, phone: int) -> None:
        """Sends message from specific sim card
        """
        data = {
            'u': self._user,
            'p': self._password,
            'l': str(sim),
            'n': str(phone),
            'm': message}
        await self._send(data)

    async def send_random_sim(self, message: str, phone: int) -> None:
        """Sends message from random sim card
        """        
        data = {
            'u': self._user,
            'p': self._password,
            'l': randint(1, self._sims),
            'n': str(phone),
            'm': message}
        await self._send(data)

    # async def test_send(self, phone):
    #     textIndex = 0
    #     for sim in range(self._sims):
    #         await self.send_specific_sim(sim+1, self._texts[textIndex], phone)
    #         textIndex += 1
    #         if textIndex == len(self._texts):
    #             textIndex = 0
