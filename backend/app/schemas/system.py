from datetime import date, datetime

from pydantic import BaseModel


class TaskLogOut(BaseModel):
    id: int
    task_name: str
    status: str
    message: str | None = None
    source: str | None = None
    records_inserted: int
    started_at: datetime
    finished_at: datetime | None = None


class RawPriceRecordOut(BaseModel):
    id: int
    source_url: str
    source_type: str
    article_title: str
    article_date: date | None = None
    status: str
    crawl_time: datetime


class DataSourceOut(BaseModel):
    id: int
    name: str
    category: str
    base_url: str
    crawl_strategy: str
    enabled: bool
    notes: str | None = None
    last_success_at: datetime | None = None


class AlertThresholdOut(BaseModel):
    id: int
    scope_key: str
    scope_label: str
    product_name: str | None = None
    warning_ratio: float
    critical_ratio: float
    std_multiplier: float
    updated_at: datetime


class AlertThresholdUpdate(BaseModel):
    warning_ratio: float
    critical_ratio: float
    std_multiplier: float


class ReportAssetOut(BaseModel):
    id: int
    title: str
    report_month: date | None = None
    source_url: str
    local_path: str | None = None
    source_type: str
    status: str
    summary: str | None = None
    created_at: datetime
