from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.system import AlertThresholdUpdate
from app.services.analytics import (
    get_data_sources,
    get_raw_price_records,
    get_report_assets,
    get_system_options,
    get_task_logs,
    get_thresholds,
    update_threshold,
)

router = APIRouter()


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/options")
def system_options(_user: User = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return get_system_options(db)


@router.get("/task-logs")
def system_task_logs(
    limit: int = Query(default=20, ge=1, le=100),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return {"items": get_task_logs(db, limit=limit)}


@router.get("/raw-records")
def system_raw_records(
    limit: int = Query(default=20, ge=1, le=100),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return {"items": get_raw_price_records(db, limit=limit)}


@router.get("/data-sources")
def system_data_sources(_user: User = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": get_data_sources(db)}


@router.get("/report-assets")
def system_report_assets(
    limit: int = Query(default=10, ge=1, le=50),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return {"items": get_report_assets(db, limit=limit)}


@router.get("/thresholds")
def system_thresholds(_user: User = Depends(require_authenticated_user), db: Session = Depends(get_db)):
    return {"items": get_thresholds(db)}


@router.put("/thresholds/{threshold_id}")
def system_update_threshold(
    threshold_id: int,
    payload: AlertThresholdUpdate,
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    try:
        item = update_threshold(
            db,
            threshold_id=threshold_id,
            warning_ratio=payload.warning_ratio,
            critical_ratio=payload.critical_ratio,
            std_multiplier=payload.std_multiplier,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return item
