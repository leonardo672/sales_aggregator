from fastapi import APIRouter, Query
from typing import List, Optional
from models.sale import Sale
from services.storage import storage
from datetime import date

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("")
def add_sales(sales: List[Sale]):
    storage.add_sales(sales)
    return {"added": len(sales)}


@router.get("")
def get_sales(
    marketplace: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    page_size: int = 20
):
    data = storage.get_sales()

    if marketplace:
        data = [s for s in data if s.marketplace == marketplace]

    if status:
        data = [s for s in data if s.status == status]

    if date_from:
        data = [s for s in data if s.sold_at >= date_from]

    if date_to:
        data = [s for s in data if s.sold_at <= date_to]

    start = (page - 1) * page_size
    end = start + page_size

    return data[start:end]