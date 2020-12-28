from typing import Dict

from aiohttp.web_request import Request

from common.exception import ServiceException


class WorkerConfigurationException(ServiceException):
    pass


class WorkerException(ServiceException):
    pass


class Worker:
    _type = ''

    def __init__(self, name: str, config: Dict):
        """Abstract worker class with basic initialization
        """
        self._name = name
        self._config = config

    def get_name(self) -> str:
        """Returns worker identifier
        """
        return self._name

    def get_type(self) -> str:
        """ Returns worker type
        """
        return self._type

    def _is_correct_field(self, fieldname: str, fieldtype: type) -> bool:
        """Checks if the specified field of worker configuration is correct
        and matches the given type
        """
        if not fieldname in self._config:
            s = 'У воркера {} с идентификатором "{}" нет поля с именем "{}"'
            s = s.format(self._type, self._name, fieldname)
            raise WorkerConfigurationException(s)

        if not isinstance(self._config[fieldname], fieldtype):
            s = 'У воркера {} с идентификатором "{}" поле "{}"'
            s += ' неверного типа. Необходимый тип: "{}"'
            s = s.format(self._type, self._name, fieldname, fieldtype)
            raise WorkerConfigurationException(s)

        return True


class RoutedWorker(Worker):
    def __init__(self, name: str, config: Dict):
        """Abstract routed worker class with basic initialization
        """
        super().__init__(name, config)
        self._type = 'routed'

        self._is_correct_field('route', str)
        self._route = config['route']

    def get_path(self) -> str:
        """Returns web route of the worker
        """
        return '/' + self._route

    def get(self, request: Request) -> None:
        """Work, that should be done on web route access
        """
        raise NotImplementedError


class LoopedWorker(Worker):
    def __init__(self, name: str, config: Dict):
        """Abstract looped worker class with basic initialization
        """
        super().__init__(name, config)
        self._type = 'looped'

    def run(self) -> None:
        """Work, that should be done each loop
        """
        raise NotImplementedError
