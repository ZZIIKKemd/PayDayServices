import aiohttp

from modules.logger import log_error, log_info


class Api:
    def __init__(self, key, listId):
        self.url = 'https://api.unisender.com/ru/api/subscribe'

        self.data = dict()
        self.data['api_key'] = key
        self.data['list_ids'] = listId
        self.data['double_optin'] = 3
        self.data['format'] = 'json'

    async def add(self, email):
        self.data['fields[email]'] = email

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=self.data) as resp:
                if not resp.status == 200:
                    log_error('Unisender не отвечает!')
                    return

                data = await resp.json()
                if 'error' in data:
                    text = 'Не получилось записать email {}\nОшибка: {}'
                    log_error(text.format(email, data['error']))
                else:
                    log_info('Email {} записан'.format(email))
