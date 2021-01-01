from datetime import datetime, timedelta
from typing import Dict, List, Tuple, cast

from aiohttp import web
from aiohttp.web_request import Request
from aiohttp.web_response import Response
from api.collection import ApiCollection
from api.type.goip import Goip
from api.type.unisender import Unisender
from common.database import Database
from dateutil.tz import gettz
from worker.abstract import (ApiUser, RoutedWorker,
                             WorkerConfigurationException, WorkerException)


class AddRawDataWorkerException(WorkerException):
    pass


class AddRawDataWorker(ApiUser, RoutedWorker):
    def __init__(self,
                 name: str,
                 config: Dict,
                 db: Database,
                 apis: ApiCollection):
        """Routed worker that adds raw data about people to a database and
        sends their data to Unisender and Goip apis if needed
        """
        super().__init__(name, config, db, apis)

        self._send_sms = cast(bool, self._get_config('sendsms', bool))

        messages = list()
        if self._send_sms:
            messages = cast(list, self._get_config('messages', list))
        for message in messages:
            if not isinstance(message, str):
                s = 'Один из шаблонов смс-сообщений'
                s += ' в конфигурации воркера не является строкой'
                raise WorkerConfigurationException(s)
        self._messages = messages

        self._send_uni=cast(bool, self._get_config('senduni', bool))

    def _bind_apis(self, apis: ApiCollection) -> None:
        """Binds apis to class fields.
        """
        self._uni=cast(Unisender, self._get_api('uni', Unisender, apis))
        self._relay=cast(Goip, self._get_api('sms', Goip, apis))

    async def run(self, request: Request) -> Response:
        data=request.query
        db=self._db
        relay=self._relay
        api=self._uni

        if not 'name' in data:
            return web.Response(text = 'В запросе не указано имя')
        name=data['name']

        if not 'email' in data:
            return web.Response(text = 'В запросе не указана почта')
        email=data['email']

        if not 'phone' in data:
            return web.Response(text = 'В запросе не указан телефон')
        phone=data['phone']

        try:
            await db.add_raw_entry(name, email, phone)
        except Exception as e:
            s='Ошибка добавления данных в базу: {}'
            s=s.format(str(e))
            return web.Response(text = s)

        if self._send_uni and api.is_mailru_adress(email):
            try:
                await api.add(name, email, phone)
            except Exception as e:
                s='Ошибка отправки данных в Unisender: {}'
                s=s.format(str(e))
                return web.Response(text = s)

        if self._send_sms and relay.is_tele2_phone(phone):
            smsdata=self._form_messages(name)
            try:
                await db.add_sms(smsdata[0][0], '8'+phone[1:], smsdata[0][1])
                await db.add_sms(smsdata[1][0], '8'+phone[1:], smsdata[1][1])
            except Exception as e:
                s='Ошибка добавления смс в очередь: {}'
                s=s.format(str(e))
                return web.Response(text = s)

        message='Необработанные данные записаны в базу.'
        message += ' Имя: "{}", телефон: "{}", email: "{}".'
        message=message.format(name, phone, email)
        message += ' Данные записаны в Unisender.' if self._send_uni else ''
        message += ' Запланированы смс-сообщения.' if self._send_sms else ''
        self.done_message=message

        return web.Response(text = 'Данные записаны')

    def _form_messages(self, name: str) -> List[Tuple[str, datetime]]:
        now=datetime.now(gettz('Europe/Moscow'))
        twominutes=now + timedelta(minutes = 2)
        timedata=(now, twominutes)

        smsdata=list()
        for i in range(2):
            smstext=self._messages[i]
            text=name + smstext
            if len(text) > 70:
                text=smstext[2].upper() + smstext[3:]
            smsdata.append((text, timedata[i]))

        return smsdata
