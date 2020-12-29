from typing import Dict

import aiohttp
from api.abstract import Api, ApiException


class TelegramApiException(ApiException):
    pass

class Telegram(Api):
    def __init__(self, name: str, config: Dict):
        """Telegram API connection
        """        
        super().__init__(name, config)

        self._check_config('token', str)
        self._urlstart = 'https://api.telegram.org/bot'
        self._urlstart += config['token'] + '/'
            
        self._check_config('chat', int)
        self._chat = config['chat']

    async def send_msg(self, text: str) -> None:
        """Send message to Telegram chat
        """        
        url = self._urlstart + 'sendMessage'
        senddata = {
            'chat_id': self._chat,
            'text': text
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=senddata) as resp:
                    data = await resp.json()
                    if not data['ok']:
                        s = 'Telegram API с идентификатором "{}" не получ'
                        s += 'илось отправить сообщение "{}". Ошибка: "{}"'
                        s = s.format(self._name, data['description'], text)
                        raise TelegramApiException(s)
        except aiohttp.ClientConnectorError:
            s = 'Ошибка подключения к API Telegram.'
            raise TelegramApiException(s)
