from __future__ import annotations

from collections import defaultdict
from datetime import date, timedelta
from statistics import mean, pstdev

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.entities import Market, PriceRecord, Product
from app.schemas.analysis import (
    AnalysisMetric,
    AnalysisOverviewResponse,
    AnalysisSeries,
    AnalysisSeriesPoint,
    AnomalyItem,
    AnomalyResponse,
    MonthlyComparisonPoint,
    MonthlyComparisonResponse,
    RegionComparisonItem,
    RegionComparisonResponse,
    TrendAnalysisResponse,
    VolatilityItem,
    VolatilityResponse,
)


def _safe_change(current: float, previous: float | None) -> float:
    if previous in (None, 0):
        return 0.0
    return round(((current - previous) / previous) * 100, 2)


def _resolve_product_name(db: Session, preferred_name: str | None = None) -> str:
    if preferred_name:
        return preferred_name
    return db.scalar(select(Product.name).order_by(Product.category, Product.name).limit(1)) or "猪肉"


def _resolve_market_name(db: Session, preferred_name: str | None = None) -> str:
    if preferred_name:
        return preferred_name
    return db.scalar(select(Market.name).order_by(Market.region, Market.name).limit(1)) or "全国均价"


def _load_product_market_series(db: Session, product_name: str, market_name: str, days: int = 420) -> list[tuple[date, float]]:
    latest_date = db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return []
    start_date = latest_date - timedelta(days=days - 1)
    rows = db.execute(
        select(PriceRecord.stat_date, PriceRecord.avg_price)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(
            and_(
                Product.name == product_name,
                Market.name == market_name,
                PriceRecord.stat_date >= start_date,
            )
        )
        .order_by(PriceRecord.stat_date)
    ).all()
    return [(row[0], row[1]) for row in rows]


def _calculate_iqr_bounds(values: list[float]) -> tuple[float, float]:
    if len(values) < 4:
        current_mean = mean(values) if values else 0.0
        spread = pstdev(values) if len(values) > 1 else max(current_mean * 0.08, 0.2)
        return round(current_mean - 2 * spread, 3), round(current_mean + 2 * spread, 3)

    ordered = sorted(values)
    q1_index = int((len(ordered) - 1) * 0.25)
    q3_index = int((len(ordered) - 1) * 0.75)
    q1 = ordered[q1_index]
    q3 = ordered[q3_index]
    iqr = q3 - q1
    return round(q1 - 1.5 * iqr, 3), round(q3 + 1.5 * iqr, 3)


def get_analysis_overview(db: Session, product_name: str | None = None, market_name: str | None = None) -> AnalysisOverviewResponse:
    resolved_product = _resolve_product_name(db, product_name)
    resolved_market = _resolve_market_name(db, market_name)
    series = _load_product_market_series(db, resolved_product, resolved_market, days=420)

    if not series:
        return AnalysisOverviewResponse(product=resolved_product, market=resolved_market, latest_date=None, metrics=[])

    latest_date, latest_value = series[-1]
    previous_value = series[-2][1] if len(series) > 1 else latest_value
    recent_values = [value for _, value in series[-30:]]
    prior_values = [value for _, value in series[-60:-30]]
    rolling_mean = round(mean(recent_values), 2)
    previous_rolling_mean = round(mean(prior_values), 2) if prior_values else rolling_mean

    latest_month = latest_date.strftime("%Y-%m")
    previous_month_date = (latest_date.replace(day=1) - timedelta(days=1))
    previous_month = previous_month_date.strftime("%Y-%m")
    same_month_last_year = latest_date.replace(year=latest_date.year - 1).strftime("%Y-%m")

    monthly_lookup: dict[str, list[float]] = defaultdict(list)
    for point_date, value in series:
        monthly_lookup[point_date.strftime("%Y-%m")].append(value)

    current_month_avg = round(mean(monthly_lookup[latest_month]), 2)
    previous_month_avg = round(mean(monthly_lookup[previous_month]), 2) if monthly_lookup[previous_month] else current_month_avg
    last_year_avg = round(mean(monthly_lookup[same_month_last_year]), 2) if monthly_lookup[same_month_last_year] else current_month_avg
    volatility = round((pstdev(recent_values) / rolling_mean) * 100, 2) if len(recent_values) > 1 and rolling_mean else 0.0

    anomaly_bounds = _calculate_iqr_bounds(recent_values)
    anomaly_count = sum(1 for value in recent_values if value < anomaly_bounds[0] or value > anomaly_bounds[1])

    metrics = [
        AnalysisMetric(title="最新价格", value=round(latest_value, 2), unit="元", change=_safe_change(latest_value, previous_value), change_label="较昨日"),
        AnalysisMetric(title="30日均价", value=rolling_mean, unit="元", change=_safe_change(rolling_mean, previous_rolling_mean), change_label="较前30日"),
        AnalysisMetric(title="环比变化", value=_safe_change(current_month_avg, previous_month_avg), unit="%", change_label="较上月"),
        AnalysisMetric(title="同比变化", value=_safe_change(current_month_avg, last_year_avg), unit="%", change_label="较去年同期"),
        AnalysisMetric(title="波动率", value=volatility, unit="%", change_label="近30日"),
        AnalysisMetric(title="异常点数", value=float(anomaly_count), unit="个", change_label="近30日"),
    ]

    return AnalysisOverviewResponse(
        product=resolved_product,
        market=resolved_market,
        latest_date=latest_date,
        metrics=metrics,
    )


def get_trend_analysis(db: Session, product_name: str | None = None, days: int = 90) -> TrendAnalysisResponse:
    resolved_product = _resolve_product_name(db, product_name)
    latest_date = db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return TrendAnalysisResponse(product=resolved_product, days=days, series=[])

    start_date = latest_date - timedelta(days=days - 1)
    rows = db.execute(
        select(Market.name, PriceRecord.stat_date, PriceRecord.avg_price)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(and_(Product.name == resolved_product, PriceRecord.stat_date >= start_date))
        .order_by(Market.name, PriceRecord.stat_date)
    ).all()

    bucket: dict[str, list[AnalysisSeriesPoint]] = defaultdict(list)
    for market_name, stat_date, avg_price in rows:
        bucket[market_name].append(AnalysisSeriesPoint(date=stat_date, value=round(avg_price, 2)))

    series = [AnalysisSeries(name=market_name, points=points) for market_name, points in bucket.items()]
    return TrendAnalysisResponse(product=resolved_product, days=days, series=series)


def get_monthly_comparison(db: Session, product_name: str | None = None, market_name: str | None = None) -> MonthlyComparisonResponse:
    resolved_product = _resolve_product_name(db, product_name)
    resolved_market = _resolve_market_name(db, market_name)
    series = _load_product_market_series(db, resolved_product, resolved_market, days=420)

    grouped: dict[str, list[float]] = defaultdict(list)
    for stat_date, value in series:
        grouped[stat_date.strftime("%Y-%m")].append(value)

    months = sorted(grouped.keys())[-12:]
    points: list[MonthlyComparisonPoint] = []
    for month in months:
        year, month_number = map(int, month.split("-"))
        previous_month_date = date(year, month_number, 1) - timedelta(days=1)
        previous_month_key = previous_month_date.strftime("%Y-%m")
        previous_year_key = f"{year - 1:04d}-{month_number:02d}"
        current_avg = round(mean(grouped[month]), 2)
        previous_month_avg = round(mean(grouped[previous_month_key]), 2) if grouped[previous_month_key] else None
        previous_year_avg = round(mean(grouped[previous_year_key]), 2) if grouped[previous_year_key] else None

        points.append(
            MonthlyComparisonPoint(
                month=month,
                current_avg=current_avg,
                previous_month_avg=previous_month_avg,
                previous_year_avg=previous_year_avg,
                mom_change=_safe_change(current_avg, previous_month_avg) if previous_month_avg else None,
                yoy_change=_safe_change(current_avg, previous_year_avg) if previous_year_avg else None,
            )
        )

    return MonthlyComparisonResponse(product=resolved_product, market=resolved_market, points=points)


def get_region_comparison(db: Session, product_name: str | None = None) -> RegionComparisonResponse:
    resolved_product = _resolve_product_name(db, product_name)
    latest_date = db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return RegionComparisonResponse(product=resolved_product, stat_date=None, items=[])

    previous_date = latest_date - timedelta(days=1)
    rows = db.execute(
        select(Market.name, Market.region, PriceRecord.avg_price, PriceRecord.market_id)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(and_(Product.name == resolved_product, PriceRecord.stat_date == latest_date))
        .order_by(PriceRecord.avg_price.desc())
    ).all()
    previous_lookup = {
        row[0]: row[1]
        for row in db.execute(
            select(PriceRecord.market_id, PriceRecord.avg_price)
            .join(Product, Product.id == PriceRecord.product_id)
            .where(and_(Product.name == resolved_product, PriceRecord.stat_date == previous_date))
        ).all()
    }

    items = [
        RegionComparisonItem(
            market=market_name,
            region=region,
            value=round(avg_price, 2),
            change=_safe_change(avg_price, previous_lookup.get(market_id)),
        )
        for market_name, region, avg_price, market_id in rows
    ]
    return RegionComparisonResponse(product=resolved_product, stat_date=latest_date, items=items)


def get_volatility_analysis(db: Session, window_days: int = 30) -> VolatilityResponse:
    latest_date = db.scalar(select(func.max(PriceRecord.stat_date)))
    if latest_date is None:
        return VolatilityResponse(window_days=window_days, items=[])

    start_date = latest_date - timedelta(days=window_days - 1)
    rows = db.execute(
        select(Product.name, Market.name, PriceRecord.avg_price)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(PriceRecord.stat_date >= start_date)
        .order_by(Product.name, Market.name, PriceRecord.stat_date)
    ).all()

    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for product_name, market_name, avg_price in rows:
        grouped[(product_name, market_name)].append(avg_price)

    items = []
    for (product_name, market_name), values in grouped.items():
        if len(values) < 2:
            continue
        mean_price = mean(values)
        volatility = round((pstdev(values) / mean_price) * 100, 2) if mean_price else 0.0
        range_ratio = round(((max(values) - min(values)) / mean_price) * 100, 2) if mean_price else 0.0
        items.append(
            VolatilityItem(
                product=product_name,
                market=market_name,
                mean_price=round(mean_price, 2),
                volatility=volatility,
                range_ratio=range_ratio,
            )
        )

    items.sort(key=lambda item: item.volatility, reverse=True)
    return VolatilityResponse(window_days=window_days, items=items[:10])


def get_anomaly_analysis(
    db: Session,
    product_name: str | None = None,
    market_name: str | None = None,
    days: int = 120,
) -> AnomalyResponse:
    resolved_product = _resolve_product_name(db, product_name)
    resolved_market = _resolve_market_name(db, market_name)
    series = _load_product_market_series(db, resolved_product, resolved_market, days=days)
    values = [value for _, value in series]
    lower_bound, upper_bound = _calculate_iqr_bounds(values)
    items = []
    for stat_date, value in series:
        if lower_bound <= value <= upper_bound:
            continue
        severity = "高" if value < lower_bound - 0.25 or value > upper_bound + 0.25 else "中"
        items.append(
            AnomalyItem(
                date=stat_date,
                value=round(value, 2),
                lower_bound=lower_bound,
                upper_bound=upper_bound,
                severity=severity,
            )
        )

    items.sort(key=lambda item: item.date, reverse=True)
    return AnomalyResponse(product=resolved_product, market=resolved_market, days=days, items=items)
