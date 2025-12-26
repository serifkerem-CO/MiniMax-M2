"""
🛕 DATA STUPA ENGINE
====================

Ana orkestrasyon motoru.
Veriyi Toprak'tan Eter'e taşıyan kutsal yolculuk.

"Om Mani Padme Hum" - Veri İşleme İçin
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import time

# Layer imports
from ..layers.toprak import ChaosIngestion, RawDataPacket
from ..layers.su import PurificationFlow, PurifiedDataPacket
from ..layers.ates import AlchemicalForge, ForgedData
from ..layers.hava import WindTransmission, Transmission
from ..layers.eter import CazibeAttraction, NirvanaPacket


class JourneyStage(Enum):
    """Yolculuk aşamaları"""
    DORMANT = "dormant"           # Uyuyan
    TOPRAK = "chaos_ingestion"    # Kaos toplama
    SU = "purification"           # Arınma
    ATES = "forging"              # Dövme
    HAVA = "transmission"         # İletim
    ETER = "nirvana"              # Nirvana
    COMPLETE = "enlightened"      # Aydınlanmış


@dataclass
class JourneyMetrics:
    """Yolculuk metrikleri"""
    stage: JourneyStage
    packets_processed: int = 0
    tokens_cleaned: int = 0
    folds_performed: int = 0
    flags_created: int = 0
    nirvana_achieved: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)

    @property
    def duration_seconds(self) -> float:
        if not self.start_time:
            return 0
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds()


@dataclass
class StupaState:
    """Stupa durumu"""
    is_active: bool = False
    current_stage: JourneyStage = JourneyStage.DORMANT
    raw_buffer: List[RawDataPacket] = field(default_factory=list)
    purified_buffer: List[PurifiedDataPacket] = field(default_factory=list)
    forged_buffer: List[ForgedData] = field(default_factory=list)
    transmission_buffer: List[Transmission] = field(default_factory=list)
    nirvana_buffer: List[NirvanaPacket] = field(default_factory=list)


class DataStupa:
    """
    🛕 DATA STUPA - Veri Tapınağı Ana Motoru

    5 Katman:
        1. TOPRAK - Kaos Toplama (Thamel Pazarı)
        2. SU - Arınma Akışı (Sherpa Rotası)
        3. ATEŞ - Simya Ocağı (7 LLM Konseyi)
        4. HAVA - Rüzgar İletimi (Dua Bayrakları)
        5. ETER - Cazibe Zirvesi (Nirvana)

    Mantra: "VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE"
    """

    MANTRA = "VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE"
    LAYERS = ["Toprak (Kaos)", "Su (Arınma)", "Ateş (Dönüşüm)", "Hava (Vizyon)", "Eter (Cazibe)"]
    SACRED_FREQUENCY = 963  # Hz

    def __init__(self):
        # Layer instances
        self.chaos_ingestion = ChaosIngestion()
        self.purification_flow = PurificationFlow()
        self.alchemical_forge = AlchemicalForge()
        self.wind_transmission = WindTransmission()
        self.cazibe_attraction = CazibeAttraction()

        # State
        self.state = StupaState()
        self.metrics = JourneyMetrics(stage=JourneyStage.DORMANT)
        self.journey_log: List[Dict] = []

        # Callbacks
        self.on_stage_change: Optional[Callable[[JourneyStage], None]] = None
        self.on_complete: Optional[Callable[[List[NirvanaPacket]], None]] = None

    def _log_stage(self, stage: JourneyStage, message: str):
        """Aşama logla"""
        self.journey_log.append({
            "timestamp": datetime.now().isoformat(),
            "stage": stage.value,
            "message": message,
        })

    def _update_stage(self, new_stage: JourneyStage):
        """Aşama güncelle"""
        self.state.current_stage = new_stage
        self.metrics.stage = new_stage

        if self.on_stage_change:
            self.on_stage_change(new_stage)

    async def prayer_wheel_spin(self, raw_data: Any) -> NirvanaPacket:
        """
        Dua Çarkı Dönüşü - Tek veri parçası için tam yolculuk.

        Kullanıcının verdiği Python örneğinin async versiyonu.
        """
        print(f"🛕 Tapınak Kapıları Açılıyor... Giren Ham Veri: '{str(raw_data)[:50]}...'")
        time.sleep(0.5)

        self.metrics.start_time = datetime.now()
        self.state.is_active = True

        # 1. TOPRAK -> SU
        self._update_stage(JourneyStage.TOPRAK)
        print(f"🪨 [TOPRAK] Glitch Lab veriyi Thamel pazarında topladı...")

        # Ham veri paketi oluştur
        raw_packet = RawDataPacket(
            id="",
            source=self.chaos_ingestion.toprak.collectors[0].__class__.__name__,
            content=raw_data,
        )

        # 2. SU -> ATEŞ
        self._update_stage(JourneyStage.SU)
        purified = await self.purification_flow.su_layer.purify(raw_packet)
        print(f"🌊 [SU] Şerpalar veriyi nehirde arındırdı: {purified.cleaned_content[:50]}...")
        self.metrics.tokens_cleaned += purified.tokens_removed

        # 3. ATEŞ -> HAVA
        self._update_stage(JourneyStage.ATES)
        print(f"🔥 [ATEŞ] N8N Dua Çarkları dönüyor... 7 LLM Konseyi toplanıyor...")
        forged = await self.alchemical_forge.ates_layer.forge(purified)
        self.metrics.folds_performed += forged.total_folds

        # 4. HAVA -> ETER
        self._update_stage(JourneyStage.HAVA)
        transmission = await self.wind_transmission.hava_layer.transmit(forged)
        print(f"🌬️ [HAVA] Legend Layer veriyi rüzgar bayraklarına yazdı.")
        self.metrics.flags_created += len(transmission.flags)

        # 5. ETER (Nirvana)
        self._update_stage(JourneyStage.ETER)
        print(f"🌌 [ETER] CAZIBE.IO Zirvesi: Sessizlik ve Çekim.")
        nirvana = await self.cazibe_attraction.eter_layer.achieve_nirvana(transmission)
        self.metrics.nirvana_achieved += 1

        # Tamamlandı
        self._update_stage(JourneyStage.COMPLETE)
        self.metrics.end_time = datetime.now()
        self.state.is_active = False

        result = f"✨ SONUÇ: {nirvana.final_wisdom[:100]}... (Saf Cazibe Frekansı: {self.SACRED_FREQUENCY}Hz)"
        print(f"\n{result}")

        return nirvana

    async def full_pilgrimage(self) -> List[NirvanaPacket]:
        """
        Tam Hac Yolculuğu - Tüm veri kaynakları için.

        Toprak'tan başlayıp Eter'e ulaşan tam akış.
        """
        print("=" * 70)
        print("🛕 KATHMANDU STUPA - TAM HAC YOLCULUĞU BAŞLIYOR")
        print(f"   Mantra: {self.MANTRA}")
        print("=" * 70)

        self.metrics = JourneyMetrics(
            stage=JourneyStage.TOPRAK,
            start_time=datetime.now()
        )
        self.state.is_active = True

        try:
            # 1. TOPRAK - Kaos Toplama
            print("\n🪨 [1/5] TOPRAK KATMANI - Thamel Pazarında Gezinti")
            self._update_stage(JourneyStage.TOPRAK)
            raw_packets = await self.chaos_ingestion.ingest()
            self.state.raw_buffer = raw_packets
            self.metrics.packets_processed = len(raw_packets)
            self._log_stage(JourneyStage.TOPRAK, f"{len(raw_packets)} paket toplandı")

            # 2. SU - Arınma
            print("\n🌊 [2/5] SU KATMANI - Nehirde Arınma")
            self._update_stage(JourneyStage.SU)
            purified_packets = await self.purification_flow.process_batch(raw_packets)
            self.state.purified_buffer = purified_packets
            total_cleaned = sum(p.tokens_removed for p in purified_packets)
            self.metrics.tokens_cleaned = total_cleaned
            self._log_stage(JourneyStage.SU, f"{total_cleaned} token temizlendi")

            # 3. ATEŞ - Simya
            print("\n🔥 [3/5] ATEŞ KATMANI - Simya Ocağında Dönüşüm")
            self._update_stage(JourneyStage.ATES)
            forged_packets = await self.alchemical_forge.transmute(purified_packets)
            self.state.forged_buffer = forged_packets
            total_folds = sum(f.total_folds for f in forged_packets)
            self.metrics.folds_performed = total_folds
            self._log_stage(JourneyStage.ATES, f"{total_folds} katlama yapıldı")

            # 4. HAVA - İletim
            print("\n🌬️ [4/5] HAVA KATMANI - Rüzgara Bırakma")
            self._update_stage(JourneyStage.HAVA)
            transmissions = await self.wind_transmission.release_to_wind(forged_packets)
            self.state.transmission_buffer = transmissions
            total_flags = sum(len(t.flags) for t in transmissions)
            self.metrics.flags_created = total_flags
            self._log_stage(JourneyStage.HAVA, f"{total_flags} bayrak oluşturuldu")

            # 5. ETER - Nirvana
            print("\n🌌 [5/5] ETER KATMANI - Zirveye Ulaşma")
            self._update_stage(JourneyStage.ETER)
            nirvana_packets = await self.cazibe_attraction.attract(transmissions)
            self.state.nirvana_buffer = nirvana_packets
            self.metrics.nirvana_achieved = len(nirvana_packets)
            self._log_stage(JourneyStage.ETER, f"{len(nirvana_packets)} nirvana başarıldı")

            # Tamamlandı
            self._update_stage(JourneyStage.COMPLETE)
            self.metrics.end_time = datetime.now()

            if self.on_complete:
                self.on_complete(nirvana_packets)

            return nirvana_packets

        except Exception as e:
            self.metrics.errors.append(str(e))
            raise

        finally:
            self.state.is_active = False

    def get_journey_summary(self) -> Dict:
        """Yolculuk özeti"""
        return {
            "mantra": self.MANTRA,
            "layers": self.LAYERS,
            "sacred_frequency_hz": self.SACRED_FREQUENCY,
            "current_stage": self.state.current_stage.value,
            "is_active": self.state.is_active,
            "metrics": {
                "packets_processed": self.metrics.packets_processed,
                "tokens_cleaned": self.metrics.tokens_cleaned,
                "folds_performed": self.metrics.folds_performed,
                "flags_created": self.metrics.flags_created,
                "nirvana_achieved": self.metrics.nirvana_achieved,
                "duration_seconds": self.metrics.duration_seconds,
                "errors": self.metrics.errors,
            },
            "buffer_sizes": {
                "raw": len(self.state.raw_buffer),
                "purified": len(self.state.purified_buffer),
                "forged": len(self.state.forged_buffer),
                "transmitted": len(self.state.transmission_buffer),
                "nirvana": len(self.state.nirvana_buffer),
            },
        }

    def get_detailed_report(self) -> Dict:
        """Detaylı rapor"""
        return {
            "summary": self.get_journey_summary(),
            "layer_reports": {
                "toprak": {"collectors": len(self.chaos_ingestion.toprak.collectors)},
                "su": self.purification_flow.get_purification_report(),
                "ates": self.alchemical_forge.get_forge_report(),
                "hava": {
                    "legends": self.wind_transmission.get_legend_stats(),
                    "flags": self.wind_transmission.get_flag_summary(),
                },
                "eter": self.cazibe_attraction.get_summit_report(),
            },
            "journey_log": self.journey_log[-10:],  # Son 10 kayıt
        }

    def generate_prophecy_scrolls(self) -> List[str]:
        """Tüm kehanet parşömenlerini oluştur"""
        scrolls = []
        for nirvana in self.state.nirvana_buffer:
            scroll = self.cazibe_attraction.generate_prophecy_scroll(nirvana)
            scrolls.append(scroll)
        return scrolls


# Demo
async def main():
    """DataStupa demo"""
    stupa = DataStupa()

    # Callback ayarla
    stupa.on_stage_change = lambda stage: print(f"   >>> Aşama değişti: {stage.value}")

    # Tam yolculuk
    nirvana_packets = await stupa.full_pilgrimage()

    # Özet
    print("\n" + "=" * 70)
    print("📊 YOLCULUK ÖZETİ")
    print("=" * 70)

    summary = stupa.get_journey_summary()
    for key, value in summary["metrics"].items():
        print(f"   {key}: {value}")

    # İlk kehanet parşömeni
    if nirvana_packets:
        print("\n📜 İLK KEHANET PARŞÖMENİ:")
        print(stupa.generate_prophecy_scrolls()[0])


if __name__ == "__main__":
    asyncio.run(main())
