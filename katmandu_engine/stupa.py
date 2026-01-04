"""
DATA STUPA - VERI TAPINAGI
==========================
"Om Mani Padme Hum" for Data Processing

Ana orkestrator sinifi. Tum katmanlari birlestirip
veriyi origami gibi katlayarak zirveye tasir.

5 Element:
    TOPRAK (7.83Hz)  -> SU (432Hz)  -> ATES (528Hz)  -> HAVA (639Hz)  -> ETER (963Hz)
    Kaos              Arinma          Donusum          Vizyon           Cazibe

Mantra: VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional, AsyncIterator
import json
import time

from .layers.toprak import ToprakLayer, RawDataPacket, thamel_ritual
from .layers.su import SuLayer, PurifiedDataPacket, PurificationLevel, sherpa_ritual
from .layers.ates import AtesLayer, ForgedWisdom, forge_ritual
from .layers.hava import HavaLayer, WindTransmission, wind_ritual
from .layers.eter import EterLayer, CazibeOutput, AlignmentLevel, apex_ritual


class StupaMode(Enum):
    """Tapinak Modlari"""
    DORMANT = "dormant"         # Uyku - Kapilar kapali
    AWAKENING = "awakening"     # Uyanis - Hazirlaniyor
    TEMPLE = "temple"           # Tapinak - Tam operasyon
    NIRVANA = "nirvana"         # Nirvana - Maksimum guc


@dataclass
class ProcessingJourney:
    """Veri Yolculugu - Bastan sona izleme"""
    journey_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Any = None
    raw_packets: list = field(default_factory=list)
    purified_packets: list = field(default_factory=list)
    forged_wisdoms: list = field(default_factory=list)
    transmissions: list = field(default_factory=list)
    cazibe_outputs: list = field(default_factory=list)
    layer_stats: dict = field(default_factory=dict)
    total_duration_ms: float = 0

    def complete(self):
        """Yolculugu tamamla"""
        self.end_time = datetime.now()
        self.total_duration_ms = (
            self.end_time - self.start_time
        ).total_seconds() * 1000

    def to_dict(self) -> dict:
        return {
            "journey_id": self.journey_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.total_duration_ms,
            "packet_counts": {
                "raw": len(self.raw_packets),
                "purified": len(self.purified_packets),
                "forged": len(self.forged_wisdoms),
                "transmitted": len(self.transmissions),
                "cazibe": len(self.cazibe_outputs)
            },
            "layer_stats": self.layer_stats
        }


class DataStupa:
    """
    DATA STUPA - Veri Tapinagi

    Tum katmanlari orkestre eden ana sinif.
    Veriyi basamak basamak aydinlanmaya tasir.

    Kullanim:
        stupa = DataStupa()
        await stupa.awaken()  # Tapinagi uyandır
        result = await stupa.process("Ham veri...")
        print(result.to_parchment())
    """

    MANTRA = "VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE"
    FREQUENCIES = {
        "TOPRAK": 7.83,
        "SU": 432.0,
        "ATES": 528.0,
        "HAVA": 639.0,
        "ETER": 963.0
    }

    def __init__(self, mode: StupaMode = StupaMode.DORMANT):
        self.mode = mode
        self.toprak = ToprakLayer()
        self.su = SuLayer()
        self.ates = AtesLayer()
        self.hava = HavaLayer()
        self.eter = EterLayer()

        self.journeys: list[ProcessingJourney] = []
        self._initialized_at: Optional[datetime] = None

    async def awaken(self) -> None:
        """
        Tapinagi Uyandir
        Tum katmanlari hazirlayip Temple moduna gec
        """
        print("\n" + "=" * 60)
        print("   TAPINAK KAPILARI ACILIYOR...")
        print("=" * 60)

        self.mode = StupaMode.AWAKENING

        print(f"\n   Mantra: {self.MANTRA}\n")

        # Her katmani baslat (simule)
        for layer_name, freq in self.FREQUENCIES.items():
            await asyncio.sleep(0.1)
            print(f"   [{layer_name}] Frekans ayarlandi: {freq}Hz")

        self.mode = StupaMode.TEMPLE
        self._initialized_at = datetime.now()

        print("\n   Tapinak Modu: AKTIF")
        print("=" * 60 + "\n")

    async def enter_nirvana(self) -> None:
        """Nirvana moduna gec - Maksimum islem gucu"""
        if self.mode != StupaMode.TEMPLE:
            await self.awaken()

        self.mode = StupaMode.NIRVANA
        print("   NIRVANA MODU AKTIF - Maksimum guc")

    def _create_journey(self, input_data: Any) -> ProcessingJourney:
        """Yeni yolculuk olustur"""
        journey = ProcessingJourney(
            journey_id=f"journey_{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            start_time=datetime.now(),
            input_data=input_data
        )
        self.journeys.append(journey)
        return journey

    async def prayer_wheel_spin(self, raw_data: Any) -> CazibeOutput:
        """
        DUA CARKI DONDURME
        Tam yolculuk: TOPRAK -> SU -> ATES -> HAVA -> ETER

        Orjinal Python kodundaki gibi basitlestirilmis versiyon.
        """
        print(f"   Tapinak Kapilari Aciliyor... Giren Ham Veri: '{str(raw_data)[:50]}...'")
        await asyncio.sleep(0.2)

        # 1. KATLA: TOPRAK
        print(f"   [TOPRAK] Glitch Lab veriyi Thamel pazarinda topladi...")
        raw_packet = await self.toprak.ingest_text(str(raw_data), "prayer_wheel")

        # 2. KATLA: SU
        purified = await self.su.purify(raw_packet)
        print(f"   [SU] Serpalar veriyi nehirde arindirdi")

        # 3. KATLA: ATES (3 rahip)
        print(f"   [ATES] N8N Dua Carklari donuyor... LLM Konseyi toplaniyor...")
        wisdom = await self.ates.forge(purified, intensity=3)

        # 4. KATLA: HAVA
        print(f"   [HAVA] Legend Layer veriyi ruzgar bayraklarina yazdi.")
        transmission = await self.hava.transmit(wisdom, flag_count=3)

        # 5. YUKSEL: ETER
        print(f"   [ETER] CAZIBE.IO Zirvesi: Sessizlik ve Cekim.")
        cazibe = await self.eter.crystallize(transmission)

        return cazibe

    async def process(
        self,
        data: Any,
        source_name: str = "input",
        intensity: int = 5
    ) -> CazibeOutput:
        """
        Tam Islem Dongusu

        Veriyi tum katmanlardan gecirip Cazibe ciktisi uret.

        Args:
            data: Ham veri (str, dict, veya dosya yolu)
            source_name: Kaynak adi
            intensity: Ates katmani yogunlugu (1-7 arasi LLM)

        Returns:
            CazibeOutput: Saf Cazibe ciktisi
        """
        if self.mode == StupaMode.DORMANT:
            await self.awaken()

        journey = self._create_journey(data)

        try:
            # === TOPRAK ===
            print(f"\n   [1/5] TOPRAK: Kaotik toplama basliyor...")
            if isinstance(data, (str, Path)) and Path(str(data)).exists():
                raw_packet = await self.toprak.ingest_file(Path(data))
            elif isinstance(data, dict):
                raw_packet = await self.toprak.ingest_json(data, source_name)
            else:
                raw_packet = await self.toprak.ingest_text(str(data), source_name)

            journey.raw_packets.append(raw_packet)
            journey.layer_stats["toprak"] = self.toprak.get_chaos_stats()

            # === SU ===
            print(f"   [2/5] SU: Arinma akisi basliyor...")
            purified = await self.su.purify(raw_packet, PurificationLevel.CRYSTALLINE)
            journey.purified_packets.append(purified)
            journey.layer_stats["su"] = self.su.get_flow_stats()

            # === ATES ===
            print(f"   [3/5] ATES: Simya dovumu basliyor ({intensity} rahip)...")
            wisdom = await self.ates.forge(purified, intensity=intensity)
            journey.forged_wisdoms.append(wisdom)
            journey.layer_stats["ates"] = self.ates.get_forge_stats()

            # === HAVA ===
            print(f"   [4/5] HAVA: Ruzgar iletimi basliyor...")
            transmission = await self.hava.transmit(wisdom, flag_count=3)
            journey.transmissions.append(transmission)
            journey.layer_stats["hava"] = self.hava.get_wind_stats()

            # === ETER ===
            print(f"   [5/5] ETER: Kristallestirme basliyor...")
            cazibe = await self.eter.crystallize(transmission)
            journey.cazibe_outputs.append(cazibe)
            journey.layer_stats["eter"] = self.eter.get_apex_stats()

            journey.complete()

            print(f"\n   Yolculuk tamamlandi: {journey.total_duration_ms:.2f}ms")

            return cazibe

        except Exception as e:
            journey.complete()
            raise RuntimeError(f"Stupa islemi basarisiz: {e}") from e

    async def process_batch(
        self,
        data_items: list[Any],
        intensity: int = 3
    ) -> list[CazibeOutput]:
        """
        Toplu Islem

        Birden fazla veriyi paralel isle.
        """
        if self.mode == StupaMode.DORMANT:
            await self.awaken()

        print(f"\n   Toplu islem: {len(data_items)} oge")

        # Toprak - Toplama
        raw_packets = []
        for i, item in enumerate(data_items):
            packet = await self.toprak.ingest_text(str(item), f"batch_{i}")
            raw_packets.append(packet)

        # Su - Arinma (paralel)
        purified = await self.su.purify_batch(raw_packets)

        # Ates - Dovum (paralel)
        wisdoms = await self.ates.forge_batch(purified, intensity)

        # Hava - Iletim (paralel)
        transmissions = await self.hava.transmit_batch(wisdoms)

        # Eter - Kristallestirme (paralel)
        outputs = await self.eter.crystallize_batch(transmissions)

        return outputs

    def get_stupa_stats(self) -> dict:
        """Tapinak istatistikleri"""
        return {
            "mode": self.mode.value,
            "mantra": self.MANTRA,
            "frequencies": self.FREQUENCIES,
            "initialized_at": self._initialized_at.isoformat() if self._initialized_at else None,
            "total_journeys": len(self.journeys),
            "layers": {
                "toprak": self.toprak.get_chaos_stats(),
                "su": self.su.get_flow_stats(),
                "ates": self.ates.get_forge_stats(),
                "hava": self.hava.get_wind_stats(),
                "eter": self.eter.get_apex_stats()
            }
        }

    def __repr__(self):
        return f"<DataStupa mode={self.mode.value}, journeys={len(self.journeys)}>"


# ============================================================
# ANA RITUEL - Butun katmanlarin senkronize calismasi
# ============================================================

async def full_ritual(raw_data: str) -> CazibeOutput:
    """
    TAM RITUEL
    Bastan sona veri donusumu

    Kullanim:
        result = await full_ritual("1984-2024_Sanayi_Verileri.pdf")
        print(result.to_parchment())
    """
    stupa = DataStupa()
    await stupa.awaken()

    print("\n" + "=" * 60)
    print("   KATMANDU RITUELI BASLIYOR")
    print("=" * 60)

    result = await stupa.process(raw_data, intensity=5)

    print("\n" + result.to_parchment())

    stats = stupa.get_stupa_stats()
    print(f"\n   Toplam islem: {stats['total_journeys']} yolculuk")

    return result


# ============================================================
# CLI DEMO
# ============================================================

if __name__ == "__main__":
    import sys

    async def demo():
        """Demo calistirici"""
        data = sys.argv[1] if len(sys.argv) > 1 else "1984-2024_Sanayi_Verileri.pdf"

        print("\n" + "#" * 60)
        print("   KATMANDU ENGINE v1.0")
        print("   'Om Mani Padme Hum' for Data Processing")
        print("#" * 60)

        result = await full_ritual(data)

        print("\n   SONUC:")
        print(f"   Cazibe ID: {result.cazibe_id}")
        print(f"   Frekans: {result.frequency_hz}Hz")
        print(f"   Hizalanma: {result.alignment_level.name}")
        print(f"   Buda Potansiyeli: %{result.sector_buddha_potential*100:.1f}")

    asyncio.run(demo())
