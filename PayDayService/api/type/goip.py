from random import randint
from typing import Dict, cast

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

        host = cast(str, self._get_config('host', str))
        port = cast(int, self._get_config('port', int))
        url = 'http://{}:{}/default/en_US/send.html'
        self._url = url.format(host, port)

        self._user = cast(str, self._get_config('user', str))

        self._password = cast(str, self._get_config('password', str))

        self._sims = cast(int, self._get_config('simcount', int))

    def is_tele2_phone(self, phone: str) -> bool:
        """Checks if the specified phone number operator is Tele2
        """
        return phone[1:4] in self._tele2numbers

    async def _send(self, data: Dict[str, str]) -> None:
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
