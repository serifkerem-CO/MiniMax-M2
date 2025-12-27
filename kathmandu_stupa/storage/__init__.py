"""
💾 STORAGE - Tapınak Arşivi
===========================

Veri kalıcılığı için storage backend'leri.
JSON (basit) ve SQLite (ölçeklenebilir) destekler.
"""

from .base import StorageBackend, StorageRecord
from .json_storage import JSONStorage
from .sqlite_storage import SQLiteStorage
from .pilgrimage_store import PilgrimageStore

__all__ = [
    "StorageBackend",
    "StorageRecord",
    "JSONStorage",
    "SQLiteStorage",
    "PilgrimageStore",
]
