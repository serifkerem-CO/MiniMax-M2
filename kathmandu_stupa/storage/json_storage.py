"""
📁 JSON STORAGE - Dosya Tabanlı Arşiv
=====================================

Basit, taşınabilir JSON dosya storage.
Küçük-orta ölçekli kullanımlar için ideal.
"""

import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import aiofiles

from .base import StorageBackend, StorageRecord


class JSONStorage(StorageBackend[StorageRecord]):
    """
    📁 JSON Dosya Storage

    Her kayıt tipi için ayrı JSON dosyası.
    Kolay yedekleme ve taşıma.
    """

    def __init__(self, base_path: str = "./stupa_data"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

        # Index dosyası
        self.index_file = self.base_path / "index.json"
        self._index: Dict[str, str] = {}  # id -> type mapping
        self._cache: Dict[str, StorageRecord] = {}

    async def _load_index(self):
        """Index'i yükle"""
        if self.index_file.exists():
            async with aiofiles.open(self.index_file, 'r') as f:
                content = await f.read()
                self._index = json.loads(content) if content else {}

    async def _save_index(self):
        """Index'i kaydet"""
        async with aiofiles.open(self.index_file, 'w') as f:
            await f.write(json.dumps(self._index, indent=2))

    def _get_type_file(self, record_type: str) -> Path:
        """Tip için dosya yolu"""
        safe_name = record_type.replace("/", "_").replace("\\", "_")
        return self.base_path / f"{safe_name}.json"

    async def _load_type_file(self, record_type: str) -> List[Dict]:
        """Tip dosyasını yükle"""
        file_path = self._get_type_file(record_type)
        if not file_path.exists():
            return []

        async with aiofiles.open(file_path, 'r') as f:
            content = await f.read()
            return json.loads(content) if content else []

    async def _save_type_file(self, record_type: str, records: List[Dict]):
        """Tip dosyasını kaydet"""
        file_path = self._get_type_file(record_type)
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(records, indent=2, ensure_ascii=False))

    async def save(self, record: StorageRecord) -> str:
        """Kayıt kaydet"""
        await self._load_index()

        # Mevcut kayıtları yükle
        records = await self._load_type_file(record.type)

        # Mevcut kayıt varsa güncelle
        existing_idx = next((i for i, r in enumerate(records) if r["id"] == record.id), None)
        if existing_idx is not None:
            records[existing_idx] = record.to_dict()
        else:
            records.append(record.to_dict())

        # Kaydet
        await self._save_type_file(record.type, records)

        # Index güncelle
        self._index[record.id] = record.type
        await self._save_index()

        # Cache
        self._cache[record.id] = record

        return record.id

    async def get(self, record_id: str) -> Optional[StorageRecord]:
        """ID ile kayıt al"""
        # Cache kontrol
        if record_id in self._cache:
            return self._cache[record_id]

        await self._load_index()

        record_type = self._index.get(record_id)
        if not record_type:
            return None

        records = await self._load_type_file(record_type)
        for r in records:
            if r["id"] == record_id:
                record = StorageRecord.from_dict(r)
                self._cache[record_id] = record
                return record

        return None

    async def get_all(self, record_type: Optional[str] = None) -> List[StorageRecord]:
        """Tüm kayıtları al"""
        await self._load_index()

        if record_type:
            types = [record_type]
        else:
            types = list(set(self._index.values()))

        all_records = []
        for t in types:
            records = await self._load_type_file(t)
            all_records.extend([StorageRecord.from_dict(r) for r in records])

        return all_records

    async def update(self, record_id: str, data: Dict[str, Any]) -> bool:
        """Kayıt güncelle"""
        record = await self.get(record_id)
        if not record:
            return False

        # Data güncelle
        record.data.update(data)
        record.updated_at = datetime.now()

        await self.save(record)
        return True

    async def delete(self, record_id: str) -> bool:
        """Kayıt sil"""
        await self._load_index()

        record_type = self._index.get(record_id)
        if not record_type:
            return False

        # Kayıtları yükle ve filtrele
        records = await self._load_type_file(record_type)
        records = [r for r in records if r["id"] != record_id]
        await self._save_type_file(record_type, records)

        # Index'ten kaldır
        del self._index[record_id]
        await self._save_index()

        # Cache'ten kaldır
        self._cache.pop(record_id, None)

        return True

    async def search(self, query: Dict[str, Any]) -> List[StorageRecord]:
        """Basit arama"""
        all_records = await self.get_all()
        results = []

        for record in all_records:
            match = True
            for key, value in query.items():
                if key == "type":
                    if record.type != value:
                        match = False
                elif key == "tags":
                    if not any(t in record.tags for t in value):
                        match = False
                elif key in record.data:
                    if record.data[key] != value:
                        match = False
                else:
                    match = False

            if match:
                results.append(record)

        return results

    async def count(self, record_type: Optional[str] = None) -> int:
        """Kayıt sayısı"""
        records = await self.get_all(record_type)
        return len(records)

    async def clear_all(self):
        """Tüm verileri sil (dikkatli kullan!)"""
        import shutil
        if self.base_path.exists():
            shutil.rmtree(self.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self._index = {}
        self._cache = {}

    def get_stats(self) -> Dict:
        """Storage istatistikleri"""
        return {
            "base_path": str(self.base_path),
            "index_size": len(self._index),
            "cache_size": len(self._cache),
            "types": list(set(self._index.values())),
        }
