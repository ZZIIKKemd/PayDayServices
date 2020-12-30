from typing import Any

from api.abstract import ApiConfigurationException
from api.type import ApiType
from api.type.goip import Goip
from api.type.telegram import Telegram
from api.type.unisender import Unisender


class ApiFactory:
    @staticmethod
    def new(name: str, config: Any) -> ApiType:
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

        if config['type'] == 'unisender':
            api = Unisender(name, config)
        elif config['type'] == 'goip':
            api = Goip(name, config)
        elif config['type'] == 'telegram':
            api = Telegram(name, config)
        else:
            s = 'Неизвестный тип "{}" у параметра API "{}".'
            s = s.format(config['type'], name)
            raise ApiConfigurationException(s)

        return api
