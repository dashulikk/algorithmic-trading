import os
import sys
from typing import Tuple, Dict

import psycopg2
from dotenv import load_dotenv

from stock_info import get_stock_price

load_dotenv()  # load .env variables

postgres_connection = psycopg2.extensions.connection
postgres_cursor = psycopg2.extensions.cursor


class Database:
    def __init__(self):
        dbname = os.environ['RDS_DB_NAME']
        user = os.environ['RDS_USERNAME']
        host = os.environ['RDS_ENDPOINT']
        password = os.environ['RDS_PASSWORD']
        port = os.environ['RDS_PORT']

        sys.stdout.flush()

        self.conn: postgres_connection = psycopg2.connect(database=dbname,
                                                          user=user,
                                                          host=host,
                                                          password=password,
                                                          port=port)

        self.cursor: postgres_cursor = self.conn.cursor()

        self.cursor.execute("""
                                    PREPARE insert_user_plan AS 
                                    INSERT INTO users (username, password_hash, salt) 
                                    VALUES ($1, $2, $3);
                                """)

        self.cursor.execute("""
                                    PREPARE insert_user_balance_plan AS 
                                    INSERT INTO users_balance (username, balance) 
                                    VALUES ($1, 0);
                                """)

    def user_exists(self, username: str) -> bool:
        # Prepare the SQL query using parameterized statements for safety
        query = "SELECT EXISTS(SELECT 1 FROM users WHERE username = %s);"

        # Execute the query with the username parameter
        self.cursor.execute(query, (username,))

        # Fetch the result
        (exists,) = self.cursor.fetchone()

        return exists

    def get_user_password_and_salt(self, username: str) -> Tuple[str, str]:
        # Prepare the SQL query using parameterized statements for safety
        query = "SELECT password_hash, salt FROM users WHERE username = %s;"

        # Execute the query with the username parameter
        self.cursor.execute(query, (username,))

        # Fetch the result
        query_result = self.cursor.fetchall()

        return query_result[0][0], query_result[0][1]

    def create_user(self, username: str, hashed_password_hex: str, salt_hex: str) -> None:
        # Execute the prepared statement with provided parameters
        self.cursor.execute("EXECUTE insert_user_plan (%s, %s, %s)", (username, hashed_password_hex, salt_hex))
        self.cursor.execute("EXECUTE insert_user_balance_plan (%s)", (username,))

        self.conn.commit()

    def delete_user(self, username: str) -> None:
        delete_from_users_query = "DELETE FROM users WHERE username = %s;"
        delete_from_balance_query = "DELETE FROM users_balance WHERE username = %s;"
        delete_from_stocks_query = "DELETE FROM users_stocks WHERE username = %s;"

        self.cursor.execute(delete_from_users_query, (username,))
        self.cursor.execute(delete_from_balance_query, (username,))
        self.cursor.execute(delete_from_stocks_query, (username,))


        self.conn.commit()

    def get_balance(self, username: str) -> float:
        query = "SELECT balance FROM users_balance WHERE username = %s;"

        # Execute the query with the username parameter
        self.cursor.execute(query, (username,))

        # Fetch the result
        query_result = self.cursor.fetchall()

        return query_result[0][0]

    def topup(self, username: str, amount: float) -> None:
        balance = self.get_balance(username)
        query = "UPDATE users_balance SET balance = %s WHERE username = %s;"

        self.cursor.execute(query, (balance + amount, username))

        self.conn.commit()

    def get_stocks_by_user(self, username: str) -> Dict[str, float]:
        stocks: Dict[str, float] = {}

        query = "SELECT stock, amount FROM users_stocks WHERE username = %s;"
        self.cursor.execute(query, (username,))
        query_result = self.cursor.fetchall()

        for res in query_result:
            stocks[res[0]] = res[1]

        return stocks

    @staticmethod
    def _calculate_fee(total: float) -> float:
        return total * 0.001  # 0.1% of the total

    def buy_stock(self, username: str, stock: str, amount: float) -> bool:
        if not self.user_exists(username) or amount <= 0:
            return False

        stock_price = get_stock_price(stock)

        total = stock_price * amount

        fee = self._calculate_fee(total)

        try:
            query_balance_subtract = "UPDATE users_balance SET balance = balance - (%s + %s) WHERE username = %s;"
            self.cursor.execute(query_balance_subtract, (total, fee, username))

            user_stocks = self.get_stocks_by_user(username)
            if stock not in user_stocks:
                query_create_stock_entry = "INSERT INTO users_stocks VALUES (%s, %s, %s);"
                self.cursor.execute(query_create_stock_entry, (username, stock, 0))

            query_stock_buy = "UPDATE users_stocks SET amount = amount + %s WHERE username = %s AND stock = %s;"
            self.cursor.execute(query_stock_buy, (amount, username, stock))

            self.conn.commit()

            return True
        except Exception as e:
            self.conn.rollback()
            print(e)
            return False

    def sell_stock(self, username: str, stock: str, amount: float) -> bool:
        if not self.user_exists(username) or amount <= 0:
            return False

        user_stocks = self.get_stocks_by_user(username)

        if stock not in user_stocks:
            return False

        stock_price = get_stock_price(stock)

        total = stock_price * amount
        fee = self._calculate_fee(total)

        if total < 0:
            return False

        try:
            query_balance_subtract = "UPDATE users_balance SET balance = balance + (%s - %s) WHERE username = %s;"
            self.cursor.execute(query_balance_subtract, (total, fee, username))

            query_stock_buy = "UPDATE users_stocks SET amount = amount - %s WHERE username = %s AND stock = %s;"
            self.cursor.execute(query_stock_buy, (amount, username, stock))

            query_remove_stock_if_zero = "DELETE FROM users_stocks WHERE username = %s AND stock = %s AND amount = 0;"
            self.cursor.execute(query_remove_stock_if_zero, (username, stock))

            self.conn.commit()

            return True
        except Exception:
            self.conn.rollback()
            print(e)
            return False

    def __del__(self):
        self.cursor.close()
        self.conn.close()
