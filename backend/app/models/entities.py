from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    unit: Mapped[str] = mapped_column(String(32))

    price_records: Mapped[list["PriceRecord"]] = relationship(back_populates="product")
    alerts: Mapped[list["AlertRecord"]] = relationship(back_populates="product")
    forecasts: Mapped[list["ForecastResult"]] = relationship(back_populates="product")


class Market(Base):
    __tablename__ = "market"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    region: Mapped[str] = mapped_column(String(32), index=True)

    price_records: Mapped[list["PriceRecord"]] = relationship(back_populates="market")
    alerts: Mapped[list["AlertRecord"]] = relationship(back_populates="market")
    forecasts: Mapped[list["ForecastResult"]] = relationship(back_populates="market")


class PriceRecord(Base):
    __tablename__ = "price_record"
    __table_args__ = (UniqueConstraint("product_id", "market_id", "stat_date"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    market_id: Mapped[int] = mapped_column(ForeignKey("market.id"), index=True)
    stat_date: Mapped[date] = mapped_column(Date, index=True)
    min_price: Mapped[float] = mapped_column(Float)
    max_price: Mapped[float] = mapped_column(Float)
    avg_price: Mapped[float] = mapped_column(Float, index=True)
    unit: Mapped[str] = mapped_column(String(32))
    source: Mapped[str] = mapped_column(String(64), default="农业农村部")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="price_records")
    market: Mapped["Market"] = relationship(back_populates="price_records")


class RawPriceRecord(Base):
    __tablename__ = "raw_price_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    source_url: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    source_type: Mapped[str] = mapped_column(String(64), index=True)
    article_title: Mapped[str] = mapped_column(String(255))
    article_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(32), default="success", index=True)
    raw_content: Mapped[str] = mapped_column(Text)
    raw_html: Mapped[str | None] = mapped_column(Text, nullable=True)
    crawl_time: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)


class AlertRecord(Base):
    __tablename__ = "alert_record"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    market_id: Mapped[int | None] = mapped_column(ForeignKey("market.id"), nullable=True, index=True)
    level: Mapped[str] = mapped_column(String(16), index=True)
    message: Mapped[str] = mapped_column(Text)
    current_value: Mapped[float] = mapped_column(Float)
    threshold_value: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="alerts")
    market: Mapped["Market | None"] = relationship(back_populates="alerts")


class TaskLog(Base):
    __tablename__ = "task_log"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    task_name: Mapped[str] = mapped_column(String(128), index=True)
    status: Mapped[str] = mapped_column(String(32), index=True)
    message: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(128), nullable=True)
    records_inserted: Mapped[int] = mapped_column(default=0)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ForecastResult(Base):
    __tablename__ = "forecast_result"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("product.id"), index=True)
    market_id: Mapped[int | None] = mapped_column(ForeignKey("market.id"), nullable=True, index=True)
    forecast_date: Mapped[date] = mapped_column(Date, index=True)
    predicted_price: Mapped[float] = mapped_column(Float)
    lower_bound: Mapped[float] = mapped_column(Float)
    upper_bound: Mapped[float] = mapped_column(Float)
    model_name: Mapped[str] = mapped_column(String(64))
    mape: Mapped[float | None] = mapped_column(Float, nullable=True)
    rmse: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    product: Mapped["Product"] = relationship(back_populates="forecasts")
    market: Mapped["Market | None"] = relationship(back_populates="forecasts")
