from fastapi import APIRouter, Query
from typing import List, Optional
from models.sale import Sale
from services.storage import storage
from datetime import date
import logging

router = APIRouter(prefix="/sales", tags=["Sales"])
logger = logging.getLogger(__name__)


@router.post("")
def add_sales(sales: List[Sale]):
    storage.add_sales(sales)
    logger.info(
        "Added sales batch",
        extra={"added_rows": len(sales)}
    )
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

    page_data = data[start:end]

    logger.info(
        "Fetched sales",
        extra={
            "marketplace": marketplace,
            "status": status,
            "date_from": str(date_from) if date_from else None,
            "date_to": str(date_to) if date_to else None,
            "page": page,
            "page_size": page_size,
            "returned_rows": len(page_data)
        }
    )

    return page_data