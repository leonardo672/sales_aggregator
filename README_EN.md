# Sales Aggregator API

## Description

This is a mini-service REST API for uploading, storing, and aggregating marketplace sales data. It supports CSV uploads, analytics, and currency conversion.

---

## Requirements

* Python 3.11+
* FastAPI
* Uvicorn
* Pandas
* Pydantic
* SQLite (optional, in-memory storage supported)

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Project Structure

```
sales_aggregator/
├── main.py              # FastAPI entry point
├── models/
│   ├── sale.py          # Pydantic sale models
│   └── analytics.py     # Pydantic analytics response models
├── routers/
│   ├── sales.py         # CRUD endpoints for sales
│   └── analytics.py     # Analytics endpoints
├── services/
│   ├── storage.py       # In-memory / SQLite storage
│   ├── aggregation.py   # Aggregation logic with Pandas
│   └── currency.py      # Currency API integration
├── requirements.txt
└── README.md            # This file
```

---

## Running the Service

Start FastAPI server:

```bash
uvicorn main:app --reload
```

Server runs at `http://localhost:8000`.

---

## Endpoints

### Sales

#### POST /sales

* Add one or more sales.
* Request body: list of sales.
* Returns: number of added records.

#### GET /sales

* Retrieve sales.
* Optional query params: `marketplace`, `status`, `date_from`, `date_to`, `page`, `page_size`.

### Analytics

#### GET /analytics/summary

* Aggregated metrics.
* Required query params: `date_from`, `date_to`.
* Optional: `marketplace`, `group_by` (`marketplace` | `date` | `status`).

#### GET /analytics/top-products

* Top products for a period.
* Required: `date_from`, `date_to`.
* Optional: `sort_by` (`revenue` | `quantity` | `profit`, default=`revenue`), `limit` (default=10).

#### GET /analytics/summary-usd

* Same as `/summary` but converted to USD.
* Uses open API from Central Bank of Russia: `https://www.cbr-xml-daily.ru/daily_json.js`
* Caches rate for 1 hour.

#### POST /analytics/upload-csv

* Upload CSV file with sales.
* Returns: `loaded` rows, `errors`, and details of invalid rows.

---

## Example CSV

```
order_id,marketplace,product_name,quantity,price,cost_price,status,sold_at
ORD-001,ozon,Cable USB-C,3,450.00,120.00,delivered,2025-03-01
...
```

---

## Notes

* Ensure `sold_at` dates are not in the future.
* Valid `marketplace`: `ozon`, `wildberries`, `yandex_market`.
* `price`, `cost_price` > 0; `quantity` >= 1.
* Returned or cancelled orders are handled in analytics accordingly.
* In-memory storage resets on server restart unless SQLite is enabled.

---

## Testing Endpoints

* Use Postman or any HTTP client.
* Example: Upload CSV → Check `/sales` → `/analytics/summary` → `/analytics/top-products` → `/analytics/summary-usd`.
* Filter, sort, and paginate using query parameters as described above.
