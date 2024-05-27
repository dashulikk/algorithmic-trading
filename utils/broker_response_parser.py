import requests
import ast


def parse_auth_token(auth_response: requests.Response) -> str:
    return auth_response.json()["access_token"]


def parse_balance(balance_response: requests.Response) -> float:
    return float(balance_response.json()["balance"])


def parse_stock_price(stock_price_response: requests.Response) -> float:
    return float(stock_price_response.json()["stock_price"])


def parse_net_worth(net_worth_response: requests.Response) -> float:
    return float(net_worth_response.json()["net_worth"])


def parse_portfolio(portfolio_response: requests.Response) -> dict[str, float]:
    portfolio_str = portfolio_response.json()["portfolio"]
    return ast.literal_eval(portfolio_str)
