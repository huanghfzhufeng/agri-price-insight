from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Final
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select

CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_DIR = CURRENT_DIR.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models.entities import Market, PriceRecord, Product, RawPriceRecord, TaskLog

HEADERS: Final = {
    "User-Agent": "PYBS/1.0 (+https://github.com/huanghfzhufeng/agri-price-insight)",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
LIST_PAGE_TEMPLATE: Final = "https://www.moa.gov.cn/xw/zxfb/{suffix}"
LIST_PAGE_SUFFIXES: Final = ["index.htm", "index_1.htm", "index_2.htm", "index_3.htm", "index_4.htm"]
ARTICLE_KEYWORD: Final = "农产品批发价格200指数"
MARKET_NAME: Final = "全国均价"
SOURCE_NAME: Final = "农业农村部每日批发价格简报"


@dataclass(frozen=True)
class MetricPattern:
    name: str
    category: str
    unit: str
    pattern: re.Pattern[str]


METRIC_PATTERNS: Final[list[MetricPattern]] = [
    MetricPattern("农产品批发价格200指数", "价格指数", "点", re.compile(r"农产品批发价格200指数[”\"]?为(?P<value>\d+(?:\.\d+)?)")),
    MetricPattern("菜篮子产品批发价格指数", "价格指数", "点", re.compile(r"菜篮子产品批发价格指数[”\"]?为(?P<value>\d+(?:\.\d+)?)")),
    MetricPattern("猪肉", "畜牧水产", "元/公斤", re.compile(r"猪肉(?:（[^）]*）)?(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("牛肉", "畜牧水产", "元/公斤", re.compile(r"牛肉(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("羊肉", "畜牧水产", "元/公斤", re.compile(r"羊肉(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("鸡蛋", "畜牧水产", "元/公斤", re.compile(r"鸡蛋(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("白条鸡", "畜牧水产", "元/公斤", re.compile(r"白条鸡(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("鲫鱼", "畜牧水产", "元/公斤", re.compile(r"鲫鱼(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("鲤鱼", "畜牧水产", "元/公斤", re.compile(r"鲤鱼(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("白鲢鱼", "畜牧水产", "元/公斤", re.compile(r"白鲢鱼(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("大带鱼", "畜牧水产", "元/公斤", re.compile(r"大带鱼(?:批发价格)?(?:为|价格为)(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("28种蔬菜", "蔬菜类", "元/公斤", re.compile(r"28种蔬菜平均价格为(?P<value>\d+(?:\.\d+)?)元/公斤")),
    MetricPattern("6种水果", "水果类", "元/公斤", re.compile(r"6种水果平均价格为(?P<value>\d+(?:\.\d+)?)元/公斤")),
]


def fetch_html(url: str) -> str:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    response.encoding = response.apparent_encoding or response.encoding
    return response.text


def extract_article_links(pages: int) -> list[tuple[str, str]]:
    links: dict[str, str] = {}
    for suffix in LIST_PAGE_SUFFIXES[:pages]:
        html = fetch_html(LIST_PAGE_TEMPLATE.format(suffix=suffix))
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.select("a[href]"):
            title = anchor.get_text(" ", strip=True)
            href = anchor.get("href", "")
            if ARTICLE_KEYWORD not in title or not href:
                continue
            links[urljoin(LIST_PAGE_TEMPLATE.format(suffix=suffix), href)] = title
    return [(title, url) for url, title in links.items()]


def parse_article_date(soup: BeautifulSoup) -> datetime.date | None:
    meta_pub_date = soup.select_one("meta[name='PubDate']")
    if meta_pub_date and meta_pub_date.get("content"):
        return datetime.strptime(meta_pub_date["content"], "%Y-%m-%d %H:%M:%S").date()

    publish_date = soup.select_one("meta[name='publishdate']")
    if publish_date and publish_date.get("content"):
        return datetime.strptime(publish_date["content"], "%Y-%m-%d").date()

    return None


def parse_article(html: str, fallback_title: str) -> tuple[str, datetime.date | None, str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = fallback_title

    title_meta = soup.select_one("meta[name='ArticleTitle']")
    if title_meta and title_meta.get("content"):
        title = title_meta["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()

    article_body = soup.select_one(".TRS_Editor")
    if article_body is None:
        article_body = soup.body
    raw_html = str(article_body) if article_body else html
    raw_text = "\n".join(article_body.stripped_strings) if article_body else soup.get_text("\n", strip=True)
    article_date = parse_article_date(soup)
    return title, article_date, raw_text, raw_html


def extract_metrics(raw_text: str) -> list[tuple[str, str, float, str]]:
    metrics: list[tuple[str, str, float, str]] = []
    for metric in METRIC_PATTERNS:
        match = metric.pattern.search(raw_text)
        if match is None:
            continue
        metrics.append((metric.name, metric.category, float(match.group("value")), metric.unit))
    return metrics


def get_or_create_market(db) -> Market:
    market = db.scalar(select(Market).where(Market.name == MARKET_NAME))
    if market:
        return market
    market = Market(name=MARKET_NAME, region="全国")
    db.add(market)
    db.flush()
    return market


def get_or_create_product(db, name: str, category: str, unit: str) -> Product:
    product = db.scalar(select(Product).where(Product.name == name))
    if product:
        if product.category != category or product.unit != unit:
            product.category = category
            product.unit = unit
        return product
    product = Product(name=name, category=category, unit=unit)
    db.add(product)
    db.flush()
    return product


def upsert_price_record(db, *, product: Product, market: Market, stat_date, value: float, unit: str, source: str) -> bool:
    record = db.scalar(
        select(PriceRecord).where(
            PriceRecord.product_id == product.id,
            PriceRecord.market_id == market.id,
            PriceRecord.stat_date == stat_date,
        )
    )
    if record:
        changed = (
            record.avg_price != value
            or record.min_price != value
            or record.max_price != value
            or record.unit != unit
            or record.source != source
        )
        record.avg_price = value
        record.min_price = value
        record.max_price = value
        record.unit = unit
        record.source = source
        return changed

    db.add(
        PriceRecord(
            product_id=product.id,
            market_id=market.id,
            stat_date=stat_date,
            min_price=value,
            max_price=value,
            avg_price=value,
            unit=unit,
            source=source,
        )
    )
    return True


def fetch_and_store(pages: int, max_articles: int) -> tuple[int, int, int]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    started_at = datetime.now()
    inserted_articles = 0
    inserted_metrics = 0
    scanned_articles = 0
    task_log = TaskLog(task_name="fetch_moa_daily", status="running", source=SOURCE_NAME, records_inserted=0, started_at=started_at)
    db.add(task_log)
    db.flush()

    try:
        market = get_or_create_market(db)
        article_links = extract_article_links(pages=pages)[:max_articles]

        for fallback_title, url in article_links:
            scanned_articles += 1
            existing_raw = db.scalar(select(RawPriceRecord).where(RawPriceRecord.source_url == url))
            if existing_raw:
                continue

            html = fetch_html(url)
            title, article_date, raw_text, raw_html = parse_article(html, fallback_title)
            metrics = extract_metrics(raw_text)
            status = "success" if metrics else "parsed_empty"

            db.add(
                RawPriceRecord(
                    source_url=url,
                    source_type=SOURCE_NAME,
                    article_title=title,
                    article_date=article_date,
                    status=status,
                    raw_content=raw_text,
                    raw_html=raw_html,
                )
            )
            inserted_articles += 1

            if article_date and metrics:
                for name, category, value, unit in metrics:
                    product = get_or_create_product(db, name=name, category=category, unit=unit)
                    if upsert_price_record(
                        db,
                        product=product,
                        market=market,
                        stat_date=article_date,
                        value=value,
                        unit=unit,
                        source=SOURCE_NAME,
                    ):
                        inserted_metrics += 1

        task_log.status = "success"
        task_log.message = f"扫描 {scanned_articles} 篇文章，新增 {inserted_articles} 条原始记录，写入 {inserted_metrics} 条标准价格记录。"
        task_log.records_inserted = inserted_metrics
        task_log.finished_at = datetime.now()
        db.commit()
        return scanned_articles, inserted_articles, inserted_metrics
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        task_log.status = "failed"
        task_log.message = str(exc)
        task_log.records_inserted = inserted_metrics
        task_log.finished_at = datetime.now()
        db.add(task_log)
        db.commit()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="抓取农业农村部每日批发价格简报并入库。")
    parser.add_argument("--pages", type=int, default=3, help="抓取列表页数量，默认 3 页。")
    parser.add_argument("--max-articles", type=int, default=20, help="最多处理的文章数，默认 20。")
    args = parser.parse_args()

    scanned_articles, inserted_articles, inserted_metrics = fetch_and_store(
        pages=max(args.pages, 1),
        max_articles=max(args.max_articles, 1),
    )
    print(
        f"fetch_moa_daily: scanned={scanned_articles} inserted_articles={inserted_articles} inserted_metrics={inserted_metrics}"
    )


if __name__ == "__main__":
    main()
