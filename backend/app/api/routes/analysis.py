from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.db.session import get_db
from app.models.entities import User
from app.services.analysis import (
    get_analysis_overview,
    get_anomaly_analysis,
    get_monthly_comparison,
    get_region_comparison,
    get_trend_analysis,
    get_volatility_analysis,
)

router = APIRouter()


@router.get("/overview")
def analysis_overview(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_analysis_overview(db, product_name=product, market_name=market)


@router.get("/trend")
def analysis_trend(
    product: str | None = Query(default=None),
    days: int = Query(default=90, ge=30, le=365),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_trend_analysis(db, product_name=product, days=days)


@router.get("/monthly")
def analysis_monthly(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_monthly_comparison(db, product_name=product, market_name=market)


@router.get("/regions")
def analysis_regions(
    product: str | None = Query(default=None),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_region_comparison(db, product_name=product)


@router.get("/volatility")
def analysis_volatility(
    window_days: int = Query(default=30, ge=7, le=120),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_volatility_analysis(db, window_days=window_days)


@router.get("/anomalies")
def analysis_anomalies(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    days: int = Query(default=120, ge=30, le=365),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return get_anomaly_analysis(db, product_name=product, market_name=market, days=days)
