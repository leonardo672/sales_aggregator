import logging
from fastapi import APIRouter, HTTPException, UploadFile, Query
from typing import Literal
from datetime import date
import pandas as pd

from services.storage import storage
from services.aggregation import summary, top_products
from services.currency import get_usd_rate
from models.sale import Sale

router = APIRouter(prefix="/analytics", tags=["Analytics"])
logger = logging.getLogger(__name__)


@router.get("/summary", summary="Get aggregated sales summary")
def get_summary(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = None
):
    """
    Returns aggregated sales metrics for the given date range, optionally filtered by marketplace
    and grouped by a field.
    """
    logger.info(
        "Summary request started",
        extra={"date_from": str(date_from), "date_to": str(date_to), "marketplace": marketplace, "group_by": group_by}
    )
    try:
        data = storage.get_sales()
        result = summary(data, date_from, date_to, marketplace, group_by)
        logger.info("Summary request finished", extra={"total_groups": len(result)})
        return result
    except Exception as e:
        logger.error("Summary request failed", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary-usd", summary="Get aggregated sales summary in USD")
def summary_usd(
    date_from: date,
    date_to: date,
    marketplace: str | None = None,
    group_by: str | None = None
):
    """
    Returns aggregated sales metrics converted to USD using current exchange rate.
    """
    logger.info(
        "Summary USD request started",
        extra={"date_from": str(date_from), "date_to": str(date_to), "marketplace": marketplace, "group_by": group_by}
    )
    try:
        rate = get_usd_rate()
    except Exception:
        logger.error("Currency API unavailable", exc_info=True)
        raise HTTPException(503, "Currency API unavailable")

    try:
        data = summary(storage.get_sales(), date_from, date_to, marketplace, group_by)
        for item in data:
            item["total_revenue"] /= rate
            item["total_cost"] /= rate
            item["gross_profit"] /= rate
            item["avg_order_value"] /= rate
        logger.info("Summary USD request finished", extra={"total_groups": len(data), "usd_rate": rate})
        return data
    except Exception as e:
        logger.error("Summary USD processing failed", exc_info=True)
        raise HTTPException(500, str(e))


@router.get("/top-products", summary="Get top-selling products")
def top(
    date_from: date,
    date_to: date,
    sort_by: Literal["revenue", "quantity", "profit"] = Query("revenue"),
    limit: int = Query(10, ge=1, le=100)
):
    """
    Returns top products by revenue, quantity, or profit within a date range.
    """
    logger.info(
        "Top products request started",
        extra={"date_from": str(date_from), "date_to": str(date_to), "sort_by": sort_by, "limit": limit}
    )
    try:
        result = top_products(storage.get_sales(), date_from, date_to, sort_by, limit)
        logger.info("Top products request finished", extra={"returned": len(result)})
        return result
    except Exception as e:
        logger.error("Top products request failed", exc_info=True)
        raise HTTPException(500, str(e))


@router.post("/upload-csv", summary="Upload sales CSV or Excel file")
async def upload_csv(file: UploadFile):
    """
    Uploads a CSV or Excel file of sales. Supports .csv (UTF-8 or CP1251) and .xlsx.
    Returns number of loaded rows and any validation errors.
    """
    logger.info("CSV upload started", extra={"file_name": file.filename})

    try:
        # Excel vs CSV auto-detect
        if file.filename.endswith(".xlsx"):
            df = pd.read_excel(file.file)
        else:
            try:
                df = pd.read_csv(file.file, sep=None, engine="python", encoding="cp1251")
            except Exception:
                file.file.seek(0)
                df = pd.read_csv(file.file, sep=None, engine="python", encoding="utf-8")

        logger.info("File read into DataFrame", extra={"columns": df.columns.tolist()})

        # normalize columns
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

        # convert date column
        if "sold_at" in df.columns:
            df["sold_at"] = pd.to_datetime(df["sold_at"]).dt.date
        else:
            raise HTTPException(400, "Missing 'sold_at' column in uploaded file")

    except Exception as e:
        logger.error("Failed to read uploaded file", exc_info=True)
        raise HTTPException(400, str(e))

    errors = []
    valid = []

    for i, row in df.iterrows():
        try:
            sale = Sale(**row.to_dict())
            valid.append(sale)
        except Exception as e:
            errors.append({"row": i + 2, "error": str(e)})
            logger.warning("Row failed validation", extra={"row": i + 2, "error": str(e)})

    storage.add_sales(valid)
    logger.info(
        "CSV upload finished",
        extra={"loaded_rows": len(valid), "error_rows": len(errors)}
    )

    return {"loaded": len(valid), "errors": len(errors), "details": errors}