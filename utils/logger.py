import time
import threading
from utils.broker_connector import authenticate, get_net_worth
from utils.broker_response_parser import parse_auth_token, parse_net_worth


class Logger:
    def __init__(self, username: str, password: str, filename: str):
        self.username = username
        self.password = password

        self.auth_token = parse_auth_token(authenticate(username, password))

        self.filename = filename

        self.stop_event = threading.Event()

    def log_continuous(self, frequency: int | None):
        while not self.stop_event.is_set():
            net_worth = parse_net_worth(get_net_worth(self.auth_token))
            with open(self.filename, 'a') as f:
                f.write(f"{net_worth}\n")

            if frequency is not None:
                time.sleep(frequency)

    def log_manual(self):
        net_worth = parse_net_worth(get_net_worth(self.auth_token))
        with open(self.filename, 'a') as f:
            f.write(f"{net_worth}\n")

    def stop(self):
        self.stop_event.set()
