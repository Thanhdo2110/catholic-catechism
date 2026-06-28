from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")
    SQLALCHEMY_DATABASE_URI: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://catechism:catechism@localhost:3306/catechism",
    )
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_DEFAULT_TTL_SECONDS: int = int(os.getenv("REDIS_DEFAULT_TTL_SECONDS", "300"))
    CORS_ORIGINS: tuple[str, ...] = ()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ENGINE_OPTIONS: dict[str, object] = None  # type: ignore[assignment]
    JSON_SORT_KEYS: bool = False
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: tuple[str, ...] = ("en", "vi")

    def __post_init__(self) -> None:
        cors_origins = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost,http://127.0.0.1",
        )
        object.__setattr__(
            self,
            "SQLALCHEMY_ENGINE_OPTIONS",
            {
                "pool_pre_ping": True,
                "pool_recycle": 1800,
                "pool_size": 20,
                "max_overflow": 10,
            },
        )
        object.__setattr__(
            self,
            "CORS_ORIGINS",
            tuple(origin.strip() for origin in cors_origins.split(",") if origin.strip()),
        )
