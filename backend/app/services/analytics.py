from __future__ import annotations

import math
from datetime import date, timedelta
from statistics import mean, pstdev

from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.models.entities import (
    AlertRecord,
    AlertThreshold,
    DataSourceConfig,
    Market,
    PriceRecord,
    Product,
    RawPriceRecord,
    ReportAsset,
    TaskLog,
)
from app.schemas.alerts import AlertItem, ForecastPoint, ForecastResponse
from app.schemas.dashboard import DashboardSummaryResponse, RankingItem, SummaryMetric, TrendPoint, TrendSeries
from app.schemas.price import PriceListResponse, PriceRecordOut, SystemOptionsResponse
from app.schemas.system import AlertThresholdOut, DataSourceOut, RawPriceRecordOut, ReportAssetOut, TaskLogOut


def _safe_change(current: float, previous: float | None) -> float:
    if previous in (None, 0):
        return 0.0
    return round(((current - previous) / previous) * 100, 1)


def _build_price_filters(
    *,
    product: str | None = None,
    market: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> list:
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
    return filters


def _base_price_query(filters: list):
    return (
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


def _model_metrics(actual: list[float], predicted: list[float]) -> dict[str, float]:
    if not actual or len(actual) != len(predicted):
        return {"mae": 0.0, "rmse": 0.0, "mape": 0.0}

    errors = [abs(a - p) for a, p in zip(actual, predicted, strict=False)]
    squared_errors = [(a - p) ** 2 for a, p in zip(actual, predicted, strict=False)]
    percentage_errors = [
        abs((a - p) / a) * 100
        for a, p in zip(actual, predicted, strict=False)
        if a not in (None, 0)
    ]
    return {
        "mae": round(sum(errors) / len(errors), 3),
        "rmse": round(math.sqrt(sum(squared_errors) / len(squared_errors)), 3),
        "mape": round(sum(percentage_errors) / len(percentage_errors), 3) if percentage_errors else 0.0,
    }


def _forecast_moving_average(values: list[float], horizon: int, window: int = 7) -> list[float]:
    history = values[:]
    forecast: list[float] = []
    for _ in range(horizon):
        sample = history[-window:] if len(history) >= window else history
        next_value = round(sum(sample) / len(sample), 2)
        history.append(next_value)
        forecast.append(next_value)
    return forecast


def _forecast_linear_trend(values: list[float], horizon: int) -> list[float]:
    x_values = list(range(len(values)))
    x_mean = mean(x_values)
    y_mean = mean(values)
    denominator = sum((x - x_mean) ** 2 for x in x_values) or 1.0
    slope = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_values, values, strict=False)) / denominator
    intercept = y_mean - slope * x_mean
    return [round(max(intercept + slope * (len(values) + index), 0.1), 2) for index in range(horizon)]


def _forecast_seasonal_trend(values: list[float], horizon: int) -> list[float]:
    if len(values) < 14:
        return _forecast_moving_average(values, horizon, window=min(5, len(values)))

    recent_avg = mean(values[-7:])
    previous_avg = mean(values[-14:-7])
    slope = (recent_avg - previous_avg) / 7
    weekly_offsets = [values[-7 + idx] - recent_avg for idx in range(7)]
    last_value = values[-1]
    forecast = []
    for index in range(1, horizon + 1):
        seasonal = weekly_offsets[(index - 1) % 7] * 0.35
        next_value = round(max(last_value + slope * index + seasonal, 0.1), 2)
        forecast.append(next_value)
    return forecast


def _predict_with_model(values: list[float], horizon: int, model_name: str) -> list[float]:
    if model_name == "moving_average":
        return _forecast_moving_average(values, horizon)
    if model_name == "linear_trend":
        return _forecast_linear_trend(values, horizon)
    return _forecast_seasonal_trend(values, horizon)


def _evaluate_models(values: list[float]) -> list[dict]:
    if len(values) < 21:
        return []

    horizon = min(7, max(len(values) // 6, 3))
    train = values[:-horizon]
    actual = values[-horizon:]
    models = [
        ("seasonal_trend", "趋势基线模型"),
        ("moving_average", "移动平均模型"),
        ("linear_trend", "线性回归模型"),
    ]

    results = []
    for model_key, display_name in models:
        predicted = _predict_with_model(train, horizon, model_key)
        metrics = _model_metrics(actual, predicted)
        results.append(
            {
                "key": model_key,
                "model_name": display_name,
                **metrics,
                "available": True,
            }
        )

    try:
        import prophet  # noqa: F401
    except Exception:  # noqa: BLE001
        results.append(
            {
                "key": "prophet",
                "model_name": "Prophet",
                "mae": None,
                "rmse": None,
                "mape": None,
                "available": False,
            }
        )

    return sorted(results, key=lambda item: item["mape"] if item["mape"] is not None else float("inf"))


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


def get_data_sources(db: Session) -> list[DataSourceOut]:
    sources = db.scalars(select(DataSourceConfig).order_by(DataSourceConfig.category, DataSourceConfig.name)).all()
    return [
        DataSourceOut(
            id=source.id,
            name=source.name,
            category=source.category,
            base_url=source.base_url,
            crawl_strategy=source.crawl_strategy,
            enabled=source.enabled,
            notes=source.notes,
            last_success_at=source.last_success_at,
        )
        for source in sources
    ]


def get_thresholds(db: Session) -> list[AlertThresholdOut]:
    rows = db.execute(
        select(AlertThreshold, Product.name)
        .outerjoin(Product, Product.id == AlertThreshold.product_id)
        .order_by(AlertThreshold.scope_key)
    ).all()
    return [
        AlertThresholdOut(
            id=threshold.id,
            scope_key=threshold.scope_key,
            scope_label=threshold.scope_label,
            product_name=product_name,
            warning_ratio=threshold.warning_ratio,
            critical_ratio=threshold.critical_ratio,
            std_multiplier=threshold.std_multiplier,
            updated_at=threshold.updated_at,
        )
        for threshold, product_name in rows
    ]


def update_threshold(db: Session, threshold_id: int, *, warning_ratio: float, critical_ratio: float, std_multiplier: float) -> AlertThresholdOut:
    threshold = db.scalar(select(AlertThreshold).where(AlertThreshold.id == threshold_id))
    if threshold is None:
        raise ValueError("预警阈值不存在")

    threshold.warning_ratio = warning_ratio
    threshold.critical_ratio = critical_ratio
    threshold.std_multiplier = std_multiplier
    db.commit()
    db.refresh(threshold)
    product_name = db.scalar(select(Product.name).where(Product.id == threshold.product_id)) if threshold.product_id else None
    return AlertThresholdOut(
        id=threshold.id,
        scope_key=threshold.scope_key,
        scope_label=threshold.scope_label,
        product_name=product_name,
        warning_ratio=threshold.warning_ratio,
        critical_ratio=threshold.critical_ratio,
        std_multiplier=threshold.std_multiplier,
        updated_at=threshold.updated_at,
    )


def get_report_assets(db: Session, limit: int = 20) -> list[ReportAssetOut]:
    reports = db.scalars(select(ReportAsset).order_by(ReportAsset.report_month.desc(), ReportAsset.created_at.desc()).limit(limit)).all()
    return [
        ReportAssetOut(
            id=report.id,
            title=report.title,
            report_month=report.report_month,
            source_url=report.source_url,
            local_path=report.local_path,
            source_type=report.source_type,
            status=report.status,
            summary=report.summary,
            created_at=report.created_at,
        )
        for report in reports
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
            value="3",
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


def list_price_rows(
    db: Session,
    *,
    product: str | None = None,
    market: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    limit: int | None = None,
    offset: int = 0,
) -> list:
    filters = _build_price_filters(
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )
    query = _base_price_query(filters).offset(offset)
    if limit is not None:
        query = query.limit(limit)
    return db.execute(query).all()


def query_prices(
    db: Session,
    product: str | None = None,
    market: str | None = None,
    category: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> PriceListResponse:
    filters = _build_price_filters(
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
    )
    total = db.scalar(
        select(func.count())
        .select_from(PriceRecord)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(*filters)
    ) or 0
    offset = (page - 1) * page_size
    rows = list_price_rows(
        db,
        product=product,
        market=market,
        category=category,
        start_date=start_date,
        end_date=end_date,
        limit=page_size,
        offset=offset,
    )

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

    pages = math.ceil(total / page_size) if page_size else 1
    return PriceListResponse(page=page, page_size=page_size, pages=pages, total=total, items=items)


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


def get_forecast(db: Session, product_name: str = "大蒜", days: int = 30, model_key: str | None = None) -> ForecastResponse:
    market_name = "全国均价"
    history_rows = db.execute(
        select(PriceRecord.stat_date, PriceRecord.avg_price)
        .join(Product, Product.id == PriceRecord.product_id)
        .join(Market, Market.id == PriceRecord.market_id)
        .where(and_(Product.name == product_name, Market.name == market_name))
        .order_by(PriceRecord.stat_date.desc())
        .limit(120)
    ).all()

    history_rows.reverse()
    history = [ForecastPoint(date=row[0], value=row[1]) for row in history_rows[-45:]]

    if len(history_rows) < 7:
        return ForecastResponse(
            product=product_name,
            market=market_name,
            days=days,
            model_name="趋势预测基线模型",
            mape=0.0,
            rmse=0.0,
            mae=0.0,
            history=history,
            forecast=[],
            insight="历史数据不足，暂不生成预测结果。",
            available_models=[],
        )

    values = [row[1] for row in history_rows]
    available_models = _evaluate_models(values)
    selected_model = next(
        (
            model
            for model in available_models
            if model["available"] and (model_key is None or model["key"] == model_key)
        ),
        next((model for model in available_models if model.get("available")), {"key": "seasonal_trend", "model_name": "趋势基线模型", "mae": 0.0, "rmse": 0.0, "mape": 0.0}),
    )

    forecast_values = _predict_with_model(values, days, selected_model["key"])
    recent_window = values[-14:] if len(values) >= 14 else values
    residual_std = pstdev(recent_window) if len(recent_window) > 1 else max(values[-1] * 0.04, 0.12)
    anchor_date = history_rows[-1][0]
    forecast = []
    for index, value in enumerate(forecast_values, start=1):
        spread = max(residual_std * 0.9, value * 0.03, 0.12)
        forecast.append(
            ForecastPoint(
                date=anchor_date + timedelta(days=index),
                value=value,
                lower_bound=round(max(value - spread, 0.1), 2),
                upper_bound=round(value + spread, 2),
            )
        )

    insight_direction = "震荡上行" if forecast_values[-1] >= values[-1] else "高位回落"
    prophet_note = ""
    if any(item["key"] == "prophet" and not item["available"] for item in available_models):
        prophet_note = " 当前环境未安装 Prophet，系统自动回退到内置时间序列模型。"

    return ForecastResponse(
        product=product_name,
        market=market_name,
        days=days,
        model_name=selected_model["model_name"],
        mape=selected_model["mape"] or 0.0,
        rmse=selected_model["rmse"] or 0.0,
        mae=selected_model["mae"] or 0.0,
        history=history,
        forecast=forecast,
        insight=f"{selected_model['model_name']}判断 {product_name}未来 {days} 天大概率呈{insight_direction}走势，建议结合库存和天气因素动态调整采购节奏。{prophet_note}",
        available_models=available_models,
    )
