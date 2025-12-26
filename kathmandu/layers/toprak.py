"""
🪨 KATMAN 1: TOPRAK (THAMEL SOKAKLARI)
======================================
"Kökler Derinde & Pazar Yeri Kaosu"

Burası Kathmandu'nun tozlu, karmaşık, baharat ve
kağıt kokan o dar sokaklarıdır.

Aktörler: GLITCH LAB (111 Persona)
Kod Adı: CHAOS_INGESTION
"""

import asyncio
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import hashlib

from .base import BaseLayer, Element, LayerResult


class DataSource(Enum):
    """Thamel Pazarı'ndaki Veri Kaynakları"""
    PDF = "pdf"
    CSV = "csv"
    JSON = "json"
    HTML = "html"
    API = "api"
    SOCIAL_MEDIA = "social"
    ARCHIVE = "archive"      # 40 yıllık tozlu dosyalar
    STREAM = "stream"        # Canlı veri akışı
    UNKNOWN = "unknown"      # Gizemli paket


@dataclass
class RawDataPacket:
    """Thamel'den gelen ham veri paketi"""

    source: DataSource
    content: Any
    origin: str                      # Nereden geldi
    timestamp: datetime
    dust_level: float = 0.0          # Toz seviyesi (0-1)
    chaos_index: float = 0.0         # Kaos endeksi (0-1)
    merchant_id: Optional[str] = None  # Hangi "tüccar" getirdi

    def __post_init__(self):
        # Kaos endeksini hesapla
        if isinstance(self.content, str):
            # Düzensizlik = özel karakter oranı + boşluk oranı
            special = len(re.findall(r'[^\w\s]', self.content))
            spaces = self.content.count(' ') + self.content.count('\n')
            total = len(self.content) or 1
            self.chaos_index = min((special + spaces) / total, 1.0)

    @property
    def lotus_potential(self) -> float:
        """Çamurun içindeki lotus potansiyeli"""
        # Yüksek kaos = yüksek lotus potansiyeli (paradoks!)
        return self.chaos_index * 0.7 + (1 - self.dust_level) * 0.3


class GlitchLabAgent:
    """
    GLITCH LAB Ajanı - Thamel'in Tüccarları

    111 Persona'dan biri. Kaosu kucaklar,
    çamurda lotus arar.
    """

    def __init__(self, agent_id: int, specialty: DataSource):
        self.agent_id = agent_id
        self.specialty = specialty
        self.name = f"GLITCH_{agent_id:03d}"
        self.collected_packets: List[RawDataPacket] = []

    async def scavenge(self, target: str) -> RawDataPacket:
        """
        Thamel sokaklarında veri avı

        Args:
            target: Hedef veri kaynağı/dosya

        Returns:
            RawDataPacket: Toplanan ham veri
        """
        # Simüle edilmiş veri toplama
        await asyncio.sleep(0.1)  # Sokakta dolaşma süresi

        # Dosya uzantısından kaynak türü belirle
        source = self._detect_source(target)

        packet = RawDataPacket(
            source=source,
            content=f"RAW_DATA_FROM_{target}",
            origin=target,
            timestamp=datetime.now(),
            dust_level=0.3,  # Varsayılan toz seviyesi
            merchant_id=self.name
        )

        self.collected_packets.append(packet)
        return packet

    def _detect_source(self, target: str) -> DataSource:
        """Hedeften kaynak türünü tespit et"""
        target_lower = target.lower()

        if target_lower.endswith('.pdf'):
            return DataSource.PDF
        elif target_lower.endswith('.csv'):
            return DataSource.CSV
        elif target_lower.endswith('.json'):
            return DataSource.JSON
        elif target_lower.endswith('.html') or target_lower.startswith('http'):
            return DataSource.HTML
        elif 'api' in target_lower:
            return DataSource.API
        elif any(s in target_lower for s in ['twitter', 'instagram', 'facebook']):
            return DataSource.SOCIAL_MEDIA
        elif any(year in target_lower for year in ['1984', '1990', '2000']):
            return DataSource.ARCHIVE
        else:
            return DataSource.UNKNOWN


class ToprakLayer(BaseLayer):
    """
    🪨 TOPRAK KATMANI

    Thamel Pazarı - Kaosu Kucakla

    Görev: Ham verileri topla, çuvallara doldur
    Teknoloji: DeepSeek + Scraping Botları
    Çıktı: Yapılandırılmamış ama zengin veri havuzu
    """

    def __init__(self, num_agents: int = 7):
        super().__init__("TOPRAK", Element.TOPRAK)
        self.code_name = "CHAOS_INGESTION"

        # Glitch Lab ajanları oluştur
        specialties = list(DataSource)
        self.agents = [
            GlitchLabAgent(
                agent_id=i + 1,
                specialty=specialties[i % len(specialties)]
            )
            for i in range(num_agents)
        ]

        self.data_sacks: List[RawDataPacket] = []  # Çuvallar
        self.mantra = "KAOSU_KUCAKLA_LOTUSU_BUL"

    async def fold(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Toprak Katlama Ritüeli

        Ham veriyi topla, çuvala koy, bir sonraki katmana hazırla.
        """
        context = context or {}
        sources = context.get("sources", [data] if not isinstance(data, list) else data)

        self._notify(f"🪨 [TOPRAK] Glitch Lab {len(sources)} hedefte veri avına çıkıyor...")

        # Paralel veri toplama - her ajan bir hedefte
        tasks = []
        for i, source in enumerate(sources):
            agent = self.agents[i % len(self.agents)]
            tasks.append(agent.scavenge(str(source)))

        collected = await asyncio.gather(*tasks, return_exceptions=True)

        # Hatalı olmayanları filtrele
        valid_packets = [p for p in collected if isinstance(p, RawDataPacket)]
        self.data_sacks.extend(valid_packets)

        # Kaos istatistikleri
        avg_chaos = sum(p.chaos_index for p in valid_packets) / len(valid_packets) if valid_packets else 0
        avg_lotus = sum(p.lotus_potential for p in valid_packets) / len(valid_packets) if valid_packets else 0

        self._notify(f"🪨 [TOPRAK] {len(valid_packets)} çuval dolduruldu | Kaos: {avg_chaos:.2f} | Lotus: {avg_lotus:.2f}")

        return LayerResult(
            layer_name=self.name,
            element=self.element,
            input_data=sources,
            output_data={
                "packets": [
                    {
                        "source": p.source.value,
                        "origin": p.origin,
                        "chaos_index": p.chaos_index,
                        "lotus_potential": p.lotus_potential,
                        "merchant": p.merchant_id
                    }
                    for p in valid_packets
                ],
                "total_collected": len(valid_packets),
                "avg_chaos_index": avg_chaos,
                "avg_lotus_potential": avg_lotus
            },
            fold_count=1,
            metadata={
                "code_name": self.code_name,
                "mantra": self.mantra,
                "active_agents": len(self.agents)
            }
        )

    def get_sacks(self) -> List[RawDataPacket]:
        """Dolu çuvalları al"""
        return self.data_sacks

    def clear_sacks(self) -> int:
        """Çuvalları boşalt (bir sonraki katmana geçti)"""
        count = len(self.data_sacks)
        self.data_sacks = []
        return count
