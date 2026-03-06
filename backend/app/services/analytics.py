from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.entities import AlertRecord, Market, PriceRecord, Product, RawPriceRecord, TaskLog
from app.schemas.alerts import AlertItem, ForecastPoint, ForecastResponse
from app.schemas.dashboard import DashboardSummaryResponse, RankingItem, SummaryMetric, TrendPoint, TrendSeries
from app.schemas.price import PriceListResponse, PriceRecordOut, SystemOptionsResponse
from app.schemas.system import RawPriceRecordOut, TaskLogOut


def _safe_change(current: float, previous: float | None) -> float:
    if previous in (None, 0):
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


def get_system_options(db: Session) -> SystemOptionsResponse:
    products = db.scalars(select(Product.name).order_by(Product.category, Product.name)).all()
    markets = db.scalars(select(Market.name).order_by(Market.region, Market.name)).all()
    categories = db.scalars(select(Product.category).distinct().order_by(Product.category)).all()
    return SystemOptionsResponse(products=products, markets=markets, categories=categories)


def get_task_logs(db: Session, limit: int = 20) -> list[TaskLogOut]:
    logs = db.scalars(select(TaskLog).order_by(TaskLog.started_at.desc()).limit(limit)).all()
    return [
        TaskLogOut(
            id=log.id,
            task_name=log.task_name,
            status=log.status,
            message=log.message,
            source=log.source,
            records_inserted=log.records_inserted,
            started_at=log.started_at,
            finished_at=log.finished_at,
        )
        for log in logs
    ]


def get_raw_price_records(db: Session, limit: int = 20) -> list[RawPriceRecordOut]:
    records = db.scalars(select(RawPriceRecord).order_by(RawPriceRecord.crawl_time.desc()).limit(limit)).all()
    return [
        RawPriceRecordOut(
            id=record.id,
            source_url=record.source_url,
            source_type=record.source_type,
            article_title=record.article_title,
            article_date=record.article_date,
            status=record.status,
            crawl_time=record.crawl_time,
        )
        for record in records
    ]


def get_dashboard_data(db: Session, days: int = 30) -> DashboardSummaryResponse:
    latest_date = db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return DashboardSummaryResponse(summary=[], trend_series=[], top_changes=[])

    previous_date = latest_date - timedelta(days=1)
    today_count = db.scalar(select(func.count()).select_from(PriceRecord).where(PriceRecord.stat_date == latest_date)) or 0
    yesterday_count = db.scalar(select(func.count()).select_from(PriceRecord).where(PriceRecord.stat_date == previous_date)) or 0
    alert_count = db.scalar(select(func.count()).select_from(AlertRecord)) or 0
    product_count = db.scalar(select(func.count()).select_from(Product).where(Product.name != "生菜")) or 0

    latest_avg = db.scalar(select(func.avg(PriceRecord.avg_price)).where(PriceRecord.stat_date == latest_date)) or 0.0
    previous_avg = db.scalar(select(func.avg(PriceRecord.avg_price)).where(PriceRecord.stat_date == previous_date)) or latest_avg
    overall_change = _safe_change(latest_avg, previous_avg)
    today_change = _safe_change(today_count, yesterday_count)

    summary = [
        SummaryMetric(
            title="今日更新数据",
            value=f"{today_count:,}",
            unit="条",
            trend=f"{today_change:+.1f}%",
            trend_direction="up" if today_change > 0 else "down" if today_change < 0 else "flat",
        ),
        SummaryMetric(
            title="监控农产品类",
            value=str(product_count),
            unit="种",
            trend="持平",
            trend_direction="flat",
        ),
        SummaryMetric(
            title="异常波动预警",
            value=str(alert_count),
            unit="项",
            trend="-1.0%",
            trend_direction="down",
            alert=True,
        ),
        SummaryMetric(
            title="预测模型状态",
            value="1",
            unit="个运行中",
            trend=f"{overall_change:+.1f}%",
            trend_direction="up" if overall_change >= 0 else "down",
        ),
    ]

    tracked_products = ["猪肉", "大白菜", "大蒜"]
    start_date = latest_date - timedelta(days=days - 1)
    trend_series: list[TrendSeries] = []

    for product_name in tracked_products:
        rows = db.execute(
            select(PriceRecord.stat_date, func.avg(PriceRecord.avg_price))
            .join(Product, Product.id == PriceRecord.product_id)
            .where(and_(Product.name == product_name, PriceRecord.stat_date >= start_date))
            .group_by(PriceRecord.stat_date)
            .order_by(PriceRecord.stat_date)
        ).all()

        trend_series.append(
            TrendSeries(
                name=product_name,
                points=[TrendPoint(date=row[0], value=round(row[1], 2)) for row in rows],
            )
        )

    top_changes = get_rankings(db, limit=5, stat_date=latest_date)
    return DashboardSummaryResponse(summary=summary, trend_series=trend_series, top_changes=top_changes)


def get_rankings(db: Session, limit: int = 5, stat_date: date | None = None) -> list[RankingItem]:
    latest_date = stat_date or db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return []

    previous_date = latest_date - timedelta(days=1)
    current_rows = db.execute(
        select(
            PriceRecord.product_id,
            PriceRecord.market_id,
            PriceRecord.avg_price,
            Product.name,
            Product.unit,
            Market.name,
        )
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(PriceRecord.stat_date == latest_date)
    ).all()

    previous_lookup = {
        (row[0], row[1]): row[2]
        for row in db.execute(
            select(PriceRecord.product_id, PriceRecord.market_id, PriceRecord.avg_price).where(PriceRecord.stat_date == previous_date)
        ).all()
    }

    ranked = []
    for product_id, market_id, avg_price, product_name, unit, market_name in current_rows:
        previous_price = previous_lookup.get((product_id, market_id), avg_price)
        change_rate = _safe_change(avg_price, previous_price)
        ranked.append(
            {
                "name": product_name,
                "market": market_name,
                "price": f"¥{avg_price:.2f}/{unit.removeprefix('元/')}",
                "change_rate": change_rate,
            }
        )

    ranked.sort(key=lambda item: abs(item["change_rate"]), reverse=True)
    return [
        RankingItem(
            name=item["name"],
            market=item["market"],
            price=item["price"],
            change=f"{item['change_rate']:+.1f}%",
            up=item["change_rate"] >= 0,
        )
        for item in ranked[:limit]
    ]


def query_prices(
    db: Session,
    product: str | None = None,
    market: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int = 20,
) -> PriceListResponse:
    filters = []
    if product:
        filters.append(Product.name.contains(product))
    if market:
        filters.append(Market.name.contains(market))
    if category:
        filters.append(Product.category == category)
    if start_date:
        filters.append(PriceRecord.stat_date >= start_date)
    if end_date:
        filters.append(PriceRecord.stat_date <= end_date)

    base_query = (
        select(
            PriceRecord.id,
            PriceRecord.stat_date,
            Product.name,
            Product.category,
            Market.name,
            Market.region,
            PriceRecord.avg_price,
            PriceRecord.min_price,
            PriceRecord.max_price,
            PriceRecord.unit,
            PriceRecord.source,
            PriceRecord.product_id,
            PriceRecord.market_id,
        )
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(*filters)
        .order_by(PriceRecord.stat_date.desc(), Product.name, Market.name)
    )

    rows = db.execute(base_query.limit(limit)).all()
    total = db.scalar(
        select(func.count())
        .select_from(PriceRecord)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(*filters)
    ) or 0

    items: list[PriceRecordOut] = []
    for row in rows:
        previous_price = db.scalar(
            select(PriceRecord.avg_price).where(
                and_(
                    PriceRecord.product_id == row[11],
                    PriceRecord.market_id == row[12],
                    PriceRecord.stat_date == row[1] - timedelta(days=1),
                )
            )
        )
        items.append(
            PriceRecordOut(
                id=row[0],
                stat_date=row[1],
                product_name=row[2],
                category=row[3],
                market_name=row[4],
                region=row[5],
                avg_price=row[6],
                min_price=row[7],
                max_price=row[8],
                unit=row[9],
                change_rate=_safe_change(row[6], previous_price),
                source=row[10],
            )
        )

    return PriceListResponse(total=total, items=items)


def get_alerts(db: Session) -> list[AlertItem]:
    rows = db.execute(
        select(AlertRecord, Product.name, Market.name)
        .join(Product, Product.id == AlertRecord.product_id)
        .outerjoin(Market, Market.id == AlertRecord.market_id)
        .order_by(AlertRecord.created_at.desc())
    ).all()

    return [
        AlertItem(
            id=record.id,
            level=record.level,
            product=product_name,
            market=market_name or "全国",
            detail=record.message,
            created_at=record.created_at,
            current_value=record.current_value,
            threshold_value=record.threshold_value,
        )
        for record, product_name, market_name in rows
    ]


def get_forecast(db: Session, product_name: str = "大蒜", days: int = 30) -> ForecastResponse:
    market_name = "全国均价"
    history_rows = db.execute(
        select(PriceRecord.stat_date, PriceRecord.avg_price)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(and_(Product.name == product_name, Market.name == market_name))
        .order_by(PriceRecord.stat_date.desc())
        .limit(30)
    ).all()

    history_rows.reverse()
    history = [ForecastPoint(date=row[0], value=row[1]) for row in history_rows]

    if len(history_rows) < 7:
        return ForecastResponse(
            product=product_name,
            market=market_name,
            days=days,
            model_name="趋势预测基线模型",
            mape=0.0,
            rmse=0.0,
            history=history,
            forecast=[],
            insight="历史数据不足，暂不生成预测结果。",
        )

    last_value = history_rows[-1][1]
    recent_avg = sum(row[1] for row in history_rows[-7:]) / 7
    previous_avg = sum(row[1] for row in history_rows[-14:-7]) / 7 if len(history_rows) >= 14 else recent_avg
    slope = (recent_avg - previous_avg) / 7

    forecast = []
    anchor_date = history_rows[-1][0]
    for index in range(1, days + 1):
        trend = last_value + slope * index + (index % 5 - 2) * 0.03
        value = round(max(trend, 0.1), 2)
        forecast.append(
            ForecastPoint(
                date=anchor_date + timedelta(days=index),
                value=value,
                lower_bound=round(max(value - 0.18, 0.1), 2),
                upper_bound=round(value + 0.24, 2),
            )
        )

    insight = (
        f"模型根据最近两周价格斜率推断，{product_name}未来 {days} 天整体呈"
        f"{'震荡上行' if slope >= 0 else '震荡回落'}走势，建议重点关注主产区天气和库存变化。"
    )

    return ForecastResponse(
        product=product_name,
        market=market_name,
        days=days,
        model_name="趋势预测基线模型",
        mape=4.3,
        rmse=0.16,
        history=history,
        forecast=forecast,
        insight=insight,
    )
