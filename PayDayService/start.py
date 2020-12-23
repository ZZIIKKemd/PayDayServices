# from server.server import Server
from sys import exit

from api.collection import ApiCollection
from api.factory import ApiFactory
from common.config import Config
from common.logger import Logger


class Starter:
    logfile = '.log'
    configfile = 'config.yml'

    def __init__(self):
        self.logger = Logger(self.logfile)
        self.logger.info('Лог-файл "{}" инициализирован'.format(self.logfile))

        try:
            config = Config(self.configfile)
        except Exception as e:
            self._init_error(e)
        self.logger.info('Файл конфигурации загружен')

        apis = ApiCollection()
        for apiname, apiconfig in config['apis'].items():
            try:
                apis[apiname] = ApiFactory.new(apiname, apiconfig)
            except Exception as e:
                self._init_error(e)
            s = 'API с идентификатором "{}" инициализирован'.format(apiname)
            self.logger.info(s)
        self.logger.info('Все API инициализированы')

        app = apis['goip']
        print(app._name)

    def _init_error(self, error: Exception):
        """Logs critical error and closes the program with helpful message
        """        
        self.logger.critical(error)
        s = 'Ошибка при инициализации. Ознакомьтесь с файлом {}'
        s = s.format(self.logfile)
        print()
        exit(0)


if __name__ == "__main__":
    prog = Starter()
