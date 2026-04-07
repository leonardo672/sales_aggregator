from datetime import date
from typing import Literal
from pydantic import BaseModel, field_validator


Marketplace = Literal["ozon", "wildberries", "yandex_market"]
Status = Literal["delivered", "returned", "cancelled"]


class Sale(BaseModel):
    order_id: str
    marketplace: Marketplace
    product_name: str
    quantity: int
    price: float
    cost_price: float
    status: Status
    sold_at: date

    @field_validator("price", "cost_price")
    @classmethod
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError("price and cost_price must be > 0")
        return v

    @field_validator("quantity")
    @classmethod
    def validate_quantity(cls, v):
        if v < 1:
            raise ValueError("quantity must be >= 1")
        return v

    @field_validator("sold_at")
    @classmethod
    def validate_date(cls, v):
        if v > date.today():
            raise ValueError("sold_at cannot be in the future")
        return v