from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import get_alerts, get_forecast

router = APIRouter()


@router.get("")
def list_alerts(db: Session = Depends(get_db)):
    return {"items": get_alerts(db)}


@router.get("/forecast")
def forecast(
    product: str = Query(default="大蒜"),
    days: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db),
):
    return get_forecast(db, product_name=product, days=days)
