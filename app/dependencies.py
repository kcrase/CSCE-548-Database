# app/dependencies.py
# Provides a single shared BusinessManager instance via FastAPI dependency
# injection.  lru_cache ensures the DB connection is created once per process.

from __future__ import annotations
import os
from functools import lru_cache
from app.data_provider import DataProvider
from app.business_manager import BusinessManager


@lru_cache(maxsize=1)
def get_business_manager() -> BusinessManager:
    dp = DataProvider(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "KeitC4658!"),
        database=os.environ.get("DB_NAME", "job_tracker"),
        port=int(os.environ.get("DB_PORT", "3306")),
    )
    return BusinessManager(dp)
