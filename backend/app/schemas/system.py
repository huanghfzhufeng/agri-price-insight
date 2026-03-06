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
