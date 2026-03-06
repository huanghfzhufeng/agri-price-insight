from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import get_raw_price_records, get_system_options, get_task_logs

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/options")
def system_options(db: Session = Depends(get_db)):
    return get_system_options(db)


@router.get("/task-logs")
def system_task_logs(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return {"items": get_task_logs(db, limit=limit)}


@router.get("/raw-records")
def system_raw_records(limit: int = Query(default=20, ge=1, le=100), db: Session = Depends(get_db)):
    return {"items": get_raw_price_records(db, limit=limit)}
