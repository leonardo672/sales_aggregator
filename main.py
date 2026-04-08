from services.logging import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from routers.sales import router as sales_router
from routers.analytics import router as analytics_router

app = FastAPI(
    title="Sales Aggregator API",
    description="Мини-сервис для загрузки, хранения и анализа данных по продажам с маркетплейсов.",
    version="1.0.0",
    contact={
        "name": "Homam Al Safadi",
        "email": "support@Safadi.com"
    },
    openapi_tags=[
        {
            "name": "Sales",
            "description": "Эндпоинты для загрузки и запроса данных о продажах"
        },
        {
            "name": "Analytics",
            "description": "Эндпоинты для агрегации и анализа продаж"
        }
    ]
)

# Include routers
app.include_router(sales_router)
app.include_router(analytics_router)