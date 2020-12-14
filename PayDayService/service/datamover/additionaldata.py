import asyncio

from microservice import MicroService
from modules.datamover import move


class AdditionalDataService(MicroService):
    def __init__(self):
        super().__init__('mover.log', 'mover.pid', 'config.yml')
        
        asyncio.get_event_loop().run_until_complete(
            move(self.config['dbconf'], self.config['uniconf']))

if __name__ == "__main__":
    service = AdditionalDataService()
