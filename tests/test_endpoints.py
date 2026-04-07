import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from main import app

client = TestClient(app)


@pytest.fixture
def upload_sample_csv():
    with open("sample_data.csv", "rb") as f:
        files = {
            "file": ("sample_data.csv", f, "text/csv")
        }
        response = client.post("/analytics/upload-csv", files=files)

    assert response.status_code == 200
    return response.json()


def test_upload_csv(upload_sample_csv):
    data = upload_sample_csv
    assert data["loaded"] > 0
    assert data["errors"] == 0


def test_get_sales():
    response = client.get("/sales")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_summary():
    response = client.get(
        "/analytics/summary",
        params={
            "date_from": "2025-03-01",
            "date_to": "2025-03-10"
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_top_products():
    response = client.get(
        "/analytics/top-products",
        params={
            "date_from": "2025-03-01",
            "date_to": "2025-03-10",
            "sort_by": "revenue",
            "limit": 5
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5

    for item in data:
        assert "product_name" in item
        assert "revenue" in item
        assert "quantity" in item
        assert "profit" in item


def test_summary_usd():
    response = client.get(
        "/analytics/summary-usd",
        params={
            "date_from": "2025-03-01",
            "date_to": "2025-03-10"
        },
    )

    # currency API may fail
    assert response.status_code in [200, 503]