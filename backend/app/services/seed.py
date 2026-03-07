from __future__ import annotations

import math
from datetime import date, datetime, timedelta
from random import Random

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import hash_password
from app.models.entities import AlertRecord, AlertThreshold, DataSourceConfig, Market, PriceRecord, Product, User


settings = get_settings()

PRODUCTS = [
    {"name": "猪肉", "category": "畜牧水产", "unit": "元/公斤", "base": 26.5, "amplitude": 1.6, "trend": 0.012},
    {"name": "大白菜", "category": "蔬菜类", "unit": "元/斤", "base": 1.6, "amplitude": 0.25, "trend": -0.001},
    {"name": "大豆", "category": "粮油类", "unit": "元/斤", "base": 2.8, "amplitude": 0.18, "trend": 0.001},
    {"name": "富士苹果", "category": "水果类", "unit": "元/斤", "base": 3.5, "amplitude": 0.32, "trend": 0.002},
    {"name": "大蒜", "category": "蔬菜类", "unit": "元/斤", "base": 6.2, "amplitude": 0.62, "trend": 0.008},
    {"name": "鸡蛋", "category": "畜牧水产", "unit": "元/斤", "base": 4.8, "amplitude": 0.26, "trend": 0.003},
]

MARKETS = [
    {"name": "北京新发地", "region": "北京"},
    {"name": "寿光蔬菜市场", "region": "山东"},
    {"name": "广州江南市场", "region": "广东"},
    {"name": "全国均价", "region": "全国"},
]

ALERT_SEEDS = [
    {"product": "大蒜", "market": "全国均价", "level": "高", "message": "连续 3 日涨幅超过 5%，触发红色阈值。", "current": 7.48, "threshold": 7.1},
    {"product": "生菜", "market": "南方产区", "level": "中", "message": "主产区降雨导致价格偏离均值，建议关注短期供应波动。", "current": 4.08, "threshold": 3.9},
    {"product": "鸡蛋", "market": "华北地区", "level": "低", "message": "阶段性波动扩大，但尚未突破高风险阈值。", "current": 5.12, "threshold": 5.3},
]

DATA_SOURCES = [
    {
        "name": "农业农村部每日批发价格简报",
        "category": "官方价格数据",
        "base_url": "https://www.moa.gov.cn/xw/zxfb/",
        "crawl_strategy": "daily",
        "enabled": True,
        "notes": "系统主抓取源，抓取农产品批发价格 200 指数及重点品类价格。",
    },
    {
        "name": "农业农村部农产品供需形势月报",
        "category": "官方分析报告",
        "base_url": "https://www.moa.gov.cn/ztzl/nybrl/rlxx/",
        "crawl_strategy": "monthly",
        "enabled": True,
        "notes": "用于论文背景说明、月度趋势分析和政策环境解读。",
    },
    {
        "name": "农业农村部数据平台",
        "category": "官方数据入口",
        "base_url": "https://data.moa.gov.cn/",
        "crawl_strategy": "manual",
        "enabled": False,
        "notes": "保留为后续扩展数据源和人工核验入口。",
    },
]

THRESHOLD_SEEDS = [
    {"scope_key": "global-default", "scope_label": "全局默认阈值", "product": None, "warning_ratio": 5.0, "critical_ratio": 8.0, "std_multiplier": 2.0},
    {"scope_key": "garlic", "scope_label": "大蒜阈值", "product": "大蒜", "warning_ratio": 6.0, "critical_ratio": 9.0, "std_multiplier": 2.2},
    {"scope_key": "egg", "scope_label": "鸡蛋阈值", "product": "鸡蛋", "warning_ratio": 4.0, "critical_ratio": 6.5, "std_multiplier": 1.8},
]


def _resolve_market_name(seed_market: str) -> str:
    aliases = {
        "南方产区": "广州江南市场",
        "华北地区": "北京新发地",
    }
    return aliases.get(seed_market, seed_market)


def _ensure_reference_data(db: Session) -> tuple[dict[str, Product], dict[str, Market]]:
    product_map: dict[str, Product] = {}
    for item in PRODUCTS:
        product = db.scalar(select(Product).where(Product.name == item["name"]))
        if product is None:
            product = Product(name=item["name"], category=item["category"], unit=item["unit"])
            db.add(product)
            db.flush()
        else:
            product.category = item["category"]
            product.unit = item["unit"]
        product_map[item["name"]] = product

    for item in [{"name": "生菜", "category": "蔬菜类", "unit": "元/斤"}]:
        product = db.scalar(select(Product).where(Product.name == item["name"]))
        if product is None:
            product = Product(name=item["name"], category=item["category"], unit=item["unit"])
            db.add(product)
            db.flush()
        product_map[item["name"]] = product

    market_map: dict[str, Market] = {}
    for item in MARKETS:
        market = db.scalar(select(Market).where(Market.name == item["name"]))
        if market is None:
            market = Market(name=item["name"], region=item["region"])
            db.add(market)
            db.flush()
        else:
            market.region = item["region"]
        market_map[item["name"]] = market

    return product_map, market_map


def _ensure_demo_prices(db: Session, product_map: dict[str, Product], market_map: dict[str, Market]) -> None:
    rng = Random(20260307)
    start_date = date.today() - timedelta(days=419)
    end_date = date.today()

    product_ids = [product_map[item["name"]].id for item in PRODUCTS]
    market_ids = [market_map[item["name"]].id for item in MARKETS]
    existing_keys = {
        (product_id, market_id, stat_date)
        for product_id, market_id, stat_date in db.execute(
            select(PriceRecord.product_id, PriceRecord.market_id, PriceRecord.stat_date).where(
                and_(
                    PriceRecord.product_id.in_(product_ids),
                    PriceRecord.market_id.in_(market_ids),
                    PriceRecord.stat_date >= start_date,
                    PriceRecord.stat_date <= end_date,
                )
            )
        ).all()
    }

    for offset in range((end_date - start_date).days + 1):
        stat_date = start_date + timedelta(days=offset)
        yearly_cycle = math.sin((offset / 365) * math.tau)
        monthly_cycle = math.sin((offset / 30) * math.tau)
        weekly_cycle = math.sin((offset / 7) * math.tau)

        for product_seed in PRODUCTS:
            product = product_map[product_seed["name"]]
            base = product_seed["base"]
            amplitude = product_seed["amplitude"]
            slope = product_seed["trend"]

            for market_index, market_seed in enumerate(MARKETS):
                market = market_map[market_seed["name"]]
                if (product.id, market.id, stat_date) in existing_keys:
                    continue

                market_bias = (market_index - 1.5) * amplitude * 0.28
                weather_shock = yearly_cycle * amplitude * 0.42 + monthly_cycle * amplitude * 0.18
                weekly_bias = weekly_cycle * amplitude * 0.1
                noise = rng.uniform(-0.12, 0.12) * amplitude
                avg_price = round(base + offset * slope + market_bias + weather_shock + weekly_bias + noise, 2)
                min_price = round(max(avg_price - rng.uniform(0.12, 0.38), 0.1), 2)
                max_price = round(avg_price + rng.uniform(0.12, 0.42), 2)

                db.add(
                    PriceRecord(
                        product_id=product.id,
                        market_id=market.id,
                        stat_date=stat_date,
                        min_price=min_price,
                        max_price=max_price,
                        avg_price=avg_price,
                        unit=product.unit,
                        source="农业农村部",
                    )
                )


def _ensure_alerts(db: Session, product_map: dict[str, Product], market_map: dict[str, Market]) -> None:
    has_alerts = db.scalar(select(AlertRecord.id).limit(1))
    if has_alerts:
        return

    now = datetime.now()
    for index, alert_seed in enumerate(ALERT_SEEDS):
        product = product_map[alert_seed["product"]]
        market = market_map.get(_resolve_market_name(alert_seed["market"]))
        db.add(
            AlertRecord(
                product_id=product.id,
                market_id=market.id if market else None,
                level=alert_seed["level"],
                message=alert_seed["message"],
                current_value=alert_seed["current"],
                threshold_value=alert_seed["threshold"],
                created_at=now - timedelta(hours=index * 2 + 1),
            )
        )


def _ensure_admin_user(db: Session) -> None:
    user = db.scalar(select(User).where(User.username == settings.default_admin_username))
    if user is None:
        db.add(
            User(
                username=settings.default_admin_username,
                display_name=settings.default_admin_display_name,
                password_hash=hash_password(settings.default_admin_password),
                role="admin",
                is_active=True,
            )
        )


def _ensure_data_sources(db: Session) -> None:
    for item in DATA_SOURCES:
        source = db.scalar(select(DataSourceConfig).where(DataSourceConfig.name == item["name"]))
        if source is None:
            source = DataSourceConfig(**item)
            db.add(source)
        else:
            source.category = item["category"]
            source.base_url = item["base_url"]
            source.crawl_strategy = item["crawl_strategy"]
            source.enabled = item["enabled"]
            source.notes = item["notes"]


def _ensure_thresholds(db: Session, product_map: dict[str, Product]) -> None:
    for item in THRESHOLD_SEEDS:
        threshold = db.scalar(select(AlertThreshold).where(AlertThreshold.scope_key == item["scope_key"]))
        product = product_map.get(item["product"]) if item["product"] else None
        payload = {
            "scope_label": item["scope_label"],
            "product_id": product.id if product else None,
            "warning_ratio": item["warning_ratio"],
            "critical_ratio": item["critical_ratio"],
            "std_multiplier": item["std_multiplier"],
        }
        if threshold is None:
            db.add(AlertThreshold(scope_key=item["scope_key"], **payload))
        else:
            threshold.scope_label = payload["scope_label"]
            threshold.product_id = payload["product_id"]
            threshold.warning_ratio = payload["warning_ratio"]
            threshold.critical_ratio = payload["critical_ratio"]
            threshold.std_multiplier = payload["std_multiplier"]


def seed_demo_data(db: Session) -> None:
    product_map, market_map = _ensure_reference_data(db)
    _ensure_demo_prices(db, product_map, market_map)
    _ensure_alerts(db, product_map, market_map)
    _ensure_admin_user(db)
    _ensure_data_sources(db)
    _ensure_thresholds(db, product_map)
    db.commit()
