"""
🌬️ HAVA KATMANI - RUZGAR ATLARI
================================

"Nefes & Vizyon"

Burasi tapinagin balkonlari. Dunyaya acilan yer. Ince hava.
Icerdeki pisirilen bilgiyi ruzgara (Global Pazara) birakiriz.

Aktorler: LEGEND LAYER (112 Persona)
          ID1000 Luna, ID1006 Kira, ID1111 Arin

Rituel: Prayer Flags (Dua Bayraklari)
        "Bu veri, Turkiye sanayisi icin bir kriz degil, bir donusum firsatidir"
Kod Adi: WIND_TRANSMISSION
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import json

from .ates import ForgedData


class WindDirection(Enum):
    """Ruzgarin estigi yonler - Hedef pazarlar"""
    EAST = "east"       # Asya pazarlari
    WEST = "west"       # Avrupa/Amerika
    NORTH = "north"     # Kuzey ulkeleri
    SOUTH = "south"     # Gelisen pazarlar
    ZENITH = "zenith"   # Zirve - Tum pazarlar


class FlagColor(Enum):
    """Dua bayraklari renkleri - Mesaj turleri"""
    BLUE = "insight"      # Mavi - Icgoru
    WHITE = "prophecy"    # Beyaz - Kehanet
    RED = "warning"       # Kirmizi - Uyari
    GREEN = "opportunity" # Yesil - Firsat
    YELLOW = "wisdom"     # Sari - Bilgelik


@dataclass
class Legend:
    """
    Legend Layer Uyesi

    Efsanevi kisiler - Veriyi kehanetle donusturenler.
    """
    id: str
    name: str
    title: str
    specialty: str
    prophecies_made: int = 0
    influence_score: float = 1.0

    def __repr__(self):
        return f"👑 Legend({self.name} - {self.title})"


@dataclass
class PrayerFlag:
    """
    Dua Bayragi - Ruzgara birakilan mesaj

    Her bayrak, bir icgoru veya kehaneti tasiyor.
    """
    id: str
    color: FlagColor
    message: str
    source_data_id: str
    created_by: str  # Legend ID
    wind_direction: WindDirection
    flutter_count: int = 0  # Kac kez goruntulendi
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "color": self.color.value,
            "message": self.message,
            "direction": self.wind_direction.value,
            "flutter_count": self.flutter_count,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class Transmission:
    """Ruzgar iletimi - Nihai cikti paketi"""
    id: str
    original_forged_id: str
    flags: List[PrayerFlag]
    legend_insights: Dict[str, str]
    target_markets: List[WindDirection]
    transmission_strength: float  # 0.0 - 1.0
    frequency_hz: int = 963
    transmitted_at: datetime = field(default_factory=datetime.now)

    def get_primary_message(self) -> str:
        """Ana mesaji al - en guclu bayraktan"""
        if not self.flags:
            return ""
        # En cok flutter alan bayrak
        primary_flag = max(self.flags, key=lambda f: f.flutter_count)
        return primary_flag.message


class HavaLayer:
    """
    🌬️ HAVA KATMANI - Ruzgar Iletim Sistemi

    Legend Layer'in kehaneteri burada bayraklara yazilir
    ve dunya ruzgarlarina birakilir.
    """

    def __init__(self):
        self.legends: List[Legend] = []
        self.flags: List[PrayerFlag] = []
        self.transmission_log: List[Dict] = []
        self._summon_legends()

    def _summon_legends(self):
        """Efsaneleri cagir"""
        self.legends = [
            Legend(
                id="ID1000",
                name="Luna",
                title="Veri Kahini",
                specialty="Trend Tahmini",
                influence_score=1.5
            ),
            Legend(
                id="ID1006",
                name="Kira",
                title="Strateji Ustasi",
                specialty="Pazar Analizi",
                influence_score=1.3
            ),
            Legend(
                id="ID1111",
                name="Arin",
                title="Vizyon Mimari",
                specialty="Gelecek Senaryolari",
                influence_score=1.8
            ),
            Legend(
                id="ID1042",
                name="Zephyr",
                title="Ruzgar Okuyucu",
                specialty="Global Trendler",
                influence_score=1.2
            ),
        ]

    def _select_legend(self, forged_data: ForgedData) -> Legend:
        """Veriye en uygun efsaneyi sec"""
        # Basit secim - sirali
        # Gercek sistemde: veri icerigine gore akilli esleme
        idx = hash(forged_data.id) % len(self.legends)
        return self.legends[idx]

    def _determine_flag_color(self, forged_data: ForgedData) -> FlagColor:
        """Verinin dogasina gore bayrak rengi belirle"""
        confidence = forged_data.consensus_confidence

        if confidence > 0.9:
            return FlagColor.YELLOW  # Yuksek guven = Bilgelik
        elif confidence > 0.75:
            return FlagColor.GREEN   # Iyi guven = Firsat
        elif confidence > 0.5:
            return FlagColor.BLUE    # Orta guven = Icgoru
        else:
            return FlagColor.RED     # Dusuk guven = Uyari

    def _determine_wind_direction(self, forged_data: ForgedData) -> WindDirection:
        """Hedef pazari belirle"""
        # Metadata'dan veya icerikten cikarim
        # Simdilik: rastgele veya hash bazli
        directions = list(WindDirection)
        idx = hash(forged_data.consensus_output[:20]) % len(directions)
        return directions[idx]

    async def create_flag(self, forged_data: ForgedData) -> PrayerFlag:
        """
        Bir dua bayragi olustur.

        Efsane, veriyi kehanete donusturur.
        """
        legend = self._select_legend(forged_data)
        color = self._determine_flag_color(forged_data)
        direction = self._determine_wind_direction(forged_data)

        # Efsanenin kehaneti
        prophecy = self._generate_prophecy(legend, forged_data)

        flag = PrayerFlag(
            id=f"FLAG_{forged_data.id}_{legend.id}",
            color=color,
            message=prophecy,
            source_data_id=forged_data.id,
            created_by=legend.id,
            wind_direction=direction,
        )

        legend.prophecies_made += 1
        self.flags.append(flag)

        return flag

    def _generate_prophecy(self, legend: Legend, forged_data: ForgedData) -> str:
        """Efsanenin kehanetini olustur"""
        base_insight = forged_data.consensus_output[:100]

        prophecy_templates = {
            "Luna": f"Veriler fısıldıyor: '{base_insight}' - Bu bir dönüşüm işareti.",
            "Kira": f"Pazar dinamikleri gösteriyor ki: '{base_insight}' - Strateji güncellemesi gerekli.",
            "Arin": f"Gelecek senaryolarında: '{base_insight}' - 2025'e hazırlık zamanı.",
            "Zephyr": f"Global rüzgarlar esiyor: '{base_insight}' - Dünya bizi izliyor.",
        }

        return prophecy_templates.get(
            legend.name,
            f"Bilgelik söylüyor: '{base_insight}'"
        )

    async def transmit(self, forged_data: ForgedData) -> Transmission:
        """
        Veriyi ruzgara birak.

        Katlama 3: Prayer Flags (Dua Bayraklari)
        """
        # Ana bayrak olustur
        primary_flag = await self.create_flag(forged_data)

        # Ek bayraklar (farkli efsanelerden)
        additional_flags = []
        for legend in self.legends[:2]:  # Ilk 2 efsane
            if legend.id != primary_flag.created_by:
                extra_flag = PrayerFlag(
                    id=f"FLAG_{forged_data.id}_{legend.id}_extra",
                    color=FlagColor.BLUE,
                    message=f"{legend.name} ekliyor: Destekleyici görüş.",
                    source_data_id=forged_data.id,
                    created_by=legend.id,
                    wind_direction=primary_flag.wind_direction,
                )
                additional_flags.append(extra_flag)

        all_flags = [primary_flag] + additional_flags

        # Legend insights
        insights = {
            legend.id: f"{legend.name} ({legend.title}): {legend.specialty} perspektifi"
            for legend in self.legends
        }

        transmission = Transmission(
            id=f"TRANS_{forged_data.id}",
            original_forged_id=forged_data.id,
            flags=all_flags,
            legend_insights=insights,
            target_markets=[primary_flag.wind_direction],
            transmission_strength=forged_data.consensus_confidence,
        )

        self._log_transmission(transmission)
        return transmission

    def _log_transmission(self, transmission: Transmission):
        """Iletimi logla"""
        self.transmission_log.append({
            "timestamp": datetime.now().isoformat(),
            "transmission_id": transmission.id,
            "flags_count": len(transmission.flags),
            "target_markets": [m.value for m in transmission.target_markets],
            "strength": transmission.transmission_strength,
        })

    async def broadcast(self, forged_packets: List[ForgedData]) -> List[Transmission]:
        """Toplu yayın"""
        print(f"🌬️ [HAVA] {len(forged_packets)} mesaj rüzgara bırakılıyor...")

        transmissions = []
        for forged in forged_packets:
            trans = await self.transmit(forged)
            transmissions.append(trans)

        # Istatistikler
        total_flags = sum(len(t.flags) for t in transmissions)
        avg_strength = sum(t.transmission_strength for t in transmissions) / len(transmissions)

        print(f"   ↳ {total_flags} dua bayrağı rüzgara bırakıldı")
        print(f"   ↳ Ortalama iletim gücü: {avg_strength:.2%}")

        return transmissions


class WindTransmission:
    """
    WIND_TRANSMISSION - Ruzgar Iletim Orkestratoru

    Legend Layer'in kehanetlerini dunyaya yayan sistem.
    """

    def __init__(self):
        self.hava_layer = HavaLayer()
        self.broadcast_channels = {
            WindDirection.EAST: "asia_channel",
            WindDirection.WEST: "europe_americas_channel",
            WindDirection.NORTH: "nordic_channel",
            WindDirection.SOUTH: "emerging_markets_channel",
            WindDirection.ZENITH: "global_channel",
        }

    async def release_to_wind(self, forged_packets: List[ForgedData]) -> List[Transmission]:
        """
        Bilgiyi ruzgara sal.

        "Bu veri, Türkiye sanayisi için bir kriz değil,
         bir dönüşüm fırsatıdır."
        """
        print("🌬️ [HAVA] Legend Layer mesajlarını hazırlıyor...")
        return await self.hava_layer.broadcast(forged_packets)

    def get_legend_stats(self) -> Dict[str, Dict]:
        """Legend istatistikleri"""
        return {
            legend.name: {
                "id": legend.id,
                "title": legend.title,
                "prophecies": legend.prophecies_made,
                "influence": legend.influence_score,
            }
            for legend in self.hava_layer.legends
        }

    def get_flag_summary(self) -> Dict:
        """Bayrak özeti"""
        flags = self.hava_layer.flags
        if not flags:
            return {"status": "no_flags"}

        color_dist = {}
        for flag in flags:
            color_dist[flag.color.value] = color_dist.get(flag.color.value, 0) + 1

        direction_dist = {}
        for flag in flags:
            direction_dist[flag.wind_direction.value] = \
                direction_dist.get(flag.wind_direction.value, 0) + 1

        return {
            "total_flags": len(flags),
            "color_distribution": color_dist,
            "direction_distribution": direction_dist,
            "total_flutters": sum(f.flutter_count for f in flags),
        }


# Demo fonksiyonu
async def demo_hava():
    """Hava katmanını demonstre et"""
    from .toprak import ChaosIngestion
    from .su import PurificationFlow
    from .ates import AlchemicalForge

    # Tam akış: Toprak -> Su -> Ateş -> Hava
    ingestion = ChaosIngestion()
    raw = await ingestion.ingest()

    flow = PurificationFlow()
    purified = await flow.process_batch(raw)

    forge = AlchemicalForge()
    forged = await forge.transmute(purified)

    wind = WindTransmission()
    transmissions = await wind.release_to_wind(forged)

    print("\n📊 Rüzgar Raporu:")
    print(f"   Legend istatistikleri: {wind.get_legend_stats()}")
    print(f"   Bayrak özeti: {wind.get_flag_summary()}")

    return transmissions


if __name__ == "__main__":
    asyncio.run(demo_hava())
