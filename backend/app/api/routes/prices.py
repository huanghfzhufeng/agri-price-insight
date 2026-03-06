from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.analytics import query_prices

router = APIRouter()


@router.get("")
def list_prices(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return query_prices(
        db=db,
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )
