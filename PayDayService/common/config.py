from os import getcwd
from typing import Dict

import yaml
from yaml.scanner import ScannerError

from common.exception import ServiceException


class ConfigLoadException(ServiceException):
    pass


class BadConfigException(ServiceException):
    pass


class Config:
    def __init__(self, filelocation: str):
        """Loads and stores all configuration data from the given yaml file
        """
        location = getcwd() + '/' + filelocation
        try:
            with open(location) as file:
                self.__data = yaml.safe_load(file)
        except FileNotFoundError:
            s = 'Файл конфигурации {} не найден'.format(location)
            raise ConfigLoadException(s)
        except ScannerError as e:
            s = 'Ошибка файла конфигурации:\n' + str(e)
            raise BadConfigException(s)

        if not isinstance(self.__data, dict):
            s = 'Файл конфигурации не является именованным списком'
            raise BadConfigException(s)

    def get_config(self, name: str) -> Dict:
        """Returns specified configuration
        """
        if not name in self.__data:
            s = 'В файле конфигурации нет параметра "{}"'.format(name)
            raise BadConfigException(s)
        if not isinstance(self.__data[name], dict):
            s = 'Параметр "{}" в файле конфигурации'
            s += ' не является именованным списком'
            s = s.format(name)
            raise BadConfigException(s)
        return self.__data[name]

    def __getitem__(self, name: str) -> Dict:
        return self.get_config(name)
