import aiohttp

from modules.logger import log_error, log_info


class Telegram:
    def __init__(self, config):
        self.urlStart = 'https://api.telegram.org/bot' + config['token'] + '/'
        self.chat = config['chat']

    async def send_msg(self, msgText):
        url = self.urlStart + 'sendMessage'
        sendData = {
            'chat_id': self.chat,
            'text': msgText
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=sendData) as resp:
                    data = await resp.json()
                    if not data['ok']:
                        text = 'Ошибка {} при отправке Telegram-сообщения {}.'
                        log_error(text.format(data['description'], msgText))
                        return
                    else:
                        log_info('Отправлено Telegram-сообщение {}.'.format(
                            msgText))
                        return
        except aiohttp.ClientConnectorError as e:
            log_error('Ошибка подключения к API Telegram.')
            return