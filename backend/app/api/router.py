from fastapi import APIRouter

from app.api.routes import alerts, analysis, auth, dashboard, prices, system

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(analysis.router, prefix="/analysis", tags=["analysis"])
api_router.include_router(alerts.router, prefix="/alerts", tags=["alerts"])
