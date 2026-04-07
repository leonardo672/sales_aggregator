import pandas as pd
from typing import List, Optional
from models.sale import Sale


def to_df(sales: List[Sale]):
    return pd.DataFrame([s.model_dump() for s in sales])


def summary(
    sales,
    date_from,
    date_to,
    marketplace=None,
    group_by=None
):
    df = to_df(sales)

    if df.empty:
        return []

    df["sold_at"] = pd.to_datetime(df["sold_at"])

    df = df[
        (df["sold_at"] >= pd.to_datetime(date_from))
        & (df["sold_at"] <= pd.to_datetime(date_to))
    ]

    if marketplace:
        df = df[df["marketplace"] == marketplace]

    df["revenue"] = df["price"] * df["quantity"]
    df["cost"] = df["cost_price"] * df["quantity"]

    if group_by:
        grouped = df.groupby(group_by)
    else:
        grouped = [("all", df)]

    results = []

    for name, group in grouped:

        delivered = group[group["status"] == "delivered"]
        returned = group[group["status"] == "returned"]

        revenue = delivered["revenue"].sum()
        cost = delivered["cost"].sum()

        profit = revenue - cost
        orders = delivered["order_id"].nunique()

        return_rate = 0
        if len(delivered) + len(returned) > 0:
            return_rate = len(returned) / (len(delivered) + len(returned)) * 100

        results.append({
            "group": str(name),
            "total_revenue": float(revenue),
            "total_cost": float(cost),
            "gross_profit": float(profit),
            "margin_percent": float((profit / revenue * 100) if revenue else 0),
            "total_orders": int(orders),
            "avg_order_value": float(revenue / orders if orders else 0),
            "return_rate": float(return_rate)
        })

    return results


def top_products(sales, date_from, date_to, sort_by="revenue", limit=10):
    df = to_df(sales)

    if df.empty:
        return []

    df["sold_at"] = pd.to_datetime(df["sold_at"])

    df = df[
        (df["sold_at"] >= pd.to_datetime(date_from)) &
        (df["sold_at"] <= pd.to_datetime(date_to))
    ]

    if df.empty:
        return []

    df = df[df["status"] == "delivered"]

    if df.empty:
        return []

    df["revenue"] = df["price"] * df["quantity"]
    df["profit"] = (df["price"] - df["cost_price"]) * df["quantity"]

    grouped = (
        df.groupby("product_name")
        .agg(
            revenue=("revenue", "sum"),
            quantity=("quantity", "sum"),
            profit=("profit", "sum")
        )
        .reset_index()
    )

    # validate sort_by
    if sort_by not in ["revenue", "quantity", "profit"]:
        sort_by = "revenue"

    grouped = grouped.sort_values(by=sort_by, ascending=False)

    result = grouped.head(limit).to_dict("records")

    # convert numpy types to python
    for r in result:
        r["revenue"] = float(r["revenue"])
        r["quantity"] = int(r["quantity"])
        r["profit"] = float(r["profit"])

    return result