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

    def _check_config(self, fieldname: str, fieldtype: type) -> None:
        """Checks if the specified field of worker configuration is correct
        and matches the given type
        """
        if not fieldname in self._config:
            s = 'У воркера {} нет поля с именем "{}"'
            s = s.format(self._name, fieldname)
            raise WorkerConfigurationException(s)

        if not isinstance(self._config[fieldname], fieldtype):
            s = 'У воркера {} поле "{}" неверного типа. Необходимый тип: "{}"'
            s = s.format(self._name, fieldname, fieldtype)
            raise WorkerConfigurationException(s)


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
                 apis: ApiCollection):
        """Abstract API using worker class with basic initialization
        """
        super().__init__(name, config, db)

        self._check_config('apis', dict)
        self._bind_apis(apis)

    def _bind_apis(self, apis: ApiCollection) -> None:
        """Bind apis to class fields. Requires implementation.
        """
        raise NotImplementedError

    def _check_apis(self, fieldname: str, apis: ApiCollection):
        """Checks if the specified field of worker API configuration
        is exist and is string type and that such API was initialized
        """
        if not fieldname in self._config['apis']:
            s = 'У воркера {} в конфигурационном файле нет API с именем "{}"'
            s = s.format(self._name, fieldname)
            raise WorkerConfigurationException(s)

        apiname = self._config['apis'][fieldname]

        if not isinstance(apiname, str):
            s = 'У воркера {} поле API "{}" не является строкой'
            s = s.format(self._name, fieldname)
            raise WorkerConfigurationException(s)

        if not apiname in apis:
            s = 'Для воркера {} необходимо API с идентификатором "{}"'
            s += ', которого нет в списке инициализированных'
            s = s.format(self._name, apiname)
            raise WorkerConfigurationException(s)