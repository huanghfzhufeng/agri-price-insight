from datetime import date

from pydantic import BaseModel


class AnalysisMetric(BaseModel):
    title: str
    value: float
    unit: str
    change: float | None = None
    change_label: str | None = None


class AnalysisOverviewResponse(BaseModel):
    product: str
    market: str
    latest_date: date | None = None
    metrics: list[AnalysisMetric]


class AnalysisSeriesPoint(BaseModel):
    date: date
    value: float


class AnalysisSeries(BaseModel):
    name: str
    points: list[AnalysisSeriesPoint]


class TrendAnalysisResponse(BaseModel):
    product: str
    days: int
    series: list[AnalysisSeries]


class MonthlyComparisonPoint(BaseModel):
    month: str
    current_avg: float
    previous_month_avg: float | None = None
    previous_year_avg: float | None = None
    mom_change: float | None = None
    yoy_change: float | None = None


class MonthlyComparisonResponse(BaseModel):
    product: str
    market: str
    points: list[MonthlyComparisonPoint]


class RegionComparisonItem(BaseModel):
    market: str
    region: str
    value: float
    change: float


class RegionComparisonResponse(BaseModel):
    product: str
    stat_date: date | None = None
    items: list[RegionComparisonItem]


class VolatilityItem(BaseModel):
    product: str
    market: str
    mean_price: float
    volatility: float
    range_ratio: float


class VolatilityResponse(BaseModel):
    window_days: int
    items: list[VolatilityItem]


class AnomalyItem(BaseModel):
    date: date
    value: float
    lower_bound: float
    upper_bound: float
    severity: str


class AnomalyResponse(BaseModel):
    product: str
    market: str
    days: int
    items: list[AnomalyItem]
