from microservice import MicroService
from modules.server import Server

class MainService(MiscroService):
    def __init__(self):
        super().__init__('main.log', 'main.pid', 'config.yml')

        server = Server(self.config['dbconf'], self.config['uniconf'])
        server.start()

if __name__ == "__main__":
    service = MainService()