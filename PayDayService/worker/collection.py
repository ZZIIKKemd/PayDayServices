from typing import Dict, Union

from worker.abstract import LoopedWorker, RoutedWorker


class WorkerCollection(Dict[str, Union[LoopedWorker, RoutedWorker]]):
    def __init__(self):
        """Collection (basically a dictionary) of APIs by those identifiers
        """
