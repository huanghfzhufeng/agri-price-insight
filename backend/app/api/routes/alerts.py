from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.db.session import get_db
from app.models.entities import User
from app.services.analytics import get_alerts, get_forecast

router = APIRouter()


@router.get("")
def list_alerts(_user: User = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": get_alerts(db)}


@router.get("/forecast")
def forecast(
    product: str = Query(default="大蒜"),
    days: int = Query(default=30, ge=7, le=90),
    model: str | None = Query(default=None),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_forecast(db, product_name=product, days=days, model_key=model)
