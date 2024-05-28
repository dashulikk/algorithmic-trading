import abc
import sys
import signal
import threading

from utils.broker_connector import authenticate, topup, create_user
from utils.broker_response_parser import parse_auth_token
from utils.logger import Logger


class BaseTradingBot(abc.ABC):
    def __init__(self, username: str, password: str, log_filename: str):
        self.username = username
        self.password = password

        create_user(username, password)  # will not create a user if it already exists

        self.auth_token = parse_auth_token(authenticate(username, password))

        self.logger = Logger(username, password, log_filename)

        self.logger_thread = None

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def log(self, frequency: int | None):
        self.logger_thread = threading.Thread(target=self.logger.log_continuous, args=(frequency,))
        self.logger_thread.start()

    def topup(self, amount: float):
        topup(self.auth_token, amount)

    def shutdown(self, signum, frame):
        self.logger.stop()
        if self.logger_thread is not None:
            self.logger_thread.join()
        sys.exit(0)

    @abc.abstractmethod
    def run(self):
        pass
