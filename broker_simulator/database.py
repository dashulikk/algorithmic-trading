import os
import sys

import psycopg2
from dotenv import load_dotenv

from data_models import Order

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
        self._execute_prepared_statements()

    def _execute_prepared_statements(self):
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

    def get_user_password_and_salt(self, username: str) -> tuple[str, str] | None:
        if not self.user_exists(username):
            return None

        # Prepare the SQL query using parameterized statements for safety
        query = "SELECT password_hash, salt FROM users WHERE username = %s;"

        # Execute the query with the username parameter
        self.cursor.execute(query, (username,))

        # Fetch the result
        query_result = self.cursor.fetchall()

        return query_result

    def create_user(self, username: str, hashed_password_hex: str, salt_hex: str) -> None:
        # Execute the prepared statement with provided parameters
        self.cursor.execute("EXECUTE insert_user_plan (%s, %s, %s)", (username, hashed_password_hex, salt_hex))
        self.cursor.execute("EXECUTE insert_user_balance_plan (%s)", (username,))

        self.conn.commit()

    def delete_user(self, username: str) -> None:
        if not self.user_exists(username):
            return None

        delete_from_users_query = "DELETE FROM users WHERE username = %s;"
        delete_from_balance_query = "DELETE FROM users_balance WHERE username = %s;"
        delete_from_stocks_query = "DELETE FROM users_stocks WHERE username = %s;"

        self.cursor.execute(delete_from_users_query, (username,))
        self.cursor.execute(delete_from_balance_query, (username,))
        self.cursor.execute(delete_from_stocks_query, (username,))

        self.conn.commit()

    def get_balance(self, username: str) -> list[tuple[any, any]] | None:
        if not self.user_exists(username):
            return None

        query = "SELECT balance FROM users_balance WHERE username = %s;"

        # Execute the query with the username parameter
        self.cursor.execute(query, (username,))

        # Fetch the result
        query_result = self.cursor.fetchall()

        return query_result

    def topup(self, username: str, amount: float) -> None:
        if not self.user_exists(username):
            return None

        balance = self.get_balance(username)
        query = "UPDATE users_balance SET balance = balance + %s WHERE username = %s;"

        self.cursor.execute(query, (amount, username))

        self.conn.commit()

    def get_portfolio(self, username: str) -> dict[str, float] | None:
        if not self.user_exists(username):
            return None

        stocks: dict[str, float] = {}

        query = "SELECT stock, amount FROM users_stocks WHERE username = %s;"
        self.cursor.execute(query, (username,))
        query_result = self.cursor.fetchall()

        for res in query_result:
            stocks[res[0]] = res[1]

        return stocks

    def buy_stock(self, username: str, stock: str, amount: float, total: float, fee: float) -> bool | None:
        if not self.user_exists(username):
            return False

        try:
            query_balance_subtract = "UPDATE users_balance SET balance = balance - (%s + %s) WHERE username = %s;"
            self.cursor.execute(query_balance_subtract, (total, fee, username))

            user_stocks = self.get_portfolio(username)
            if stock not in user_stocks:
                query_create_stock_entry = "INSERT INTO users_stocks VALUES (%s, %s, %s);"
                self.cursor.execute(query_create_stock_entry, (username, stock, 0))

            query_stock_buy = "UPDATE users_stocks SET amount = amount + %s WHERE username = %s AND stock = %s;"
            self.cursor.execute(query_stock_buy, (amount, username, stock))

            self.conn.commit()

            return True
        except Exception as e:
            self.conn.rollback()
            return False

    def sell_stock(self, username: str, stock: str, amount: float, total: float, fee: float) -> bool:
        if not self.user_exists(username):
            return False

        user_stocks = self.get_portfolio(username)

        if stock not in user_stocks:
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
        except Exception as e:
            self.conn.rollback()
            print(e)
            return False

    def submit_order(self, username: str, order_type: str, stock: str, amount: float, trigger_price: str):
        if not self.user_exists(username):
            return False

        try:
            query_create_stock_entry = "INSERT INTO users_orders VALUES (%s, %s, %s, %s, %s);"
            self.cursor.execute(query_create_stock_entry, (username, stock, order_type, trigger_price, amount))
            self.conn.commit()

            return True
        except Exception as e:
            self.conn.rollback()
            return False

    def get_all_orders(self) -> list[Order] | None:
        try:
            # Preparing the SQL query to select all rows from the users_orders table
            query = "SELECT * FROM users_orders;"

            # Executing the query
            self.cursor.execute(query)

            # Fetching the results
            orders_data = self.cursor.fetchall()

            # Creating a list of Order instances
            orders = [Order(id=order[0], username=order[1], stock=order[2], order_type=order[3], trigger_price=order[4],
                            amount=order[5]) for order in orders_data]

            return orders
        except Exception as e:
            print(f"An error occurred while fetching orders: {e}")
            return None

    def __del__(self):
        self.cursor.close()
        self.conn.close()
