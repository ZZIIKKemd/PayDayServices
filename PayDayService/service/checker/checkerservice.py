import asyncio

from microservice import MicroService
from modules.checker import Checker


class CheckerService(MicroService):
    def __init__(self):
        super().__init__('checks.log', 'checks.pid', 'config.yml')

        checker = Checker(self.config['dbconf'], self.config['teleconf'])
        asyncio.get_event_loop().run_until_complete(checker.init())
        asyncio.get_event_loop().run_until_complete(checker.check())


if __name__ == "__main__":
    service = CheckerService()
