from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PYBS 农产品价格分析系统"
    app_description: str = "基于 FastAPI 的农产品价格监测、分析、预测与可视化接口服务"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "sqlite:///./pybs.db"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
