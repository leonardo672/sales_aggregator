import logging
from fastapi import APIRouter, Query
from typing import List, Optional
from models.sale import Sale
from services.storage import storage
from datetime import date

router = APIRouter(prefix="/sales", tags=["Sales"])
logger = logging.getLogger(__name__)


@router.post(
    "",
    summary="Add sales records",
    description="Add multiple sales entries to the storage. Each entry must match the Sale model schema.",
    response_description="Number of sales successfully added"
)
def add_sales(sales: List[Sale]):
    """
    Example request body:
    [
        {
            "order_id": "ORD-001",
            "marketplace": "ozon",
            "product_name": "Кабель USB-C",
            "quantity": 3,
            "price": 450.0,
            "cost_price": 120.0,
            "status": "delivered",
            "sold_at": "2025-03-01"
        }
    ]
    """
    storage.add_sales(sales)
    logger.info(
        "Added sales batch",
        extra={"added_rows": len(sales)}
    )
    return {"added": len(sales)}


@router.get(
    "",
    summary="Get sales records",
    description="Fetch sales with optional filters: marketplace, status, date range. Supports pagination.",
    response_description="List of sales matching filters and pagination"
)
def get_sales(
    marketplace: Optional[str] = Query(None, description="Filter by marketplace, e.g., 'ozon', 'wildberries'"),
    status: Optional[str] = Query(None, description="Filter by status, e.g., 'delivered', 'returned'"),
    date_from: Optional[date] = Query(None, description="Filter sales from this date (inclusive)"),
    date_to: Optional[date] = Query(None, description="Filter sales up to this date (inclusive)"),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    page_size: int = Query(20, ge=1, le=100, description="Number of records per page")
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