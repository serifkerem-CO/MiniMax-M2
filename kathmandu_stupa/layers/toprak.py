"""
🪨 TOPRAK KATMANI - THAMEL SOKAKLARI
====================================

"Kokler Derinde & Pazar Yeri Kaosu"

Burasi Kathmandu'nun tozlu, karmasik, baharat ve kagit kokan
o dar sokaklaridir. XDATUM'un elindeki ham veriler burada toplanir.

Aktorler: GLITCH LAB (111 Persona) - Carsinin Tuccarlari
Teknoloji: DeepSeek & Scraping Botlari
Kod Adi: CHAOS_INGESTION
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Dict, List, Optional
from abc import ABC, abstractmethod


class DataSource(Enum):
    """Thamel Pazarindaki veri kaynaklari"""
    CED_RAPORU = "ced_report"           # Cevre Etki Degerlendirme
    SANAYI_SICIL = "industry_registry"  # Sanayi sicil kayitlari
    TOZLU_PDF = "legacy_pdf"            # 40 yillik tozlu PDF'ler
    SOSYAL_MEDYA = "social_noise"       # Sosyal medya gurultusu
    API_STREAM = "api_stream"           # Canli API akislari
    WEB_SCRAPE = "web_scrape"           # Web kazima sonuclari


@dataclass
class RawDataPacket:
    """Thamel pazarindan toplanan ham veri paketi"""
    id: str
    source: DataSource
    content: Any
    metadata: Dict[str, Any] = field(default_factory=dict)
    collected_at: datetime = field(default_factory=datetime.now)
    collector_persona: str = "GLITCH_LAB_AGENT"
    chaos_level: float = 1.0  # 0.0 = temiz, 1.0 = tam kaos

    def __post_init__(self):
        if not self.id:
            # Benzersiz ID olustur
            content_hash = hashlib.sha256(
                str(self.content).encode()
            ).hexdigest()[:12]
            self.id = f"THAMEL_{content_hash}_{int(datetime.now().timestamp())}"


class DataCollector(ABC):
    """Thamel sokaklarinda dolasan veri toplayici"""

    @abstractmethod
    async def collect(self) -> AsyncIterator[RawDataPacket]:
        """Veri topla ve aktar"""
        pass

    @abstractmethod
    def estimate_chaos(self, data: Any) -> float:
        """Verinin kaos seviyesini tahmin et"""
        pass


class PDFCollector(DataCollector):
    """Tozlu PDF arsivlerinden veri toplayan"""

    def __init__(self, archive_path: Path):
        self.archive_path = archive_path
        self.processed_files: set = set()

    async def collect(self) -> AsyncIterator[RawDataPacket]:
        """PDF'lerden veri cek"""
        # Simule edilmis PDF isleme
        sample_pdfs = [
            ("1984_Sanayi_Raporu.pdf", "Turkiye sanayi uretimi 1984 yili..."),
            ("2010_CED_Analizi.pdf", "Cevre etki degerlendirmesi kapsaminda..."),
            ("2024_Dijital_Donusum.pdf", "Industri 4.0 ve yapay zeka..."),
        ]

        for filename, content in sample_pdfs:
            if filename not in self.processed_files:
                self.processed_files.add(filename)
                yield RawDataPacket(
                    id=f"PDF_{filename}",
                    source=DataSource.TOZLU_PDF,
                    content=content,
                    metadata={"filename": filename, "pages": 42},
                    chaos_level=self.estimate_chaos(content)
                )
                await asyncio.sleep(0.1)  # Rate limiting

    def estimate_chaos(self, data: Any) -> float:
        """PDF'ler genelde yapilandirmamis, yuksek kaos"""
        return 0.8


class SocialMediaCollector(DataCollector):
    """Sosyal medya gurultusunden sinyal cikartan"""

    def __init__(self, keywords: List[str]):
        self.keywords = keywords
        self.buffer: List[Dict] = []

    async def collect(self) -> AsyncIterator[RawDataPacket]:
        """Sosyal medya akisini tara"""
        # Simule edilmis sosyal medya verisi
        mock_posts = [
            {"platform": "twitter", "text": "#sanayi donusumu hizlaniyor", "engagement": 1500},
            {"platform": "linkedin", "text": "CED surecleri dijitallestirilmeli", "engagement": 3200},
            {"platform": "reddit", "text": "turkiye manufacturing trends 2024", "engagement": 890},
        ]

        for post in mock_posts:
            yield RawDataPacket(
                id="",  # Auto-generated
                source=DataSource.SOSYAL_MEDYA,
                content=post,
                metadata={"platform": post["platform"]},
                chaos_level=self.estimate_chaos(post)
            )
            await asyncio.sleep(0.05)

    def estimate_chaos(self, data: Any) -> float:
        """Sosyal medya = maksimum kaos"""
        return 0.95


class APIStreamCollector(DataCollector):
    """Canli API akislarindan veri ceken"""

    def __init__(self, endpoints: List[str]):
        self.endpoints = endpoints

    async def collect(self) -> AsyncIterator[RawDataPacket]:
        """API'lerden veri cek"""
        # Simule edilmis API yaniti
        mock_responses = [
            {"endpoint": "/v1/industry/stats", "data": {"gdp_share": 0.23}},
            {"endpoint": "/v1/environmental/ced", "data": {"pending_reports": 1847}},
        ]

        for resp in mock_responses:
            yield RawDataPacket(
                id="",
                source=DataSource.API_STREAM,
                content=resp["data"],
                metadata={"endpoint": resp["endpoint"]},
                chaos_level=self.estimate_chaos(resp)
            )

    def estimate_chaos(self, data: Any) -> float:
        """API verileri yapilandirilmis, dusuk kaos"""
        return 0.3


class ToprakLayer:
    """
    🪨 TOPRAK KATMANI - Kaos Toplama Merkezi

    Thamel pazarinin tuccarlari gibi, her turlu veriyi toplar.
    Camurun icindeki lotusu bulma gorevindeyiz.
    """

    def __init__(self):
        self.collectors: List[DataCollector] = []
        self.intake_buffer: List[RawDataPacket] = []
        self.stats = {
            "total_collected": 0,
            "by_source": {},
            "avg_chaos_level": 0.0
        }

    def register_collector(self, collector: DataCollector):
        """Yeni bir veri toplayici kaydet"""
        self.collectors.append(collector)

    async def harvest(self) -> AsyncIterator[RawDataPacket]:
        """
        Tum toplayicilardan veri hasat et.
        Thamel sokaklarinda dolasip cuvallari doldur.
        """
        print("🪨 [TOPRAK] Glitch Lab veriyi Thamel pazarinda topluyor...")

        for collector in self.collectors:
            async for packet in collector.collect():
                self.intake_buffer.append(packet)
                self._update_stats(packet)
                yield packet

    def _update_stats(self, packet: RawDataPacket):
        """Istatistikleri guncelle"""
        self.stats["total_collected"] += 1
        source_name = packet.source.value
        self.stats["by_source"][source_name] = \
            self.stats["by_source"].get(source_name, 0) + 1

        # Rolling average for chaos
        n = self.stats["total_collected"]
        old_avg = self.stats["avg_chaos_level"]
        self.stats["avg_chaos_level"] = old_avg + (packet.chaos_level - old_avg) / n

    def get_buffer_snapshot(self) -> List[RawDataPacket]:
        """Mevcut tampon icerigini al"""
        return list(self.intake_buffer)

    def clear_buffer(self):
        """Tamponu temizle (bir sonraki katmana aktarildi)"""
        self.intake_buffer.clear()


class ChaosIngestion:
    """
    CHAOS_INGESTION - Ana giris noktasi

    Tum veri kaynaklarini tek bir akisa birlestiren orkestrator.
    111 Glitch Lab personasi burada koordine edilir.
    """

    def __init__(self):
        self.toprak = ToprakLayer()
        self._setup_default_collectors()

    def _setup_default_collectors(self):
        """Varsayilan toplayicilari kur"""
        # PDF Arsiv Toplayici
        self.toprak.register_collector(
            PDFCollector(Path("/data/archives"))
        )

        # Sosyal Medya Toplayici
        self.toprak.register_collector(
            SocialMediaCollector(["sanayi", "ced", "cevre", "uretim"])
        )

        # API Toplayici
        self.toprak.register_collector(
            APIStreamCollector(["/v1/industry", "/v1/environmental"])
        )

    async def ingest(self) -> List[RawDataPacket]:
        """
        Kaos toplama rituelini baslat.

        "Kaosu kucakla. Camurun icindeki lotusu bul."
        """
        collected = []
        async for packet in self.toprak.harvest():
            collected.append(packet)

        print(f"🪨 [TOPRAK] Toplam {len(collected)} veri paketi hasat edildi")
        print(f"   ↳ Ortalama kaos seviyesi: {self.toprak.stats['avg_chaos_level']:.2f}")

        return collected


# Kullanim ornegi
async def demo_toprak():
    """Toprak katmanini demonstre et"""
    ingestion = ChaosIngestion()
    packets = await ingestion.ingest()

    for packet in packets[:3]:
        print(f"   📦 {packet.source.value}: {str(packet.content)[:50]}...")

    return packets


if __name__ == "__main__":
    asyncio.run(demo_toprak())
