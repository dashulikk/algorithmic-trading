from trading_bots.base_trading_bot import BaseTradingBot
from utils.broker_connector import buy_stock


class MagnificentSevenTradingBot(BaseTradingBot):
    magnificent_seven_stocks = ["GOOG", "AMZN", "AAPL", "MSFT", "META", "NVDA", "TSLA"]

    def __init__(self, username: str, password: str, log_filename: str):
        super().__init__(username, password, log_filename)
        self.topup(3_000)

        for stock in MagnificentSevenTradingBot.magnificent_seven_stocks:
            buy_stock(self.auth_token, stock, 1)

        # log every 5 mins
        self.log(300)

    def run(self):
        while True:
            pass


# Clean
try:
    from utils.broker_connector import authenticate, delete_user
    from utils.broker_response_parser import parse_auth_token

    username = "magnificent_seven_bot"
    pwd = "1234"

    auth_token = parse_auth_token(authenticate(username, pwd))
    delete_user(auth_token)

except:
    pass


bot = MagnificentSevenTradingBot("magnificent_seven_bot", "1234", "magnificent_seven_bot.txt")
bot.run()
