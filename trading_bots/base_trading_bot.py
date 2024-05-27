import abc

from utils.broker_connector import authenticate
from utils.broker_response_parser import parse_auth_token


class BaseTradingBot(abc.ABC):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        self.auth_token = parse_auth_token(authenticate(username, password))

    @abc.abstractmethod
    def run(self):
        pass
