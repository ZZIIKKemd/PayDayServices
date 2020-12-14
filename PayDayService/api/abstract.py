from typing import Dict

from common.exception import ServiceException


class ApiConfigurationException(ServiceException):
    pass


class ApiException(ServiceException):
    pass


class Api:
    def __init__(self, name: str, config: Dict):
        """Abstract API class with basic initialization
        """
        self._name = name
        self._type = config['type']
        self._config = config

    def get_name(self) -> str:
        """Returns API identifier
        """
        return self._name

    def get_type(self) -> str:
        """ Returns API type
        """
        return self._type

    def _is_correct_field(self, fieldname: str, fieldtype: type) -> bool:
        """Checks if the specified field of API configuration is correct
        and matches the given type
        """
        if not fieldname in self._config:
            s = 'У API {} с идентификатором "{}" нет поля с именем "{}"'
            s = s.format(self._type, self._name, fieldname)
            raise ApiConfigurationException(s)

        if not isinstance(self._config[fieldname], fieldtype):
            s = 'У API {} с идентификатором "{}" поле "{}" неверного типа. '
            s += 'Необходимый тип: "{}"'
            s = s.format(self._type, self._name, fieldname, fieldtype)
            raise ApiConfigurationException(s)
        
        return True
