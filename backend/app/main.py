from fastapi import FastAPI

from app.api.agent import router as agent_router
from app.api.analysis import router as analysis_router
from app.api.database import router as database_router
from app.api.health import router as health_router
from app.api.orders import router as orders_router
from app.api.sql import router as sql_router


app = FastAPI(
    title="InsightPilot API",
    description="AI-powered ecommerce data analysis and attribution backend.",
    version="0.1.0",
)

app.include_router(health_router)
app.include_router(orders_router)
app.include_router(analysis_router)
app.include_router(database_router)
app.include_router(sql_router)
app.include_router(agent_router)
