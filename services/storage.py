from typing import List
from models.sale import Sale

class Storage:
    def __init__(self):
        self.sales: List[Sale] = []

    def add_sales(self, sales: List[Sale]):
        self.sales.extend(sales)

    def get_sales(self):
        return self.sales


storage = Storage()