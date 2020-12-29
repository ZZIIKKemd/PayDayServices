from typing import Any, Union

from api.collection import ApiCollection
from common.database import Database

from worker.abstract import WorkerConfigurationException
from worker.type.addraw import AddRawDataWorker


class WorkerFactory:
    @staticmethod
    def new(name: str,
            config: Any,
            db: Database,
            apis: ApiCollection
            ) -> Union[AddRawDataWorker]:
        """Returns new worker instance with the specified parameters
        """
        if not isinstance(config, dict):
            s = 'В файле конфигурации воркер "{}"'
            s += ' не является именованным списком'
            s = s.format(name)
            raise WorkerConfigurationException(s)

        if name == 'addraw':
            worker = AddRawDataWorker(name, config, db, apis)
        else:
            s = 'Неизвестный вид воркера "{}"'.format(name)
            raise WorkerConfigurationException(s)

        return worker
