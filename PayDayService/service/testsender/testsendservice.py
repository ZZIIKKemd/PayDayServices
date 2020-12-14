import asyncio

from microservice import MicroService
from modules.testsender import TestSender


class TestSendService(MicroService):
    def __init__(self):
        super().__init__('sender.log', 'sender.pid', 'config.yml')
        
        sender = TestSender(self.config['senderconf'], self.config['teleconf'])
        asyncio.get_event_loop().run_until_complete(sender.send())

if __name__ == "__main__":
    service = TestSendService()
