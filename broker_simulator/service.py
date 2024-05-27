from broker_simulator.data_models import Order
from broker_simulator.custom_exceptions import ServiceException
from broker_simulator.stock_info import get_stock_price
from broker_simulator.database import Database


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

    def buy_stock(self, username: str, stock: str, amount: float, commit=True) -> None:
        if amount <= 0:
            raise ServiceException(f"Amount has to be positive. Amount provided: {amount}")

        stock_price = Service.stock_price(stock)

        total = stock_price * amount

        fee = self._calculate_fee(total)
        self.db.buy_stock(username, stock, amount, total, fee, commit=commit)

    def sell_stock(self, username: str, stock: str, amount: float, commit=True) -> None:
        if amount <= 0:
            raise ServiceException(f"Amount has to be positive. Amount provided: {amount}")

        stock_price = Service.stock_price(stock)

        total = stock_price * amount

        fee = self._calculate_fee(total)
        self.db.sell_stock(username, stock, amount, total, fee, commit=commit)

    def get_net_worth(self, username: str) -> float:
        cash = self.get_balance(username)
        portfolio = self.get_portfolio(username)

        net_worth = cash
        for stock, amount in portfolio.items():
            net_worth += Service.stock_price(stock) * amount

        return net_worth

    def submit_order(self, username: str, order_type: str, stock: str, amount: float, trigger_price: float):
        self.db.submit_order(username, order_type, stock, amount, trigger_price)

    def get_order_book(self) -> list[Order]:
        return self.db.get_all_orders()

    @staticmethod
    def can_execute_order(order: Order) -> bool:
        curr_stock_price = Service.stock_price(order.stock)
        trigger_stock_price = order.trigger_price

        if order.order_type == "limit" or order.order_type == "stop_loss":
            return curr_stock_price <= trigger_stock_price
        elif order.order_type == "take_profit":
            return curr_stock_price >= trigger_stock_price
        else:
            raise ServiceException(f"Order is of type {order.order_type}, "
                                   f"Only limit, stop_loss and take_profit orders are accepted")

    def execute_order(self, order: Order) -> None:
        if order.order_type == "limit":
            try:
                self.buy_stock(order.username, order.stock, order.amount, commit=False)
                self.db.delete_order(order.id, commit=False)
                self.db.conn.commit()
            except Exception as e:
                self.db.conn.rollback()
                raise ServiceException(f"{e}")
        elif order.order_type == "stop_loss" or order.order_type == "take_profit":
            try:
                self.sell_stock(order.username, order.stock, order.amount, commit=False)
                self.db.delete_order(order.id, commit=False)
                self.db.conn.commit()
            except Exception as e:
                self.db.conn.rollback()
                raise ServiceException(f"{e}")
        else:
            raise ServiceException(f"Order is of type {order.order_type}, "
                                   f"Only limit, stop_loss and take_profit orders are accepted")
