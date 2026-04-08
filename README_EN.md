# Sales Aggregator API

## Description

This is a mini REST API service for uploading, storing, and aggregating sales data from marketplaces. It supports CSV uploads, analytics, and currency conversion.

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
├── main.py                  # Entry point of FastAPI app
├── models/
│   ├── sale.py              # Pydantic models for Sale
│   └── analytics.py         # Pydantic models for analytics responses
├── routers/
│   ├── sales.py             # CRUD endpoints for /sales
│   └── analytics.py         # Analytics endpoints: summary, top-products, CSV upload, USD conversion
├── services/
│   ├── storage.py           # In-memory or SQLite storage for sales
│   ├── aggregation.py       # Logic for summary and top-products (using Pandas)
│   ├── currency.py          # Fetch and cache USD/RUB rate
│   └── logging.py           # Structured logging (JSON format)
├── tests/
│   ├── test_endpoints.py    # pytest tests for main endpoints
│   └── sample_data.csv      # Sample CSV for testing upload
├── sales-aggregator-api-tests.zip  # ZIP file containing additional tests
├── .github/
│   └── workflows/
│       └── docker.yml       # GitHub Actions CI/CD workflow for building and pushing Docker
├── Dockerfile               # Docker container definition
├── requirements.txt         # Python dependencies
├── README.md                # Run instructions, API details
└── .gitignore               # Ignore venv, __pycache__, logs, etc.
```

---

## Running the Service

### Local Python Run

```bash
uvicorn main:app --reload
```

The server will be available at `http://localhost:8000`.

---

### Running via Docker

Build the image:

```bash
docker build -t sales-aggregator .
```

Run the container:

```bash
docker run -p 8000:8000 sales-aggregator
```

The service will be available at `http://localhost:8000`.

---

## Endpoints

### Sales

#### POST /sales

* Add one or multiple sales.
* Request body: list of sales.
* Returns: number of added records.

#### GET /sales

* Retrieve a list of sales.
* Optional query parameters: `marketplace`, `status`, `date_from`, `date_to`, `page`, `page_size`.

### Analytics

#### GET /analytics/summary

* Aggregated metrics.
* Required: `date_from`, `date_to`.
* Optional: `marketplace`, `group_by` (`marketplace` | `date` | `status`).

#### GET /analytics/top-products

* Top products for a given period.
* Required: `date_from`, `date_to`.
* Optional: `sort_by` (`revenue` | `quantity` | `profit`, default=`revenue`), `limit` (default=10).

#### GET /analytics/summary-usd

* Same as `/summary` but converted to USD.
* Uses the Central Bank of Russia API: `https://www.cbr-xml-daily.ru/daily_json.js`
* Caches exchange rate for 1 hour.

#### POST /analytics/upload-csv

* Upload CSV file with sales.
* Returns: `loaded` rows, `errors`, and details of invalid rows.

---

## CSV Example

```
order_id,marketplace,product_name,quantity,price,cost_price,status,sold_at
ORD-001,ozon,Cable USB-C,3,450.00,120.00,delivered,2025-03-01
...
```

---

## Notes

* Ensure `sold_at` dates are not in the future.
* Supported `marketplace`: `ozon`, `wildberries`, `yandex_market`.
* `price`, `cost_price` > 0; `quantity` >= 1.
* Returned or canceled orders are considered correctly in analytics.
* In-memory storage is cleared on server restart if SQLite is not enabled.

---

## Endpoint Testing

* Use Postman or any HTTP client.
* Example flow: Upload CSV → Check `/sales` → `/analytics/summary` → `/analytics/top-products` → `/analytics/summary-usd`.
* Filter, sort, and paginate using query parameters as described above.
