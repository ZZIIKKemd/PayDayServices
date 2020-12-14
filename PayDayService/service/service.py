import sys
from os import getcwd, getpid

import yaml

from modules.logger import log_error, log_init


class MicroService:
    def __init__(self, log, pid, config):
        thisDir = getcwd() + '/'
        print(thisDir)

        log_init(thisDir+log)

        with open(thisDir+pid, 'w') as f:
            f.write(str(getpid()))

        try:
            with open(thisDir+config) as file:
                self.config = yaml.safe_load(file)
        except FileNotFoundError:
            log_error('Нет конфигурационного файла')
