import aiohttp

from modules.logger import log_error, log_info


class Api:
    def __init__(self, config):
        self.url = 'https://api.unisender.com/ru/api/subscribe'
        self.api_key = config['key']
        self.format = 'json'

    async def add(self, name, email, phone, listId):
        pushData = {
            'api_key': self.api_key,
            'fields[email]': email,
            'list_ids': listId,
            'double_optin': 3,
            'format': self.format}
        if name:
            pushData['fields[Name]'] = name
        if phone:
            pushData['fields[phone]'] = '+' + str(phone)

        async with aiohttp.ClientSession() as session:
            async with session.post(self.url, data=pushData) as resp:
                if not resp.status == 200:
                    log_error('Unisender не отвечает!')
                    return

                data = await resp.json()
                if 'error' in data:
                    text = 'Не получилось записать email {}\nОшибка: {}'
                    log_error(text.format(email, data['error']))
                else:
                    log_info('Email {} записан'.format(email))
