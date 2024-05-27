import requests

HTTP_STRING = "http://"
IP = "127.0.0.1"
PORT = 5000


def _create_endpoint(path: str):
    return f"{HTTP_STRING}{IP}:{PORT}/{path}"


def _get_authorization_header(bearer_token: str):
    return {"Authorization": f"Bearer {bearer_token}"}


def create_user(username: str, password: str) -> requests.Response:
    endpoint = _create_endpoint("create_user")
    body = {
        "username": username,
        "password": password,
    }

    return requests.post(endpoint, json=body)


def authenticate(username: str, password: str) -> requests.Response:
    endpoint = _create_endpoint("login")
    body = {
        "username": username,
        "password": password,
    }

    return requests.post(endpoint, json=body)


def delete_user(bearer_token: str) -> requests.Response:
    endpoint = _create_endpoint("delete_user")
    headers = _get_authorization_header(bearer_token)

    return requests.post(endpoint, headers=headers)


def get_balance(bearer_token: str) -> requests.Response:
    endpoint = _create_endpoint("get_balance")
    headers = _get_authorization_header(bearer_token)

    return requests.get(endpoint, headers=headers)


def topup(bearer_token: str, amount: float) -> requests.Response:
    endpoint = _create_endpoint("topup")
    body = {
        "amount": amount,
    }
    headers = _get_authorization_header(bearer_token)

    return requests.put(endpoint, json=body, headers=headers)


def get_stock_price(stock: str) -> requests.Response:
    endpoint = _create_endpoint("get_stock_price")
    body = {
        "stock": stock,
    }

    return requests.get(endpoint, json=body)


def buy_stock(bearer_token: str, stock: str, amount: float) -> requests.Response:
    endpoint = _create_endpoint("buy")
    body = {
        "stock": stock,
        "amount": amount
    }
    headers = _get_authorization_header(bearer_token)

    return requests.put(endpoint, json=body, headers=headers)


def sell_stock(bearer_token: str, stock: str, amount: float) -> requests.Response:
    endpoint = _create_endpoint("sell")
    body = {
        "stock": stock,
        "amount": amount
    }
    headers = _get_authorization_header(bearer_token)

    return requests.put(endpoint, json=body, headers=headers)


def get_portfolio(bearer_token: str) -> requests.Response:
    endpoint = _create_endpoint("get_portfolio")
    headers = _get_authorization_header(bearer_token)

    return requests.get(endpoint, headers=headers)


def get_net_worth(bearer_token: str) -> requests.Response:
    endpoint = _create_endpoint("get_net_worth")
    headers = _get_authorization_header(bearer_token)

    return requests.get(endpoint, headers=headers)


def submit_order(bearer_token: str, order_type: str, stock: str,
                 amount: float, trigger_price: float) -> requests.Response:
    endpoint = _create_endpoint("submit_order")
    body = {
        "order_type": order_type,
        "stock": stock,
        "amount": amount,
        "trigger_price": trigger_price
    }
    headers = _get_authorization_header(bearer_token)

    return requests.put(endpoint, json=body, headers=headers)