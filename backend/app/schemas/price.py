from datetime import date

from pydantic import BaseModel


class PriceRecordOut(BaseModel):
    id: int
    stat_date: date
    product_name: str
    category: str
    market_name: str
    region: str
    avg_price: float
    min_price: float
    max_price: float
    unit: str
    change_rate: float
    source: str


class PriceListResponse(BaseModel):
    total: int
    items: list[PriceRecordOut]


class SystemOptionsResponse(BaseModel):
    products: list[str]
    markets: list[str]
    categories: list[str]
