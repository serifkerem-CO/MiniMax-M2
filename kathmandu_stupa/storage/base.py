"""
💾 STORAGE BASE - Temel Arşiv Sınıfı
====================================

Tüm storage backend'lerinin miras aldığı temel sınıf.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any, Dict, List, Optional, TypeVar, Generic
import json


@dataclass
class StorageRecord:
    """Temel kayıt yapısı"""
    id: str
    type: str  # pilgrimage, nirvana, fold, etc.
    data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """JSON serializable dict"""
        return {
            "id": self.id,
            "type": self.type,
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, d: Dict) -> "StorageRecord":
        """Dict'ten oluştur"""
        return cls(
            id=d["id"],
            type=d["type"],
            data=d["data"],
            metadata=d.get("metadata", {}),
            created_at=datetime.fromisoformat(d["created_at"]) if isinstance(d.get("created_at"), str) else d.get("created_at", datetime.now()),
            updated_at=datetime.fromisoformat(d["updated_at"]) if isinstance(d.get("updated_at"), str) else d.get("updated_at", datetime.now()),
            tags=d.get("tags", []),
        )


T = TypeVar('T', bound=StorageRecord)


class StorageBackend(ABC, Generic[T]):
    """
    💾 Temel Storage Backend

    Tüm storage implementasyonlarının arayüzü.
    """

    @abstractmethod
    async def save(self, record: T) -> str:
        """Kayıt kaydet, ID döndür"""
        pass

    @abstractmethod
    async def get(self, record_id: str) -> Optional[T]:
        """ID ile kayıt al"""
        pass

    @abstractmethod
    async def get_all(self, record_type: Optional[str] = None) -> List[T]:
        """Tüm kayıtları al (opsiyonel tip filtresi)"""
        pass

    @abstractmethod
    async def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Kayıt güncelle"""
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """Kayıt sil"""
        pass

    @abstractmethod
    async def search(self, query: Dict[str, Any]) -> List[T]:
        """Arama yap"""
        pass

    @abstractmethod
    async def count(self, record_type: Optional[str] = None) -> int:
        """Kayıt sayısı"""
        pass

    # Yardımcı metodlar
    async def exists(self, record_id: str) -> bool:
        """Kayıt var mı?"""
        return await self.get(record_id) is not None

    async def get_by_type(self, record_type: str) -> List[T]:
        """Tipe göre kayıtlar"""
        return await self.get_all(record_type)

    async def get_by_tags(self, tags: List[str]) -> List[T]:
        """Tag'lere göre kayıtlar"""
        all_records = await self.get_all()
        return [r for r in all_records if any(t in r.tags for t in tags)]

    async def get_recent(self, limit: int = 10, record_type: Optional[str] = None) -> List[T]:
        """Son kayıtlar"""
        records = await self.get_all(record_type)
        sorted_records = sorted(records, key=lambda r: r.created_at, reverse=True)
        return sorted_records[:limit]
