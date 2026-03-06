from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import get_dashboard_data, get_rankings

router = APIRouter()


@router.get("")
def dashboard_overview(days: int = Query(default=30, ge=7, le=90), db: Session = Depends(get_db)):
    return get_dashboard_data(db, days=days)


@router.get("/rankings")
def dashboard_rankings(limit: int = Query(default=5, ge=1, le=20), db: Session = Depends(get_db)):
    return get_rankings(db, limit=limit)
