from typing import Any, Union

from common.exception import ServiceException

from api.abstract import ApiConfigurationException
from api.type.goip import Goip
from api.type.telegram import Telegram
from api.type.unisender import Unisender

POSSIBLEAPIS = ('unisender', 'goip', 'telegram')


class ApiFactoryException(ServiceException):
    pass


class ApiFactory:
    @staticmethod
    def new(name: str, config: Any) -> Union[Unisender, Telegram, Goip]:
        """Returns new API instance with the specified parameters
        """
        if not isinstance(config, dict):
            s = 'В файле конфигурации параметр API "{}"'
            s += ' не является именованным списком'
            s = s.format(name)
            raise ApiConfigurationException(s)

        if not 'type' in config:
            s = 'У параметра API "{}" нет типа'
            s = s.format(name)
            raise ApiConfigurationException(s)

        if not config['type'] in POSSIBLEAPIS:
            s = 'Неизвестный тип "{}" у параметра API "{}". '
            s += 'Возможные варианты: ' + ','.join(POSSIBLEAPIS)
            s = s.format(config['type'], name)
            raise ApiConfigurationException(s)

        api = None
        if config['type'] == 'unisender':
            api = Unisender(name, config)
        elif config['type'] == 'goip':
            api = Goip(name, config)
        elif config['type'] == 'telegram':
            api = Telegram(name, config)

        if not api:
            s = 'Неизвестный тип API "{}" с идентификатором "{}"'
            s = s.format(config['type'], name)
            raise ApiFactoryException(s)

        return api
