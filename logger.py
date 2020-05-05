import logging
from datetime import datetime

from dateutil.tz import gettz


def log_init(filename):
    open(filename, 'w').close()
    logging.basicConfig(filename=filename, level=logging.INFO)


def log_error(msg):
    logging.error(msg + '\nВремя: {}\n\n'.format(
        datetime.now(gettz('Europe/Moscow'))))


def log_info(msg):
    logging.info(msg + '\nВремя: {}\n\n'.format(
        datetime.now(gettz('Europe/Moscow'))))
