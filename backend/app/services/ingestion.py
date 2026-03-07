from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Final
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.entities import DataSourceConfig, Market, PriceRecord, Product, RawPriceRecord, ReportAsset, TaskLog


HEADERS: Final = {
    "User-Agent": "PYBS/1.0 (+https://github.com/huanghfzhufeng/agri-price-insight)",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}
DAILY_LIST_PAGE_TEMPLATE: Final = "https://www.moa.gov.cn/xw/zxfb/{suffix}"
DAILY_LIST_PAGE_SUFFIXES: Final = ["index.htm", "index_1.htm", "index_2.htm", "index_3.htm", "index_4.htm"]
DAILY_ARTICLE_KEYWORD: Final = "农产品批发价格200指数"
DAILY_MARKET_NAME: Final = "全国均价"
DAILY_SOURCE_NAME: Final = "农业农村部每日批发价格简报"
MONTHLY_LIST_URL: Final = "https://www.moa.gov.cn/ztzl/nybrl/rlxx/"
MONTHLY_ARTICLE_LIST_URL: Final = "https://scs.moa.gov.cn/jcyj/"
MONTHLY_SOURCE_NAME: Final = "农业农村部农产品供需形势月报"

PRODUCT_ALIASES: Final = {
    "猪肉（白条猪）": "猪肉",
}
UNIT_ALIASES: Final = {
    "元／公斤": "元/公斤",
    "元/千克": "元/公斤",
    "元/500克": "元/斤",
    "元／斤": "元/斤",
}


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


def fetch_binary(url: str) -> bytes:
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.content


def normalize_product_name(name: str) -> str:
    return PRODUCT_ALIASES.get(name, name)


def normalize_unit(unit: str) -> str:
    return UNIT_ALIASES.get(unit, unit)


def extract_daily_article_links(pages: int) -> list[tuple[str, str]]:
    links: dict[str, str] = {}
    for suffix in DAILY_LIST_PAGE_SUFFIXES[:pages]:
        html = fetch_html(DAILY_LIST_PAGE_TEMPLATE.format(suffix=suffix))
        soup = BeautifulSoup(html, "html.parser")
        for anchor in soup.select("a[href]"):
            title = anchor.get_text(" ", strip=True)
            href = anchor.get("href", "")
            if DAILY_ARTICLE_KEYWORD not in title or not href:
                continue
            links[urljoin(DAILY_LIST_PAGE_TEMPLATE.format(suffix=suffix), href)] = title
    return [(title, url) for url, title in links.items()]


def parse_article_date(soup: BeautifulSoup) -> date | None:
    meta_pub_date = soup.select_one("meta[name='PubDate']")
    if meta_pub_date and meta_pub_date.get("content"):
        return datetime.strptime(meta_pub_date["content"], "%Y-%m-%d %H:%M:%S").date()

    publish_date = soup.select_one("meta[name='publishdate']")
    if publish_date and publish_date.get("content"):
        return datetime.strptime(publish_date["content"], "%Y-%m-%d").date()

    return None


def parse_article(html: str, fallback_title: str) -> tuple[str, date | None, str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = fallback_title

    title_meta = soup.select_one("meta[name='ArticleTitle']")
    if title_meta and title_meta.get("content"):
        title = title_meta["content"].strip()
    elif soup.title and soup.title.string:
        title = soup.title.string.strip()

    article_body = soup.select_one(".TRS_Editor") or soup.body
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
        metrics.append(
            (
                normalize_product_name(metric.name),
                metric.category,
                float(match.group("value")),
                normalize_unit(metric.unit),
            )
        )
    return metrics


def get_or_create_market(db: Session, name: str = DAILY_MARKET_NAME, region: str = "全国") -> Market:
    market = db.scalar(select(Market).where(Market.name == name))
    if market:
        return market
    market = Market(name=name, region=region)
    db.add(market)
    db.flush()
    return market


def get_or_create_product(db: Session, name: str, category: str, unit: str) -> Product:
    product = db.scalar(select(Product).where(Product.name == name))
    normalized_unit = normalize_unit(unit)
    if product:
        if product.category != category or product.unit != normalized_unit:
            product.category = category
            product.unit = normalized_unit
        return product
    product = Product(name=name, category=category, unit=normalized_unit)
    db.add(product)
    db.flush()
    return product


def upsert_price_record(db: Session, *, product: Product, market: Market, stat_date: date, value: float, unit: str, source: str) -> bool:
    record = db.scalar(
        select(PriceRecord).where(
            PriceRecord.product_id == product.id,
            PriceRecord.market_id == market.id,
            PriceRecord.stat_date == stat_date,
        )
    )
    normalized_unit = normalize_unit(unit)
    if record:
        changed = (
            record.avg_price != value
            or record.min_price != value
            or record.max_price != value
            or record.unit != normalized_unit
            or record.source != source
        )
        record.avg_price = value
        record.min_price = value
        record.max_price = value
        record.unit = normalized_unit
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
            unit=normalized_unit,
            source=source,
        )
    )
    return True


def mark_data_source_success(db: Session, source_name: str) -> None:
    data_source = db.scalar(select(DataSourceConfig).where(DataSourceConfig.name == source_name))
    if data_source:
        data_source.last_success_at = datetime.now()


def run_moa_daily_ingestion(db: Session, *, pages: int = 3, max_articles: int = 20) -> tuple[int, int, int]:
    started_at = datetime.now()
    inserted_articles = 0
    inserted_metrics = 0
    scanned_articles = 0
    failed_articles = 0
    task_log = TaskLog(task_name="fetch_moa_daily", status="running", source=DAILY_SOURCE_NAME, records_inserted=0, started_at=started_at)
    db.add(task_log)
    db.flush()

    try:
        market = get_or_create_market(db)
        article_links = extract_daily_article_links(pages=pages)[:max_articles]

        for fallback_title, url in article_links:
            scanned_articles += 1
            existing_raw = db.scalar(select(RawPriceRecord).where(RawPriceRecord.source_url == url))
            if existing_raw and existing_raw.status == "success":
                continue

            try:
                html = fetch_html(url)
                title, article_date, raw_text, raw_html = parse_article(html, fallback_title)
                metrics = extract_metrics(raw_text)
                status = "success" if metrics else "parsed_empty"
                if existing_raw is None:
                    db.add(
                        RawPriceRecord(
                            source_url=url,
                            source_type=DAILY_SOURCE_NAME,
                            article_title=title,
                            article_date=article_date,
                            status=status,
                            raw_content=raw_text,
                            raw_html=raw_html,
                        )
                    )
                    inserted_articles += 1
                else:
                    existing_raw.article_title = title
                    existing_raw.article_date = article_date
                    existing_raw.status = status
                    existing_raw.raw_content = raw_text
                    existing_raw.raw_html = raw_html

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
                            source=DAILY_SOURCE_NAME,
                        ):
                            inserted_metrics += 1
            except Exception as exc:  # noqa: BLE001
                failed_articles += 1
                error_text = str(exc)
                if existing_raw is None:
                    db.add(
                        RawPriceRecord(
                            source_url=url,
                            source_type=DAILY_SOURCE_NAME,
                            article_title=fallback_title,
                            article_date=None,
                            status="fetch_failed",
                            raw_content=error_text,
                            raw_html=None,
                        )
                    )
                    inserted_articles += 1
                else:
                    existing_raw.status = "fetch_failed"
                    existing_raw.raw_content = error_text
                    existing_raw.raw_html = None

        mark_data_source_success(db, DAILY_SOURCE_NAME)
        task_log.status = "success"
        task_log.message = (
            f"扫描 {scanned_articles} 篇文章，新增 {inserted_articles} 条原始记录，"
            f"写入 {inserted_metrics} 条标准价格记录，失败 {failed_articles} 篇。"
        )
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


def _extract_monthly_report_month(title: str) -> date | None:
    match = re.search(r"(?P<year>\d{4})年(?P<month>\d{1,2})月", title)
    if not match:
        return None
    return date(int(match.group("year")), int(match.group("month")), 1)


def _find_monthly_report_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str]] = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        if ".pdf" not in href.lower():
            continue
        title = anchor.get_text(" ", strip=True) or anchor.get("title", "").strip()
        if not title:
            title = anchor.parent.get_text(" ", strip=True)
        if "月报" not in title and "供需形势分析" not in title:
            continue
        links.append((title, urljoin(MONTHLY_LIST_URL, href)))
    return links


def _find_monthly_article_links(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    links: list[tuple[str, str]] = []
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        title = anchor.get_text(" ", strip=True)
        if not href or ".htm" not in href.lower():
            continue
        if "供需形势分析" not in title and "CASDE" not in title:
            continue
        links.append((title, urljoin(MONTHLY_ARTICLE_LIST_URL, href)))
    return links


def _extract_pdf_from_article(article_html: str, article_url: str) -> tuple[str | None, str | None]:
    soup = BeautifulSoup(article_html, "html.parser")
    for anchor in soup.select("a[href]"):
        href = anchor.get("href", "")
        if ".pdf" not in href.lower():
            continue
        title = anchor.get_text(" ", strip=True) or "官方月报 PDF"
        return title, urljoin(article_url, href)
    return None, None


def run_moa_monthly_report_sync(db: Session, *, limit: int = 12, download_dir: Path | None = None) -> tuple[int, int]:
    resolved_dir = download_dir or Path(__file__).resolve().parents[2] / "data" / "monthly_reports"
    resolved_dir.mkdir(parents=True, exist_ok=True)

    task_log = TaskLog(task_name="fetch_moa_monthly_report", status="running", source=MONTHLY_SOURCE_NAME, records_inserted=0, started_at=datetime.now())
    db.add(task_log)
    db.flush()

    try:
        html = fetch_html(MONTHLY_ARTICLE_LIST_URL)
        article_links = _find_monthly_article_links(html)
        report_links: list[tuple[str, str]] = []

        for article_title, article_url in article_links:
            article_html = fetch_html(article_url)
            report_title, report_url = _extract_pdf_from_article(article_html, article_url)
            if report_url:
                report_links.append((report_title or article_title, report_url))
            if len(report_links) >= limit:
                break

        if not report_links:
            fallback_html = fetch_html(MONTHLY_LIST_URL)
            report_links = _find_monthly_report_links(fallback_html)[:limit]

        downloaded = 0
        scanned = 0

        for title, url in report_links:
            scanned += 1
            report_month = _extract_monthly_report_month(title)
            existing = db.scalar(select(ReportAsset).where(ReportAsset.source_url == url))
            if existing and existing.local_path and Path(existing.local_path).exists():
                continue

            content = fetch_binary(url)
            suffix = report_month.strftime("%Y-%m") if report_month else f"report-{scanned}"
            local_path = resolved_dir / f"{suffix}.pdf"
            local_path.write_bytes(content)

            if existing is None:
                db.add(
                    ReportAsset(
                        title=title,
                        report_month=report_month,
                        source_url=url,
                        local_path=str(local_path),
                        source_type=MONTHLY_SOURCE_NAME,
                        status="downloaded",
                        summary="官方月报 PDF 已归档，可用于论文趋势分析与政策背景说明。",
                    )
                )
            else:
                existing.title = title
                existing.report_month = report_month
                existing.local_path = str(local_path)
                existing.status = "downloaded"
                existing.summary = "官方月报 PDF 已归档，可用于论文趋势分析与政策背景说明。"
            downloaded += 1

        mark_data_source_success(db, MONTHLY_SOURCE_NAME)
        task_log.status = "success"
        task_log.records_inserted = downloaded
        task_log.finished_at = datetime.now()
        task_log.message = f"扫描 {scanned} 份月报，下载 {downloaded} 份官方 PDF。"
        db.commit()
        return scanned, downloaded
    except Exception as exc:  # noqa: BLE001
        db.rollback()
        task_log.status = "failed"
        task_log.message = str(exc)
        task_log.finished_at = datetime.now()
        db.add(task_log)
        db.commit()
        raise
