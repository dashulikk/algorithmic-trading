import pandas as pd
import random
import time
from trading_bots.base_trading_bot import BaseTradingBot
from utils.broker_connector import buy_stock, sell_stock, get_stock_price, authenticate, delete_user, get_balance, \
    get_portfolio
from utils.broker_response_parser import parse_auth_token, parse_stock_price, parse_balance, parse_portfolio


class RandomTradingBot(BaseTradingBot):
    def __init__(self, username: str, password: str, log_filename: str):
        super().__init__(username, password, log_filename)

        self.operations = ["BUY", "SELL"]
        self.stocks = pd.read_csv("trading_bots/stock_symbols.csv")["Symbol"].array

        self.topup(1_000)

        # log every 100 seconds
        self.log(100)

    def run(self):
        while True:
            operation = random.choice(self.operations)

            if operation == "BUY":
                self.random_buy_operation()
            elif operation == "SELL":
                self.random_sell_operation()

    def random_buy_operation(self):
        valid_stock_found = False

        stock = None
        stock_price = None

        while not valid_stock_found:
            try:
                stock = random.choice(self.stocks)
                stock_price = parse_stock_price(get_stock_price(stock))
                valid_stock_found = True
            except:
                pass

        balance = parse_balance(get_balance(self.auth_token))
        max_amount_to_buy = balance / stock_price

        if max_amount_to_buy != 0:
            buy_amount = random.uniform(0, max_amount_to_buy)
            buy_stock(self.auth_token, stock, buy_amount)

    def random_sell_operation(self):
        portfolio = parse_portfolio(get_portfolio(self.auth_token))
        portfolio_stocks = list(portfolio.keys())

        if len(portfolio_stocks) != 0:
            stock = random.choice(portfolio_stocks)
            sell_amount = random.uniform(0, portfolio[stock])
            sell_stock(self.auth_token, stock, sell_amount)


# Clean
try:
    username = "random_bot"
    pwd = "1234"

    auth_token = parse_auth_token(authenticate(username, pwd))
    delete_user(auth_token)

except:
    pass

bot = RandomTradingBot("random_bot", "1234", "random_bot.txt")
bot.run()
