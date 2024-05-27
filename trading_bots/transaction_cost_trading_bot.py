from trading_bots.base_trading_bot import BaseTradingBot
from utils.broker_connector import buy_stock, sell_stock


class TransactionCostTradingBot(BaseTradingBot):
    stock = "MSFT"
    num_transactions = 1_000

    def __init__(self, username: str, password: str, log_filename: str):
        super().__init__(username, password, log_filename)
        self.topup(1_000)

    def run(self):
        for _ in range(TransactionCostTradingBot.num_transactions):
            buy_stock(self.auth_token, TransactionCostTradingBot.stock, 1)
            sell_stock(self.auth_token, TransactionCostTradingBot.stock, 1)
            self.logger.log_manual()


bot = TransactionCostTradingBot("transaction_cost_bot", "1234", "no_transaction_cost_bot.txt")
bot.run()
