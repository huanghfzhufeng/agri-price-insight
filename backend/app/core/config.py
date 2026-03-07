from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


DEFAULT_SQLITE_PATH = Path(__file__).resolve().parents[2] / "pybs.db"


class Settings(BaseSettings):
    app_name: str = "PYBS 农产品价格分析系统"
    app_description: str = "基于 FastAPI 的农产品价格监测、分析、预测与可视化接口服务"
    api_v1_prefix: str = "/api/v1"
    database_url: str = f"sqlite:///{DEFAULT_SQLITE_PATH}"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    auth_token_ttl_hours: int = 12
    default_admin_username: str = "admin"
    default_admin_password: str = "Admin@123456"
    default_admin_display_name: str = "系统管理员"
    scheduler_enabled: bool = False
    scheduler_timezone: str = "Asia/Shanghai"
    daily_sync_hour: int = 9
    daily_sync_minute: int = 0
    monthly_sync_day: int = 1
    monthly_sync_hour: int = 10
    monthly_sync_minute: int = 0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
