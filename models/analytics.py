from typing import Optional, List
from pydantic import BaseModel


class SummaryItem(BaseModel):
    group: Optional[str] = None
    total_revenue: float
    total_cost: float
    gross_profit: float
    margin_percent: float
    total_orders: int
    avg_order_value: float
    return_rate: float


class SummaryResponse(BaseModel):
    items: List[SummaryItem]


class TopProduct(BaseModel):
    product_name: str
    revenue: float
    quantity: int
    profit: float