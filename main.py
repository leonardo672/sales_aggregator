from services.logging import setup_logging
setup_logging()

import logging
logger = logging.getLogger(__name__)

from fastapi import FastAPI
from routers.sales import router as sales_router
from routers.analytics import router as analytics_router

app = FastAPI()

app.include_router(sales_router)
app.include_router(analytics_router)