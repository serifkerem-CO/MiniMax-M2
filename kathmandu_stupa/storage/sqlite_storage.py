"""
🗄️ SQLITE STORAGE - Veritabanı Arşivi
======================================

Ölçeklenebilir SQLite storage.
Büyük veri setleri ve karmaşık sorgular için.
"""

import asyncio
import json
import sqlite3
from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .base import StorageBackend, StorageRecord

# Opsiyonel async sqlite
try:
    import aiosqlite
    HAS_AIOSQLITE = True
except ImportError:
    HAS_AIOSQLITE = False


class SQLiteStorage(StorageBackend[StorageRecord]):
    """
    🗄️ SQLite Storage Backend

    Performanslı ve ölçeklenebilir.
    Full-text search ve complex queries.
    """

    CREATE_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS records (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        data TEXT NOT NULL,
        metadata TEXT,
        tags TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );

    CREATE INDEX IF NOT EXISTS idx_type ON records(type);
    CREATE INDEX IF NOT EXISTS idx_created ON records(created_at);
    """

    def __init__(self, db_path: str = "./stupa_data/stupa.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_init(self):
        """Veritabanı başlat"""
        if self._initialized:
            return

        if HAS_AIOSQLITE:
            async with aiosqlite.connect(str(self.db_path)) as db:
                await db.executescript(self.CREATE_TABLE_SQL)
                await db.commit()
        else:
            # Sync fallback
            with sqlite3.connect(str(self.db_path)) as conn:
                conn.executescript(self.CREATE_TABLE_SQL)
                conn.commit()

        self._initialized = True

    @asynccontextmanager
    async def _get_conn(self):
        """Bağlantı context manager"""
        await self._ensure_init()

        if HAS_AIOSQLITE:
            async with aiosqlite.connect(str(self.db_path)) as db:
                db.row_factory = sqlite3.Row
                yield db
        else:
            # Sync wrapper
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            try:
                yield conn
            finally:
                conn.close()

    def _record_to_row(self, record: StorageRecord) -> tuple:
        """Record -> SQL row"""
        return (
            record.id,
            record.type,
            json.dumps(record.data, ensure_ascii=False),
            json.dumps(record.metadata, ensure_ascii=False),
            json.dumps(record.tags),
            record.created_at.isoformat(),
            record.updated_at.isoformat(),
        )

    def _row_to_record(self, row) -> StorageRecord:
        """SQL row -> Record"""
        return StorageRecord(
            id=row["id"],
            type=row["type"],
            data=json.loads(row["data"]),
            metadata=json.loads(row["metadata"] or "{}"),
            tags=json.loads(row["tags"] or "[]"),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )

    async def save(self, record: StorageRecord) -> str:
        """Kayıt kaydet"""
        async with self._get_conn() as db:
            sql = """
            INSERT OR REPLACE INTO records
            (id, type, data, metadata, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            row = self._record_to_row(record)

            if HAS_AIOSQLITE:
                await db.execute(sql, row)
                await db.commit()
            else:
                db.execute(sql, row)
                db.commit()

        return record.id

    async def get(self, record_id: str) -> Optional[StorageRecord]:
        """ID ile kayıt al"""
        async with self._get_conn() as db:
            sql = "SELECT * FROM records WHERE id = ?"

            if HAS_AIOSQLITE:
                cursor = await db.execute(sql, (record_id,))
                row = await cursor.fetchone()
            else:
                cursor = db.execute(sql, (record_id,))
                row = cursor.fetchone()

            if row:
                return self._row_to_record(row)

        return None

    async def get_all(self, record_type: Optional[str] = None) -> List[StorageRecord]:
        """Tüm kayıtları al"""
        async with self._get_conn() as db:
            if record_type:
                sql = "SELECT * FROM records WHERE type = ? ORDER BY created_at DESC"
                params = (record_type,)
            else:
                sql = "SELECT * FROM records ORDER BY created_at DESC"
                params = ()

            if HAS_AIOSQLITE:
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
            else:
                cursor = db.execute(sql, params)
                rows = cursor.fetchall()

            return [self._row_to_record(row) for row in rows]

    async def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Kayıt güncelle"""
        record = await self.get(record_id)
        if not record:
            return False

        record.data.update(data)
        record.updated_at = datetime.now()
        await self.save(record)
        return True

    async def delete(self, record_id: str) -> bool:
        """Kayıt sil"""
        async with self._get_conn() as db:
            sql = "DELETE FROM records WHERE id = ?"

            if HAS_AIOSQLITE:
                cursor = await db.execute(sql, (record_id,))
                await db.commit()
                return cursor.rowcount > 0
            else:
                cursor = db.execute(sql, (record_id,))
                db.commit()
                return cursor.rowcount > 0

    async def search(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """SQL tabanlı arama"""
        conditions = []
        params = []

        if "type" in query:
            conditions.append("type = ?")
            params.append(query["type"])

        if "tags" in query:
            # JSON array içinde arama
            for tag in query["tags"]:
                conditions.append("tags LIKE ?")
                params.append(f'%"{tag}"%')

        if "data" in query:
            # Data JSON içinde arama
            for key, value in query["data"].items():
                conditions.append("json_extract(data, ?) = ?")
                params.extend([f"$.{key}", value])

        if "created_after" in query:
            conditions.append("created_at >= ?")
            params.append(query["created_after"])

        if "created_before" in query:
            conditions.append("created_at <= ?")
            params.append(query["created_before"])

        where_clause = " AND ".join(conditions) if conditions else "1=1"
        sql = f"SELECT * FROM records WHERE {where_clause} ORDER BY created_at DESC"

        async with self._get_conn() as db:
            if HAS_AIOSQLITE:
                cursor = await db.execute(sql, params)
                rows = await cursor.fetchall()
            else:
                cursor = db.execute(sql, params)
                rows = cursor.fetchall()

            return [self._row_to_record(row) for row in rows]

    async def count(self, record_type: Optional[str] = None) -> int:
        """Kayıt sayısı"""
        async with self._get_conn() as db:
            if record_type:
                sql = "SELECT COUNT(*) as cnt FROM records WHERE type = ?"
                params = (record_type,)
            else:
                sql = "SELECT COUNT(*) as cnt FROM records"
                params = ()

            if HAS_AIOSQLITE:
                cursor = await db.execute(sql, params)
                row = await cursor.fetchone()
            else:
                cursor = db.execute(sql, params)
                row = cursor.fetchone()

            return row["cnt"] if row else 0

    async def get_type_stats(self) -> Dict[str, int]:
        """Tip bazında istatistik"""
        async with self._get_conn() as db:
            sql = "SELECT type, COUNT(*) as cnt FROM records GROUP BY type"

            if HAS_AIOSQLITE:
                cursor = await db.execute(sql)
                rows = await cursor.fetchall()
            else:
                cursor = db.execute(sql)
                rows = cursor.fetchall()

            return {row["type"]: row["cnt"] for row in rows}

    def get_stats(self) -> Dict:
        """Storage istatistikleri"""
        return {
            "db_path": str(self.db_path),
            "db_size_kb": self.db_path.stat().st_size / 1024 if self.db_path.exists() else 0,
            "async_mode": HAS_AIOSQLITE,
        }
