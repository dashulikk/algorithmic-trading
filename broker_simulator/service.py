from custom_exceptions import ServiceException
from stock_info import get_stock_price
from database import Database


class Service:
    def __init__(self, db: Database):
        self.db = db

    def user_exists(self, username: str) -> bool:
        return self.db.user_exists(username)

    def get_user_password_and_salt(self, username: str) -> tuple[str, str]:
        query_result = self.db.get_user_password_and_salt(username)
        return query_result[0][0], query_result[0][1]

    def create_user(self, username: str, hashed_password_hex: str, salt_hex: str) -> None:
        self.db.create_user(username, hashed_password_hex, salt_hex)

    def delete_user(self, username: str):
        self.db.delete_user(username)

    def get_balance(self, username: str) -> float:
        query_result = self.db.get_balance(username)
        return query_result[0][0]

    def topup(self, username: str, amount: float) -> None:
        if amount <= 0:
            raise ServiceException(f"Amount has to be positive. Amount provided: {amount}")

        self.db.topup(username, amount)

    def get_portfolio(self, username: str) -> dict[str, float]:
        return self.db.get_portfolio(username)

    @staticmethod
    def _calculate_fee(total: float) -> float:
        return total * 0.001  # 0.1% of the total

    @staticmethod
    def stock_price(stock: str) -> float:
        return get_stock_price(stock)

    def buy_stock(self, username: str, stock: str, amount: float) -> None:
        if amount <= 0:
            raise ServiceException(f"Amount has to be positive. Amount provided: {amount}")

        stock_price = Service.stock_price(stock)

        total = stock_price * amount

        fee = self._calculate_fee(total)
        self.db.buy_stock(username, stock, amount, total, fee)

    def sell_stock(self, username: str, stock: str, amount: float) -> None:
        if amount <= 0:
            raise ServiceException(f"Amount has to be positive. Amount provided: {amount}")

        stock_price = Service.stock_price(stock)

        total = stock_price * amount

        fee = self._calculate_fee(total)
        self.db.sell_stock(username, stock, amount, total, fee)

    def get_net_worth(self, username: str) -> float:
        cash = self.get_balance(username)
        portfolio = self.get_portfolio(username)

        net_worth = cash
        for stock, amount in portfolio.items():
            net_worth += Service.stock_price(stock) * amount

        return net_worth

    def submit_order(self, username: str, order_type: str, stock: str, amount: float, trigger_price: float):
        self.db.submit_order(username, order_type, stock, amount, trigger_price)

        print(self.db.get_all_orders())


