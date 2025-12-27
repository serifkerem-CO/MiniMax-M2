"""
🛕 PILGRIMAGE STORE - Hac Yolculuğu Arşivi
==========================================

Tam hac yolculuklarını ve nirvana paketlerini saklayan
yüksek seviye storage arayüzü.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
import hashlib

from .base import StorageBackend, StorageRecord
from .json_storage import JSONStorage
from .sqlite_storage import SQLiteStorage


class PilgrimageStore:
    """
    🛕 Hac Yolculuğu Deposu

    Kathmandu Stupa'nın kalıcı hafızası.
    Tüm yolculukları, katlamaları ve nirvana paketlerini saklar.
    """

    # Kayıt tipleri
    TYPE_PILGRIMAGE = "pilgrimage"
    TYPE_NIRVANA = "nirvana"
    TYPE_FOLD = "fold"
    TYPE_TRANSMISSION = "transmission"
    TYPE_PROPHECY = "prophecy"
    TYPE_COUNCIL = "council"

    def __init__(
        self,
        backend: Optional[StorageBackend] = None,
        use_sqlite: bool = False,
        base_path: str = "./stupa_data"
    ):
        if backend:
            self.backend = backend
        elif use_sqlite:
            self.backend = SQLiteStorage(f"{base_path}/stupa.db")
        else:
            self.backend = JSONStorage(base_path)

    def _generate_id(self, prefix: str, content: str = "") -> str:
        """Benzersiz ID oluştur"""
        timestamp = int(datetime.now().timestamp() * 1000)
        hash_part = hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()[:8]
        return f"{prefix}_{timestamp}_{hash_part}"

    # ===== PILGRIMAGE =====

    async def save_pilgrimage(
        self,
        summary: Dict[str, Any],
        nirvana_ids: List[str],
        tags: Optional[List[str]] = None
    ) -> str:
        """Tam hac yolculuğu kaydet"""
        record = StorageRecord(
            id=self._generate_id("PILGRIMAGE"),
            type=self.TYPE_PILGRIMAGE,
            data={
                "summary": summary,
                "nirvana_ids": nirvana_ids,
                "packets_processed": summary.get("packets_processed", 0),
                "total_folds": summary.get("folds_performed", 0),
                "duration_seconds": summary.get("duration_seconds", 0),
            },
            metadata={
                "frequency_hz": 963,
                "mantra": summary.get("mantra", ""),
            },
            tags=tags or ["pilgrimage"],
        )
        return await self.backend.save(record)

    async def get_pilgrimage(self, pilgrimage_id: str) -> Optional[StorageRecord]:
        """Hac yolculuğu al"""
        return await self.backend.get(pilgrimage_id)

    async def get_recent_pilgrimages(self, limit: int = 10) -> List[StorageRecord]:
        """Son hac yolculukları"""
        return await self.backend.get_recent(limit, self.TYPE_PILGRIMAGE)

    # ===== NIRVANA =====

    async def save_nirvana(
        self,
        wisdom: str,
        frequency_hz: int,
        confidence: float,
        source_chain: List[str],
        tags: Optional[List[str]] = None
    ) -> str:
        """Nirvana paketi kaydet"""
        record = StorageRecord(
            id=self._generate_id("NIRVANA", wisdom[:50]),
            type=self.TYPE_NIRVANA,
            data={
                "wisdom": wisdom,
                "frequency_hz": frequency_hz,
                "confidence": confidence,
                "source_chain": source_chain,
            },
            metadata={
                "length": len(wisdom),
                "word_count": len(wisdom.split()),
            },
            tags=tags or ["nirvana", f"freq_{frequency_hz}"],
        )
        return await self.backend.save(record)

    async def get_nirvana(self, nirvana_id: str) -> Optional[StorageRecord]:
        """Nirvana paketi al"""
        return await self.backend.get(nirvana_id)

    async def search_nirvana(
        self,
        min_confidence: Optional[float] = None,
        frequency_hz: Optional[int] = None
    ) -> List[StorageRecord]:
        """Nirvana ara"""
        all_nirvana = await self.backend.get_all(self.TYPE_NIRVANA)
        results = []

        for record in all_nirvana:
            if min_confidence and record.data.get("confidence", 0) < min_confidence:
                continue
            if frequency_hz and record.data.get("frequency_hz") != frequency_hz:
                continue
            results.append(record)

        return results

    # ===== FOLD (Katlama) =====

    async def save_fold(
        self,
        content: str,
        fold_depth: int,
        monks_involved: List[str],
        consensus_score: float
    ) -> str:
        """Katlama kaydet"""
        record = StorageRecord(
            id=self._generate_id("FOLD", content[:30]),
            type=self.TYPE_FOLD,
            data={
                "content": content,
                "fold_depth": fold_depth,
                "monks_involved": monks_involved,
                "consensus_score": consensus_score,
            },
            tags=["fold"] + monks_involved,
        )
        return await self.backend.save(record)

    # ===== PROPHECY (Kehanet) =====

    async def save_prophecy(
        self,
        title: str,
        wisdom: str,
        legend_name: str,
        frequency_hz: int = 963
    ) -> str:
        """Kehanet parşömeni kaydet"""
        record = StorageRecord(
            id=self._generate_id("PROPHECY", wisdom[:30]),
            type=self.TYPE_PROPHECY,
            data={
                "title": title,
                "wisdom": wisdom,
                "legend_name": legend_name,
                "frequency_hz": frequency_hz,
            },
            metadata={"format": "scroll"},
            tags=["prophecy", legend_name.lower()],
        )
        return await self.backend.save(record)

    async def get_prophecies_by_legend(self, legend_name: str) -> List[StorageRecord]:
        """Legend'a göre kehanetler"""
        return await self.backend.get_by_tags([legend_name.lower()])

    # ===== COUNCIL (Konsey) =====

    async def save_council_decision(
        self,
        query: str,
        winning_monk: str,
        vote_breakdown: Dict[str, float],
        consensus_score: float,
        wisdom: str
    ) -> str:
        """Konsey kararı kaydet"""
        record = StorageRecord(
            id=self._generate_id("COUNCIL", query[:30]),
            type=self.TYPE_COUNCIL,
            data={
                "query": query,
                "winning_monk": winning_monk,
                "vote_breakdown": vote_breakdown,
                "consensus_score": consensus_score,
                "wisdom": wisdom,
            },
            tags=["council", winning_monk.lower()],
        )
        return await self.backend.save(record)

    # ===== STATISTICS =====

    async def get_statistics(self) -> Dict[str, Any]:
        """Depo istatistikleri"""
        stats = {
            "total_pilgrimages": await self.backend.count(self.TYPE_PILGRIMAGE),
            "total_nirvana": await self.backend.count(self.TYPE_NIRVANA),
            "total_folds": await self.backend.count(self.TYPE_FOLD),
            "total_prophecies": await self.backend.count(self.TYPE_PROPHECY),
            "total_councils": await self.backend.count(self.TYPE_COUNCIL),
        }

        # Nirvana ortalama güven
        nirvana_records = await self.backend.get_all(self.TYPE_NIRVANA)
        if nirvana_records:
            confidences = [r.data.get("confidence", 0) for r in nirvana_records]
            stats["avg_nirvana_confidence"] = sum(confidences) / len(confidences)
        else:
            stats["avg_nirvana_confidence"] = 0

        stats["backend_stats"] = self.backend.get_stats()
        return stats

    async def export_all(self) -> Dict[str, List[Dict]]:
        """Tüm verileri export et"""
        return {
            "pilgrimages": [r.to_dict() for r in await self.backend.get_all(self.TYPE_PILGRIMAGE)],
            "nirvana": [r.to_dict() for r in await self.backend.get_all(self.TYPE_NIRVANA)],
            "folds": [r.to_dict() for r in await self.backend.get_all(self.TYPE_FOLD)],
            "prophecies": [r.to_dict() for r in await self.backend.get_all(self.TYPE_PROPHECY)],
            "councils": [r.to_dict() for r in await self.backend.get_all(self.TYPE_COUNCIL)],
        }


# Factory
def create_store(use_sqlite: bool = False, base_path: str = "./stupa_data") -> PilgrimageStore:
    """Store oluştur"""
    return PilgrimageStore(use_sqlite=use_sqlite, base_path=base_path)


# Demo
async def demo_storage():
    """Storage demo"""
    print("💾 Pilgrimage Store Demo")
    print("=" * 50)

    store = create_store(use_sqlite=False)

    # Nirvana kaydet
    nirvana_id = await store.save_nirvana(
        wisdom="Türkiye sanayisi dönüşüm fırsatıyla karşı karşıya",
        frequency_hz=963,
        confidence=0.92,
        source_chain=["TOPRAK", "SU", "ATES", "HAVA", "ETER"],
    )
    print(f"✅ Nirvana kaydedildi: {nirvana_id}")

    # Pilgrimage kaydet
    pilgrim_id = await store.save_pilgrimage(
        summary={"packets_processed": 10, "folds_performed": 30},
        nirvana_ids=[nirvana_id],
        tags=["demo", "test"],
    )
    print(f"✅ Pilgrimage kaydedildi: {pilgrim_id}")

    # İstatistikler
    stats = await store.get_statistics()
    print(f"\n📊 İstatistikler: {stats}")


if __name__ == "__main__":
    asyncio.run(demo_storage())
