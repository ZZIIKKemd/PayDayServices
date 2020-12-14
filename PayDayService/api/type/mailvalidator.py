import aiohttp

from modules.logger import log_error, log_info


class Api:
    def __init__(self, config):
        self.url = 'https://mailvalidator.ru/api/v2/email_check/'
        self.headers = {'Authorization': 'Token ' + config['token']}

    async def check(self, email):
        pushData = {'email': email}

        async with aiohttp.ClientSession() as session:
            async with session.get(
                self.url, data=pushData, headers=self.headers) as resp:
                if not resp.status == 200:
                    log_error('Mailvalidator не отвечает!')
                    return

                data = await resp.json()
                return data['Email status express']
