from datetime import date
from typing import Literal

from pydantic import BaseModel


class SummaryMetric(BaseModel):
    title: str
    value: str
    unit: str
    trend: str
    trend_direction: Literal["up", "down", "flat"]
    alert: bool = False


class TrendPoint(BaseModel):
    date: date
    value: float


class TrendSeries(BaseModel):
    name: str
    points: list[TrendPoint]


class RankingItem(BaseModel):
    name: str
    market: str
    price: str
    change: str
    up: bool


class DashboardSummaryResponse(BaseModel):
    summary: list[SummaryMetric]
    trend_series: list[TrendSeries]
    top_changes: list[RankingItem]
