"""
TOPRAK KATMANI - THAMEL SOKAKLARI
=================================
"Kokler Derinde & Pazar Yeri Kaosu"

Kathmandu'nun tozlu, karmasik, baharat ve kagit kokan dar sokaklari.
Ham veriler burada toplanir: CED raporlari, sanayi sicilleri, 40 yillik
tozlu PDF'ler, sosyal medya gurultusu.

Aktorler: GLITCH LAB (111 Persona) - Carsinin Tuccarlari
Rituel: Kaosu kucakla. DeepSeek ve Scraping Botlari dolasiyor.
Kod Adi: CHAOS_INGESTION
"""

import asyncio
import hashlib
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Optional
import json
import re


class DataSourceType(Enum):
    """Thamel Pazarindaki Veri Kaynaklari"""
    PDF_DOCUMENT = "pdf"           # Tozlu arsivler
    WEB_SCRAPE = "web"             # Dijital pazarlar
    API_FEED = "api"               # Canli akislar
    DATABASE = "db"                # Eski defterler
    SOCIAL_MEDIA = "social"        # Sokak dedikodulari
    IOT_SENSOR = "iot"             # Dijital tuccarlarin gozleri
    MANUAL_INPUT = "manual"        # Elle yazilan notlar


@dataclass
class RawDataPacket:
    """Ham veri paketi - Thamel'den gelen cuvaller"""
    source_id: str
    source_type: DataSourceType
    content: Any
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    checksum: str = ""

    def __post_init__(self):
        """Cuvalin muhru"""
        content_str = str(self.content).encode('utf-8')
        self.checksum = hashlib.sha256(content_str).hexdigest()[:16]

    def to_dict(self) -> dict:
        return {
            "source_id": self.source_id,
            "source_type": self.source_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp.isoformat(),
            "checksum": self.checksum
        }


class GlitchLabPersona:
    """GLITCH LAB Tuccar Personasi (111 Persona Pool)"""

    def __init__(self, persona_id: int, specialty: str):
        self.persona_id = persona_id
        self.specialty = specialty
        self.items_collected = 0
        self.active = True

    async def collect(self, source: str) -> Optional[RawDataPacket]:
        """Pazarda dolasip veri toplama"""
        # Simule edilen toplama suresi
        await asyncio.sleep(0.1)
        self.items_collected += 1
        return RawDataPacket(
            source_id=f"glitch_{self.persona_id}_{source}",
            source_type=DataSourceType.MANUAL_INPUT,
            content={"collected_by": self.specialty, "source": source},
            metadata={"persona_id": self.persona_id}
        )


class ToprakLayer:
    """
    TOPRAK KATMANI - Chaos Ingestion Layer

    Gorev: Ham veriyi kaotik kaynaklardan toplamak
    Frekans: Topragin titresimi - 7.83Hz (Schumann)
    """

    LAYER_NAME = "TOPRAK"
    LAYER_EMOJI = "earth"
    LAYER_CODE = "CHAOS_INGESTION"
    FREQUENCY_HZ = 7.83  # Schumann Rezonansi

    def __init__(self, max_workers: int = 111):
        self.max_workers = max_workers
        self.active_personas: list[GlitchLabPersona] = []
        self.ingestion_queue: asyncio.Queue = asyncio.Queue()
        self.collected_packets: list[RawDataPacket] = []
        self._initialize_personas()

    def _initialize_personas(self):
        """111 Glitch Lab personasini baslat"""
        specialties = [
            "PDF_Arkeologu", "Web_Avcisi", "API_Simyacisi",
            "Veritabani_Kazicisi", "Sosyal_Dinleyici", "IoT_Fisildayici"
        ]
        for i in range(self.max_workers):
            specialty = specialties[i % len(specialties)]
            self.active_personas.append(GlitchLabPersona(i, specialty))

    async def ingest_file(self, file_path: Path) -> RawDataPacket:
        """Dosyayi Thamel pazarina sok"""
        mime_type, _ = mimetypes.guess_type(str(file_path))

        # Dosya tipine gore kaynak belirle
        source_type = DataSourceType.MANUAL_INPUT
        if mime_type and 'pdf' in mime_type:
            source_type = DataSourceType.PDF_DOCUMENT

        content = {
            "file_path": str(file_path),
            "file_name": file_path.name,
            "mime_type": mime_type,
            "size_bytes": file_path.stat().st_size if file_path.exists() else 0
        }

        packet = RawDataPacket(
            source_id=f"file_{file_path.stem}",
            source_type=source_type,
            content=content,
            metadata={"ingestion_layer": self.LAYER_NAME}
        )

        self.collected_packets.append(packet)
        return packet

    async def ingest_text(self, text: str, source_name: str = "manual") -> RawDataPacket:
        """Ham metni Thamel'e sok"""
        packet = RawDataPacket(
            source_id=f"text_{source_name}_{datetime.now().timestamp()}",
            source_type=DataSourceType.MANUAL_INPUT,
            content={"raw_text": text, "char_count": len(text)},
            metadata={"source_name": source_name}
        )
        self.collected_packets.append(packet)
        return packet

    async def ingest_json(self, data: dict, source_name: str = "api") -> RawDataPacket:
        """JSON verisini isle"""
        packet = RawDataPacket(
            source_id=f"json_{source_name}_{datetime.now().timestamp()}",
            source_type=DataSourceType.API_FEED,
            content=data,
            metadata={"key_count": len(data.keys()) if isinstance(data, dict) else 0}
        )
        self.collected_packets.append(packet)
        return packet

    async def scrape_chaos(self, sources: list[str]) -> AsyncIterator[RawDataPacket]:
        """
        Birden fazla kaynaktan paralel kaotik toplama
        Tuccarlari pazara sal!
        """
        tasks = []
        for i, source in enumerate(sources):
            persona = self.active_personas[i % len(self.active_personas)]
            tasks.append(persona.collect(source))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, RawDataPacket):
                self.collected_packets.append(result)
                yield result

    def get_chaos_stats(self) -> dict:
        """Pazar istatistikleri"""
        return {
            "layer": self.LAYER_NAME,
            "code": self.LAYER_CODE,
            "frequency_hz": self.FREQUENCY_HZ,
            "active_personas": len([p for p in self.active_personas if p.active]),
            "total_collected": len(self.collected_packets),
            "packets_by_type": self._count_by_type()
        }

    def _count_by_type(self) -> dict:
        """Tip bazli sayim"""
        counts = {}
        for packet in self.collected_packets:
            type_name = packet.source_type.value
            counts[type_name] = counts.get(type_name, 0) + 1
        return counts

    def extract_lotus_from_mud(self, packet: RawDataPacket) -> dict:
        """
        Camurdaki Lotusu Bul
        Ham veriden potansiyel degeri cikar
        """
        content = packet.content
        lotus = {
            "packet_id": packet.source_id,
            "checksum": packet.checksum,
            "potential_value": "unknown",
            "extraction_hints": []
        }

        # Icerik analizine gore ipuclari
        if isinstance(content, dict):
            if "raw_text" in content:
                text = content["raw_text"]
                # Anahtar kelime tespiti
                if any(kw in text.lower() for kw in ["rapor", "analiz", "veri", "sonuc"]):
                    lotus["potential_value"] = "high"
                    lotus["extraction_hints"].append("Rapor icerigi tespit edildi")

            if "file_path" in content:
                if ".pdf" in content.get("file_name", ""):
                    lotus["potential_value"] = "medium"
                    lotus["extraction_hints"].append("PDF dokumani - OCR gerekebilir")

        return lotus

    def __repr__(self):
        return f"<ToprakLayer: {len(self.collected_packets)} packets, {self.max_workers} personas>"


# Rituel Fonksiyonlari
async def thamel_ritual(sources: list[str]) -> list[RawDataPacket]:
    """
    THAMEL RITUELI
    Kaosu kucakla, camurun icindeki lotusu bul
    """
    layer = ToprakLayer()
    packets = []

    print(f"Thamel Sokaklari aciliyor... {len(sources)} kaynak tespit edildi")

    async for packet in layer.scrape_chaos(sources):
        lotus = layer.extract_lotus_from_mud(packet)
        print(f"  Lotus bulundu: {lotus['packet_id']} - Deger: {lotus['potential_value']}")
        packets.append(packet)

    return packets
