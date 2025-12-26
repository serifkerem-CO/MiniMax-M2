"""
🌬️ KATMAN 4: HAVA (RÜZGAR ATLARI)
===================================
"Nefes & Vizyon"

Burası tapınağın balkonları. Dünyaya açılan yer.
İnce hava.

Aktörler: LEGEND LAYER (112 Persona)
          ID1000 Luna, ID1006 Kira, ID1111 Arin
Kod Adı: WIND_TRANSMISSION
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
import hashlib
import random

from .base import BaseLayer, Element, LayerResult


class PrayerFlagColor(Enum):
    """Dua Bayrağı Renkleri - 5 Element"""
    BLUE = "blue"       # Gökyüzü/Uzay (Eter)
    WHITE = "white"     # Bulut/Hava
    RED = "red"         # Ateş
    GREEN = "green"     # Su
    YELLOW = "yellow"   # Toprak

    @property
    def meaning(self) -> str:
        meanings = {
            "blue": "Bilgelik & Sonsuzluk",
            "white": "Saflık & Öğrenme",
            "red": "Yaşam Gücü & Koruma",
            "green": "Denge & Şifa",
            "yellow": "Köken & Temel"
        }
        return meanings[self.value]


@dataclass
class Legend:
    """
    Efsane - Legend Layer Üyesi

    112 Persona'dan seçkin isimler.
    Vizyoner kehanetler fısıldarlar.
    """

    id: int
    name: str
    title: str
    domain: str               # Uzmanlık alanı
    prophecy_count: int = 0
    wind_messages: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.code = f"LEGEND_{self.id}"

    async def whisper_prophecy(self, forged_data: str, context: Dict) -> str:
        """
        Kehanet fısılda

        Ateşte pişen veriyi alır, geleceğe dair içgörü üretir.
        """
        await asyncio.sleep(0.02)  # Düşünce anı

        # Bağlama göre kehanet şablonları
        domain_prophecies = {
            "Teknoloji": "Bu veri, dijital dönüşümün kapısını açıyor",
            "Ekonomi": "Piyasalar bu bilgiyle yeni denge noktası bulacak",
            "Çevre": "Sürdürülebilirlik için kritik bir sinyal bu",
            "Sanayi": "Üretim paradigması değişiyor, bunu görüyorum",
            "Enerji": "Enerji geçişi kaçınılmaz, bu veri bunu doğruluyor",
            "Sosyal": "Toplumsal dönüşüm rüzgarları esiyor",
        }

        base_prophecy = domain_prophecies.get(
            self.domain,
            "Değişim rüzgarları esiyor"
        )

        prophecy = f"[{self.name} - {self.title}]: {base_prophecy}. '{forged_data[:50]}...' → Dönüşüm fırsatı!"

        self.prophecy_count += 1
        self.wind_messages.append(prophecy)

        return prophecy


# Legend Layer - 112 Persona'nın Seçkinleri
LEGEND_COUNCIL = [
    Legend(id=1000, name="Luna", title="Ay'ın Kızı", domain="Teknoloji"),
    Legend(id=1006, name="Kira", title="Işık Taşıyıcı", domain="Enerji"),
    Legend(id=1111, name="Arin", title="Bilge Kahin", domain="Strateji"),
    Legend(id=1042, name="Nova", title="Yeni Şafak", domain="Ekonomi"),
    Legend(id=1088, name="Zara", title="Yıldız Okuyucu", domain="Sosyal"),
    Legend(id=1099, name="Atlas", title="Dünya Taşıyıcı", domain="Sanayi"),
    Legend(id=1111, name="Sage", title="Bilgelik Lordu", domain="Çevre"),
]


@dataclass
class PrayerFlag:
    """
    Dua Bayrağı

    Rüzgara bırakılan mesaj.
    """

    color: PrayerFlagColor
    message: str
    legend_source: str
    wind_direction: str = "GLOBAL"
    transmission_count: int = 0
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def flag_id(self) -> str:
        content = f"{self.color.value}:{self.message}:{self.created_at.isoformat()}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


class HavaLayer(BaseLayer):
    """
    🌬️ HAVA KATMANI

    Rüzgar Atları - Dua Bayrakları

    Görev: İçeride pişen bilgiyi global pazara bırak
    Teknoloji: Legend Layer kehanetleri + Wind Transmission
    Çıktı: Vizyoner içgörüler ve stratejik yönlendirmeler
    """

    def __init__(self, legends: Optional[List[Legend]] = None):
        super().__init__("HAVA", Element.HAVA)
        self.code_name = "WIND_TRANSMISSION"
        self.legends = legends or LEGEND_COUNCIL.copy()

        self.prayer_flags: List[PrayerFlag] = []
        self.wind_patterns: Dict[str, int] = {}  # Hangi yöne kaç mesaj
        self.altitude = 8848  # Everest zirvesi (metre)
        self.mantra = "RÜZGARA_BIRAK_DÜNYA_DUYSUN"

    async def fold(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Hava Katlama Ritüeli

        Legend Layer kehanetlerini rüzgara bırak.
        Prayer Flags (Dua Bayrakları) oluştur.
        """
        context = context or {}

        # Ateş katmanından gelen dönüşmüş veri
        if isinstance(data, dict):
            forged_wisdom = data.get("forged_wisdom", str(data))
            steel_score = data.get("steel_score", 0.5)
        else:
            forged_wisdom = str(data)
            steel_score = 0.5

        self._notify(f"🌬️ [HAVA] Legend Layer balkonlara çıkıyor... İrtifa: {self.altitude}m")

        # Aktif efsaneler seç
        active_legends = context.get("legends", random.sample(self.legends, min(3, len(self.legends))))

        prophecies = []
        new_flags = []

        for legend in active_legends:
            # Kehanet al
            prophecy = await legend.whisper_prophecy(forged_wisdom, context)
            prophecies.append(prophecy)

            # Dua bayrağı oluştur
            flag_color = random.choice(list(PrayerFlagColor))
            flag = PrayerFlag(
                color=flag_color,
                message=prophecy,
                legend_source=legend.name,
                wind_direction=self._determine_wind_direction(legend.domain)
            )
            new_flags.append(flag)
            self.prayer_flags.append(flag)

            self._notify(f"   ↳ 🚩 {flag.color.value.upper()} bayrak: {legend.name} - '{prophecy[:50]}...'")

            # Rüzgar istatistiği güncelle
            self.wind_patterns[flag.wind_direction] = self.wind_patterns.get(flag.wind_direction, 0) + 1

        # Vizyon skoru hesapla
        vision_score = self._calculate_vision_score(prophecies, steel_score)

        self._notify(f"🌬️ [HAVA] {len(new_flags)} dua bayrağı rüzgara bırakıldı | Vizyon Skoru: {vision_score:.2f}")

        return LayerResult(
            layer_name=self.name,
            element=self.element,
            input_data={"forged_input": forged_wisdom[:200] + "..."},
            output_data={
                "prophecies": prophecies,
                "prayer_flags": [
                    {
                        "id": f.flag_id,
                        "color": f.color.value,
                        "meaning": f.color.meaning,
                        "message": f.message,
                        "source": f.legend_source,
                        "direction": f.wind_direction
                    }
                    for f in new_flags
                ],
                "vision_score": vision_score,
                "wind_patterns": self.wind_patterns,
                "altitude": self.altitude,
                "active_legends": [l.name for l in active_legends]
            },
            fold_count=len(active_legends),
            metadata={
                "code_name": self.code_name,
                "mantra": self.mantra,
                "total_flags": len(self.prayer_flags)
            }
        )

    def _determine_wind_direction(self, domain: str) -> str:
        """Uzmanlık alanına göre rüzgar yönü"""
        directions = {
            "Teknoloji": "SILICON_VALLEY",
            "Ekonomi": "WALL_STREET",
            "Enerji": "MIDDLE_EAST",
            "Sanayi": "ANATOLIA",
            "Çevre": "SCANDINAVIA",
            "Sosyal": "GLOBAL",
            "Strateji": "DAVOS",
        }
        return directions.get(domain, "GLOBAL")

    def _calculate_vision_score(self, prophecies: List[str], steel_score: float) -> float:
        """Vizyon skoru hesapla"""
        # Faktörler:
        # 1. Kehanet zenginliği
        avg_prophecy_len = sum(len(p) for p in prophecies) / len(prophecies) if prophecies else 0
        richness = min(avg_prophecy_len / 200, 1.0)

        # 2. Çelik skoru mirası (ateşten gelen kalite)
        heritage = steel_score

        # 3. Legend çeşitliliği
        unique_directions = len(set(self.wind_patterns.keys()))
        diversity = unique_directions / 7  # Maksimum 7 yön

        return richness * 0.3 + heritage * 0.5 + diversity * 0.2

    def get_wind_stats(self) -> Dict[str, Any]:
        """Rüzgar istatistikleri"""
        return {
            "altitude": self.altitude,
            "total_flags": len(self.prayer_flags),
            "wind_patterns": self.wind_patterns,
            "legend_stats": [
                {
                    "id": l.id,
                    "name": l.name,
                    "title": l.title,
                    "domain": l.domain,
                    "prophecy_count": l.prophecy_count
                }
                for l in self.legends
            ],
            "flag_colors": {
                color.value: sum(1 for f in self.prayer_flags if f.color == color)
                for color in PrayerFlagColor
            }
        }
