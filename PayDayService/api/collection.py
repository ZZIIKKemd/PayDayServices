from typing import Dict

from api.abstract import Api


class ApiCollection(Dict[str, Api]):
    def __init__(self):
        """Collection (basically a dictionary) of APIs by those identifiers
        """
