from datetime import date
import csv
from io import StringIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import require_authenticated_user
from app.db.session import get_db
from app.models.entities import User
from app.services.analytics import list_price_rows, query_prices

router = APIRouter()


@router.get("")
def list_prices(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    return query_prices(
        db=db,
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get("/export")
def export_prices(
    product: str | None = Query(default=None),
    market: str | None = Query(default=None),
    category: str | None = Query(default=None),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
    _user: User = Depends(require_authenticated_user),
    db: Session = Depends(get_db),
):
    rows = list_price_rows(
        db=db,
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=None,
        offset=0,
    )
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["日期", "品名", "分类", "市场", "地区", "均价", "最低价", "最高价", "单位", "来源"])
    for row in rows:
        writer.writerow([row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]])

    csv_content = buffer.getvalue()
    buffer.close()
    return StreamingResponse(
        iter([csv_content]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment; filename=price-records.csv"},
    )
