import abc

from utils.broker_connector import authenticate, topup, create_user
from utils.broker_response_parser import parse_auth_token


class BaseTradingBot(abc.ABC):
    def __init__(self, username: str, password: str):
        self.username = username
        self.password = password

        create_user(username, password) # will not create a user if it already exists

        self.auth_token = parse_auth_token(authenticate(username, password))

    def topup(self, amount: float):
        topup(self.auth_token, amount)

    @abc.abstractmethod
    def run(self):
        pass
