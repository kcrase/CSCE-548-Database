# app/dependencies.py
# Creates a fresh DataProvider (and therefore a fresh MySQL connection)
# for every request, then closes it cleanly when the request is done.
# This avoids stale connection errors caused by MySQL's idle timeout.

from __future__ import annotations
import os
from app.data_provider import DataProvider
from app.business_manager import BusinessManager


def get_business_manager():
    dp = DataProvider(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", "KeitC4658!"),
        database=os.environ.get("DB_NAME", "job_tracker"),
        port=int(os.environ.get("DB_PORT", "3306")),
    )
    try:
        yield BusinessManager(dp)
    finally:
        dp.close()
        