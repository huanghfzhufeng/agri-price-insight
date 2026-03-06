from __future__ import annotations

from datetime import date, datetime, timedelta
from random import Random

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import AlertRecord, Market, PriceRecord, Product


PRODUCTS = [
    {"name": "猪肉", "category": "畜牧水产", "unit": "元/公斤", "base": 26.5, "amplitude": 1.6, "trend": 0.04},
    {"name": "大白菜", "category": "蔬菜类", "unit": "元/斤", "base": 1.6, "amplitude": 0.25, "trend": -0.002},
    {"name": "大豆", "category": "粮油类", "unit": "元/斤", "base": 2.8, "amplitude": 0.18, "trend": 0.003},
    {"name": "富士苹果", "category": "水果类", "unit": "元/斤", "base": 3.5, "amplitude": 0.32, "trend": 0.005},
    {"name": "大蒜", "category": "蔬菜类", "unit": "元/斤", "base": 6.2, "amplitude": 0.62, "trend": 0.03},
    {"name": "鸡蛋", "category": "畜牧水产", "unit": "元/斤", "base": 4.8, "amplitude": 0.26, "trend": 0.008},
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


def _resolve_market_name(seed_market: str) -> str:
    aliases = {
        "南方产区": "广州江南市场",
        "华北地区": "北京新发地",
    }
    return aliases.get(seed_market, seed_market)


def seed_demo_data(db: Session) -> None:
    has_products = db.scalar(select(Product.id).limit(1))
    if has_products:
        return

    rng = Random(20260307)

    products = [Product(name=item["name"], category=item["category"], unit=item["unit"]) for item in PRODUCTS]
    markets = [Market(name=item["name"], region=item["region"]) for item in MARKETS]

    db.add_all(products)
    db.add_all(markets)
    db.flush()

    product_map = {product.name: product for product in products}
    market_map = {market.name: market for market in markets}

    start_date = date.today() - timedelta(days=44)
    for offset in range(45):
        stat_date = start_date + timedelta(days=offset)
        for product_seed in PRODUCTS:
            product = product_map[product_seed["name"]]
            base = product_seed["base"]
            amplitude = product_seed["amplitude"]
            slope = product_seed["trend"]
            seasonal = ((offset % 7) - 3) * amplitude * 0.08
            trend = offset * slope

            for market_index, market_seed in enumerate(MARKETS):
                market = market_map[market_seed["name"]]
                market_bias = (market_index - 1.5) * amplitude * 0.25
                noise = rng.uniform(-0.12, 0.12) * amplitude
                avg_price = round(base + trend + seasonal + market_bias + noise, 2)
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

    db.flush()

    # 生菜不进入主数据表，仅用于演示多级预警展示。
    lettuce = Product(name="生菜", category="蔬菜类", unit="元/斤")
    db.add(lettuce)
    db.flush()
    product_map["生菜"] = lettuce

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

    db.commit()
