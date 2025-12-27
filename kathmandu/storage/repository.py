"""
🗄️ Storage Repositories
========================
Farklı depolama backend'leri
"""

import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from collections import Counter

from .models import StoredJourney, StoredCrystal, StorageStats


class BaseRepository(ABC):
    """Temel repository arayüzü"""

    @abstractmethod
    async def save_journey(self, journey: StoredJourney) -> bool:
        pass

    @abstractmethod
    async def get_journey(self, journey_id: str) -> Optional[StoredJourney]:
        pass

    @abstractmethod
    async def list_journeys(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredJourney]:
        pass

    @abstractmethod
    async def save_crystal(self, crystal: StoredCrystal) -> bool:
        pass

    @abstractmethod
    async def get_crystal(self, crystal_id: str) -> Optional[StoredCrystal]:
        pass

    @abstractmethod
    async def list_crystals(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredCrystal]:
        pass

    @abstractmethod
    async def get_stats(self) -> StorageStats:
        pass


class InMemoryStorage(BaseRepository):
    """
    Bellek İçi Depolama

    Hızlı ama geçici. Test ve geliştirme için.
    """

    def __init__(self):
        self.journeys: Dict[str, StoredJourney] = {}
        self.crystals: Dict[str, StoredCrystal] = {}
        self.last_activity: Optional[datetime] = None

    async def save_journey(self, journey: StoredJourney) -> bool:
        self.journeys[journey.journey_id] = journey
        self.last_activity = datetime.now()
        return True

    async def get_journey(self, journey_id: str) -> Optional[StoredJourney]:
        return self.journeys.get(journey_id)

    async def list_journeys(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredJourney]:
        all_journeys = sorted(
            self.journeys.values(),
            key=lambda j: j.created_at,
            reverse=True
        )
        return all_journeys[offset:offset + limit]

    async def save_crystal(self, crystal: StoredCrystal) -> bool:
        self.crystals[crystal.crystal_id] = crystal
        self.last_activity = datetime.now()
        return True

    async def get_crystal(self, crystal_id: str) -> Optional[StoredCrystal]:
        return self.crystals.get(crystal_id)

    async def list_crystals(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredCrystal]:
        all_crystals = sorted(
            self.crystals.values(),
            key=lambda c: c.created_at,
            reverse=True
        )
        return all_crystals[offset:offset + limit]

    async def get_stats(self) -> StorageStats:
        journeys = list(self.journeys.values())
        crystals = list(self.crystals.values())

        successful = sum(1 for j in journeys if j.state == "enlightened")
        avg_duration = (
            sum(j.duration_seconds for j in journeys) / len(journeys)
            if journeys else 0
        )
        avg_purity = (
            sum(c.purity_percentage for c in crystals) / len(crystals)
            if crystals else 0
        )

        enlightenment_counts = Counter(c.enlightenment_level for c in crystals)
        most_common = (
            enlightenment_counts.most_common(1)[0][0]
            if enlightenment_counts else "none"
        )

        return StorageStats(
            total_journeys=len(journeys),
            total_crystals=len(crystals),
            successful_journeys=successful,
            average_duration=avg_duration,
            average_purity=avg_purity,
            most_common_enlightenment=most_common,
            storage_type="in_memory",
            last_activity=self.last_activity
        )


class FileStorage(BaseRepository):
    """
    Dosya Tabanlı Depolama

    JSON dosyalarında kalıcı saklama.
    """

    def __init__(self, base_path: str = ".temple_data"):
        self.base_path = Path(base_path)
        self.journeys_path = self.base_path / "journeys"
        self.crystals_path = self.base_path / "crystals"

        # Dizinleri oluştur
        self.journeys_path.mkdir(parents=True, exist_ok=True)
        self.crystals_path.mkdir(parents=True, exist_ok=True)

    async def save_journey(self, journey: StoredJourney) -> bool:
        try:
            filepath = self.journeys_path / f"{journey.journey_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(journey.to_json())
            return True
        except Exception:
            return False

    async def get_journey(self, journey_id: str) -> Optional[StoredJourney]:
        filepath = self.journeys_path / f"{journey_id}.json"
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return StoredJourney.from_dict(data)
        except Exception:
            return None

    async def list_journeys(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredJourney]:
        journeys = []
        files = sorted(
            self.journeys_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for filepath in files[offset:offset + limit]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                journeys.append(StoredJourney.from_dict(data))
            except Exception:
                continue

        return journeys

    async def save_crystal(self, crystal: StoredCrystal) -> bool:
        try:
            filepath = self.crystals_path / f"{crystal.crystal_id}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(crystal.to_json())
            return True
        except Exception:
            return False

    async def get_crystal(self, crystal_id: str) -> Optional[StoredCrystal]:
        filepath = self.crystals_path / f"{crystal_id}.json"
        if not filepath.exists():
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return StoredCrystal.from_dict(data)
        except Exception:
            return None

    async def list_crystals(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredCrystal]:
        crystals = []
        files = sorted(
            self.crystals_path.glob("*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        for filepath in files[offset:offset + limit]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                crystals.append(StoredCrystal.from_dict(data))
            except Exception:
                continue

        return crystals

    async def get_stats(self) -> StorageStats:
        journeys = await self.list_journeys(limit=10000)
        crystals = await self.list_crystals(limit=10000)

        successful = sum(1 for j in journeys if j.state == "enlightened")
        avg_duration = (
            sum(j.duration_seconds for j in journeys) / len(journeys)
            if journeys else 0
        )
        avg_purity = (
            sum(c.purity_percentage for c in crystals) / len(crystals)
            if crystals else 0
        )

        enlightenment_counts = Counter(c.enlightenment_level for c in crystals)
        most_common = (
            enlightenment_counts.most_common(1)[0][0]
            if enlightenment_counts else "none"
        )

        # Son aktivite
        all_files = list(self.journeys_path.glob("*.json")) + list(self.crystals_path.glob("*.json"))
        last_activity = None
        if all_files:
            newest = max(all_files, key=lambda p: p.stat().st_mtime)
            last_activity = datetime.fromtimestamp(newest.stat().st_mtime)

        return StorageStats(
            total_journeys=len(journeys),
            total_crystals=len(crystals),
            successful_journeys=successful,
            average_duration=avg_duration,
            average_purity=avg_purity,
            most_common_enlightenment=most_common,
            storage_type="file",
            last_activity=last_activity
        )


class SQLiteStorage(BaseRepository):
    """
    SQLite Depolama

    Daha büyük veri setleri için.
    """

    def __init__(self, db_path: str = ".temple_data/stupa.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialized = False

    async def _ensure_tables(self):
        """Tabloları oluştur"""
        if self._initialized:
            return

        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS journeys (
                journey_id TEXT PRIMARY KEY,
                input_data TEXT,
                final_output TEXT,
                layers_traversed TEXT,
                duration_seconds REAL,
                state TEXT,
                created_at TEXT,
                metadata TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS crystals (
                crystal_id TEXT PRIMARY KEY,
                essence TEXT,
                frequency INTEGER,
                enlightenment_level TEXT,
                purity_percentage REAL,
                source_journey_id TEXT,
                created_at TEXT,
                tags TEXT
            )
        """)

        conn.commit()
        conn.close()
        self._initialized = True

    async def save_journey(self, journey: StoredJourney) -> bool:
        await self._ensure_tables()
        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO journeys
                (journey_id, input_data, final_output, layers_traversed,
                 duration_seconds, state, created_at, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                journey.journey_id,
                journey.input_data,
                json.dumps(journey.final_output) if journey.final_output else None,
                json.dumps(journey.layers_traversed),
                journey.duration_seconds,
                journey.state,
                journey.created_at.isoformat(),
                json.dumps(journey.metadata)
            ))

            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    async def get_journey(self, journey_id: str) -> Optional[StoredJourney]:
        await self._ensure_tables()
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM journeys WHERE journey_id = ?",
            (journey_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return StoredJourney(
            journey_id=row[0],
            input_data=row[1],
            final_output=json.loads(row[2]) if row[2] else None,
            layers_traversed=json.loads(row[3]) if row[3] else [],
            duration_seconds=row[4],
            state=row[5],
            created_at=datetime.fromisoformat(row[6]),
            metadata=json.loads(row[7]) if row[7] else {}
        )

    async def list_journeys(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredJourney]:
        await self._ensure_tables()
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM journeys ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            StoredJourney(
                journey_id=row[0],
                input_data=row[1],
                final_output=json.loads(row[2]) if row[2] else None,
                layers_traversed=json.loads(row[3]) if row[3] else [],
                duration_seconds=row[4],
                state=row[5],
                created_at=datetime.fromisoformat(row[6]),
                metadata=json.loads(row[7]) if row[7] else {}
            )
            for row in rows
        ]

    async def save_crystal(self, crystal: StoredCrystal) -> bool:
        await self._ensure_tables()
        import sqlite3

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("""
                INSERT OR REPLACE INTO crystals
                (crystal_id, essence, frequency, enlightenment_level,
                 purity_percentage, source_journey_id, created_at, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                crystal.crystal_id,
                crystal.essence,
                crystal.frequency,
                crystal.enlightenment_level,
                crystal.purity_percentage,
                crystal.source_journey_id,
                crystal.created_at.isoformat(),
                json.dumps(crystal.tags)
            ))

            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    async def get_crystal(self, crystal_id: str) -> Optional[StoredCrystal]:
        await self._ensure_tables()
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM crystals WHERE crystal_id = ?",
            (crystal_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        return StoredCrystal(
            crystal_id=row[0],
            essence=row[1],
            frequency=row[2],
            enlightenment_level=row[3],
            purity_percentage=row[4],
            source_journey_id=row[5],
            created_at=datetime.fromisoformat(row[6]),
            tags=json.loads(row[7]) if row[7] else []
        )

    async def list_crystals(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[StoredCrystal]:
        await self._ensure_tables()
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM crystals ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset)
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            StoredCrystal(
                crystal_id=row[0],
                essence=row[1],
                frequency=row[2],
                enlightenment_level=row[3],
                purity_percentage=row[4],
                source_journey_id=row[5],
                created_at=datetime.fromisoformat(row[6]),
                tags=json.loads(row[7]) if row[7] else []
            )
            for row in rows
        ]

    async def get_stats(self) -> StorageStats:
        await self._ensure_tables()
        import sqlite3

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Journey stats
        cursor.execute("SELECT COUNT(*) FROM journeys")
        total_journeys = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM journeys WHERE state = 'enlightened'")
        successful = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(duration_seconds) FROM journeys")
        avg_duration = cursor.fetchone()[0] or 0

        # Crystal stats
        cursor.execute("SELECT COUNT(*) FROM crystals")
        total_crystals = cursor.fetchone()[0]

        cursor.execute("SELECT AVG(purity_percentage) FROM crystals")
        avg_purity = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT enlightenment_level, COUNT(*) as cnt
            FROM crystals
            GROUP BY enlightenment_level
            ORDER BY cnt DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
        most_common = row[0] if row else "none"

        conn.close()

        return StorageStats(
            total_journeys=total_journeys,
            total_crystals=total_crystals,
            successful_journeys=successful,
            average_duration=avg_duration,
            average_purity=avg_purity,
            most_common_enlightenment=most_common,
            storage_type="sqlite",
            last_activity=datetime.now()
        )


# Repository Factory
class JourneyRepository:
    """Journey işlemleri için wrapper"""

    def __init__(self, storage: BaseRepository):
        self.storage = storage

    async def save(self, journey) -> bool:
        """ProcessingJourney'den StoredJourney'e dönüştür ve kaydet"""
        stored = StoredJourney(
            journey_id=journey.journey_id,
            input_data=str(journey.input_data)[:1000],
            final_output=journey.final_output if hasattr(journey, 'final_output') else None,
            layers_traversed=journey.layers_traversed if hasattr(journey, 'layers_traversed') else [],
            duration_seconds=journey.duration_seconds if hasattr(journey, 'duration_seconds') else 0,
            state=journey.state.value if hasattr(journey.state, 'value') else str(journey.state),
            created_at=journey.started_at if hasattr(journey, 'started_at') else datetime.now()
        )
        return await self.storage.save_journey(stored)

    async def get(self, journey_id: str) -> Optional[StoredJourney]:
        return await self.storage.get_journey(journey_id)

    async def list(self, limit: int = 100) -> List[StoredJourney]:
        return await self.storage.list_journeys(limit=limit)


class CrystalRepository:
    """Crystal işlemleri için wrapper"""

    def __init__(self, storage: BaseRepository):
        self.storage = storage

    async def save_from_output(self, journey_id: str, output: Dict) -> bool:
        """Journey output'undan crystal çıkar ve kaydet"""
        crystal_data = output.get("crystal", {})
        if not crystal_data:
            return False

        stored = StoredCrystal(
            crystal_id=crystal_data.get("id", "unknown"),
            essence=crystal_data.get("essence", ""),
            frequency=crystal_data.get("frequency", 963),
            enlightenment_level=crystal_data.get("enlightenment", "seeker"),
            purity_percentage=crystal_data.get("purity", 0),
            source_journey_id=journey_id,
            created_at=datetime.now()
        )
        return await self.storage.save_crystal(stored)

    async def get(self, crystal_id: str) -> Optional[StoredCrystal]:
        return await self.storage.get_crystal(crystal_id)

    async def list(self, limit: int = 100) -> List[StoredCrystal]:
        return await self.storage.list_crystals(limit=limit)
