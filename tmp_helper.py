from utils.broker_connector import authenticate, delete_user
from utils.broker_response_parser import parse_auth_token

username = "transaction_cost_bot"
pwd = "1234"

auth_token = parse_auth_token(authenticate(username, pwd))
delete_user(auth_token)
