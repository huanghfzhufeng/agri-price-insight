from datetime import date, datetime

from pydantic import BaseModel


class AlertItem(BaseModel):
    id: int
    level: str
    product: str
    market: str
    detail: str
    created_at: datetime
    current_value: float
    threshold_value: float


class AlertsResponse(BaseModel):
    items: list[AlertItem]


class ForecastPoint(BaseModel):
    date: date
    value: float
    lower_bound: float | None = None
    upper_bound: float | None = None


class ForecastResponse(BaseModel):
    product: str
    market: str
    days: int
    model_name: str
    mape: float
    rmse: float
    history: list[ForecastPoint]
    forecast: list[ForecastPoint]
    insight: str
