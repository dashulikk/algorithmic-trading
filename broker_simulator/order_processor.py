import time

from database import Database
from service import Service

db = Database()
service = Service(db)

FREQUENCY = 100


def process_orders():
    try:
        orders = db.get_all_orders()
        for order in orders:
            if service.can_execute_order(order):
                service.execute_order(order)
    except Exception as e:
        print(f"Error processing orders: {e}")


while True:
    process_orders()

    # save CPU resources, process orders only every 100 seconds
    time.sleep(FREQUENCY)