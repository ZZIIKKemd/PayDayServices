from typing import Dict

from aiohttp.web_request import Request
from api.collection import ApiCollection
from common.database import Database
from common.exception import ServiceException


class WorkerConfigurationException(ServiceException):
    pass


class WorkerException(ServiceException):
    pass


class Worker:
    _type = ''

    def __init__(self, name: str, config: Dict, db: Database):
        """Abstract worker class with basic initialization
        """
        self._name = name
        self._config = config
        self._db = db

    def get_name(self) -> str:
        """Returns worker identifier
        """
        return self._name

    def get_type(self) -> str:
        """ Returns worker type
        """
        return self._type

    def _check_config(self, fieldname: str, fieldtype: type) -> bool:
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
    def __init__(self, name: str, config: Dict, db: Database):
        """Abstract routed worker class with basic initialization
        """
        super().__init__(name, config, db)
        self._type = 'routed'

        self._check_config('route', str)
        self._route = config['route']

    def get_path(self) -> str:
        """Returns web route of the worker
        """
        return '/' + self._route

    def run(self, request: Request) -> None:
        """Work, that should be done on web route access. Requires implementation.
        """
        raise NotImplementedError


class LoopedWorker(Worker):
    def __init__(self, name: str, config: Dict, db: Database):
        """Abstract looped worker class with basic initialization
        """
        super().__init__(name, config, db)
        self._type = 'looped'

    def run(self) -> None:
        """Work, that should be done each loop. Requires implementation.
        """
        raise NotImplementedError


class ApiUser(Worker):
    def __init__(self,
                 name: str,
                 config: Dict,
                 db: Database,
                 api: ApiCollection):
        """Abstract API using worker class with basic initialization
        """
        super().__init__(name, config, db)

        self._check_config('apis', Dict[str, str])
        self._bind_apis()

    def _bind_apis(self) -> None:
        """Bind apis to class fields. Requires implementation.
        """
        raise NotImplementedError
