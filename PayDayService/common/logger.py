import logging
from os import getcwd


class Logger:
    def __init__(self, filelocation: str):
        """Logger of service information
        """
        location = getcwd() + '/' + filelocation
        open(location, 'w').close()

        self.log = logging.getLogger('Service log')
        self.log.setLevel(logging.INFO)
        filestream = logging.FileHandler(location)
        filestream.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(name)s at %(asctime)s -- %(levelname)s: %(message)s')
        filestream.setFormatter(formatter)
        self.log.addHandler(filestream)

    def critical(self, exception: Exception) -> None:
        """Logs critical exception message
        """
        self.log.critical(exception)

    def error(self, exception: Exception) -> None:
        """Logs error message
        """        
        self.log.error(exception)

    def info(self, info: str) -> None:
        """Logs information message
        """        
        self.log.info(info)
