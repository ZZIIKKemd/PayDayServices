# from server.server import Server
from sys import exit

from api.collection import ApiCollection
from api.factory import ApiFactory
from common.config import Config
from common.logger import Logger

LOG = '.log'
CONFIG = 'config.yml'


def __error__():
    print('Ошибка при инициализации. Ознакомьтесь с файлом {}'.format(LOG))
    exit(0)


def main():
    logger = Logger(LOG)
    logger.info('Лог-файл "{}" инициализирован'.format(LOG))

    try:
        config = Config(CONFIG)
    except Exception as e:
        logger.critical(e)
        __error__()
    logger.info('Файл конфигурации загружен')

    apis = ApiCollection()
    for apiname, apiconfig in config['apis'].items():
        try:
            apis[apiname] = ApiFactory.new(apiname, apiconfig)
        except Exception as e:
            logger.critical(e)
            __error__()
        s = 'API с идентификатором "{}" инициализирован'.format(apiname)
        logger.info(s)
    logger.info('Все API инициализированы')

    app = apis['goip']
    print(app._name)


if __name__ == "__main__":
    main()
