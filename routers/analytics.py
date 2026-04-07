from fastapi import APIRouter, HTTPException, UploadFile
from datetime import date
import pandas as pd

from services.storage import storage
from services.aggregation import summary, top_products
from services.currency import get_usd_rate
from models.sale import Sale

from fastapi import Query
from typing import Literal

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/summary")
def get_summary(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = None
):
    data = storage.get_sales()

    return summary(data, date_from, date_to, marketplace, group_by)


@router.get("/summary-usd")
def summary_usd(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = None
):
    try:
        rate = get_usd_rate()
    except:
        raise HTTPException(503, "Currency API unavailable")

    data = summary(
        storage.get_sales(),
        date_from,
        date_to,
        marketplace,
        group_by
    )

    for item in data:
        item["total_revenue"] /= rate
        item["total_cost"] /= rate
        item["gross_profit"] /= rate
        item["avg_order_value"] /= rate

    return data


@router.get("/top-products")
def top(
    date_from: date,
    date_to: date,
    sort_by: Literal["revenue", "quantity", "profit"] = Query("revenue"),
    limit: int = Query(10, ge=1, le=100)
):
    return top_products(
        storage.get_sales(),
        date_from,
        date_to,
        sort_by,
        limit
    )

@router.post("/upload-csv")
async def upload_csv(file: UploadFile):
    df = pd.read_csv(file.file)

    errors = []
    valid = []

    for i, row in df.iterrows():
        try:
            sale = Sale(**row.to_dict())
            valid.append(sale)
        except Exception as e:
            errors.append({
                "row": i + 1,
                "error": str(e)
            })

    storage.add_sales(valid)

    return {
        "loaded": len(valid),
        "errors": len(errors),
        "details": errors
    }