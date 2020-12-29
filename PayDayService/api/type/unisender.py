from typing import Dict, Optional

import aiohttp
from api.abstract import Api, ApiException


class UnisenderApiException(ApiException):
    pass


class Unisender(Api):
    _url = 'https://api.unisender.com/ru/api/subscribe'
    _format = 'json'
    _double_optin = 3

    def __init__(self, name: str, config: Dict):
        """Unisender API connection
        """
        super().__init__(name, config)

        self._check_config('key', str)
        self._api_key = config['key']
            
        self._check_config('list', int)
        self._list = config['list']

    async def add(
            self,
            email: str,
            name: Optional[str] = None,
            phone: Optional[str] = None) -> None:
        """Adds new subscriber to the Unisender list
        """
        pushdata = {
            'api_key': self._api_key,
            'fields[email]': email,
            'list_ids': self._list,
            'double_optin': self._double_optin,
            'format': self._format}
        if name:
            pushdata['fields[Name]'] = name
        if phone:
            pushdata['fields[phone]'] = '+' + str(phone)

        async with aiohttp.ClientSession() as session:
            async with session.post(self._url, data=pushdata) as resp:
                if not resp.status == 200:
                    s = 'Сервера Unisender возвращают ошибку {}'
                    s = s.format(resp.status)
                    raise UnisenderApiException(s)

                data = await resp.json()
                if 'error' in data:
                    s = 'API Unisender с идентификатором "{}" '
                    s += 'не получилось записать email "{}". Ошибка: "{}"'
                    s = s.format(self._name, email, data['error'])
                    raise UnisenderApiException(s)

    @staticmethod
    def is_mailru_adress(email: str) -> bool:
        """Checks if the specified string is valid mail.ru email
        """
        is_mailru = email.endswith('@mail.ru')
        is_mailru = is_mailru or email.endswith('@bk.ru')
        is_mailru = is_mailru or email.endswith('@list.ru')
        is_mailru = is_mailru or email.endswith('@inbox.ru')
        return is_mailru
