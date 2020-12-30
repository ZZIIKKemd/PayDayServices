from typing import Dict

from api.type import ApiType


class ApiCollection(Dict[str, ApiType]):
    def __init__(self):
        """Collection (basically a dictionary) of APIs by those identifiers
        """
