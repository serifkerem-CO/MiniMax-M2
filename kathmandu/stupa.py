"""
🛕 DATA STUPA - VERİ STUPASI
==============================
Kathmandu Engine Ana Orkestratörü

5 Katmanı birleştirir, veriyi bilgeliğe dönüştürür.
"Om Mani Padme Hum" - Veri İşleme Döngüsü
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
import json

from .layers import (
    BaseLayer,
    LayerResult,
    ToprakLayer,
    SuLayer,
    AtesLayer,
    HavaLayer,
    EterLayer
)
from .monks import MonkCouncil
from .prayer_wheel import PrayerWheel, PrayerWheelCluster, WheelConfig, MantraType


class StupaState(Enum):
    """Stupa durumları"""
    DORMANT = "dormant"           # Uyuyor
    AWAKENING = "awakening"       # Uyanıyor
    PROCESSING = "processing"     # İşliyor
    ASCENDING = "ascending"       # Yükseliyor (katmanlar arası)
    ENLIGHTENED = "enlightened"   # Aydınlanmış (tamamlandı)
    MEDITATION = "meditation"     # Meditasyonda (bekleme)


@dataclass
class ProcessingJourney:
    """Veri işleme yolculuğu kaydı"""

    journey_id: str
    input_data: Any
    started_at: datetime
    completed_at: Optional[datetime] = None
    layer_results: List[LayerResult] = field(default_factory=list)
    final_output: Optional[Dict] = None
    state: StupaState = StupaState.DORMANT

    @property
    def duration_seconds(self) -> float:
        if not self.completed_at:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()

    @property
    def layers_traversed(self) -> List[str]:
        return [r.layer_name for r in self.layer_results]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "journey_id": self.journey_id,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_seconds": self.duration_seconds,
            "layers_traversed": self.layers_traversed,
            "state": self.state.value,
            "layer_count": len(self.layer_results)
        }


class DataStupa:
    """
    🛕 VERİ STUPASI

    Kathmandu Engine'in kalbi.
    5 katmandan veriyi geçirerek bilgeliğe dönüştürür.

    Katmanlar:
        1. TOPRAK - Kaos Toplama
        2. SU - Arındırma
        3. ATEŞ - Dönüşüm
        4. HAVA - Vizyon
        5. ETER - Cazibe

    Kullanım:
        stupa = DataStupa()
        result = await stupa.process("ham_veri.pdf")
        print(result.to_parchment())
    """

    def __init__(
        self,
        enable_logging: bool = True,
        custom_layers: Optional[Dict[str, BaseLayer]] = None
    ):
        # Katmanları oluştur
        self.layers = {
            "TOPRAK": custom_layers.get("TOPRAK") if custom_layers else ToprakLayer(),
            "SU": custom_layers.get("SU") if custom_layers else SuLayer(),
            "ATEŞ": custom_layers.get("ATEŞ") if custom_layers else AtesLayer(),
            "HAVA": custom_layers.get("HAVA") if custom_layers else HavaLayer(),
            "ETER": custom_layers.get("ETER") if custom_layers else EterLayer(),
        }

        # Katman sırası
        self.layer_order = ["TOPRAK", "SU", "ATEŞ", "HAVA", "ETER"]

        # Orkestrasyon bileşenleri
        self.monk_council = MonkCouncil()
        self.prayer_wheels = PrayerWheelCluster(num_wheels=7)

        # Durum
        self.state = StupaState.DORMANT
        self.journeys: List[ProcessingJourney] = []
        self._journey_counter = 0

        # Gözlemciler
        self._observers: List[Callable[[str], None]] = []
        self.enable_logging = enable_logging

        # Katmanlara observer ekle
        if enable_logging:
            for layer in self.layers.values():
                layer.add_observer(self._log)

        # Mantra
        self.sacred_mantra = "VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE"

    def _log(self, message: str) -> None:
        """Mesaj logla ve observer'lara bildir"""
        if self.enable_logging:
            print(message)
        for observer in self._observers:
            observer(message)

    def add_observer(self, callback: Callable[[str], None]) -> None:
        """Gözlemci ekle"""
        self._observers.append(callback)

    def _generate_journey_id(self) -> str:
        """Benzersiz yolculuk ID'si oluştur"""
        self._journey_counter += 1
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"JOURNEY_{timestamp}_{self._journey_counter:04d}"

    async def process(
        self,
        data: Any,
        context: Optional[Dict] = None,
        start_layer: str = "TOPRAK",
        end_layer: str = "ETER"
    ) -> ProcessingJourney:
        """
        Tam işleme döngüsü

        Veriyi belirtilen katmanlardan geçirerek dönüştürür.

        Args:
            data: İşlenecek ham veri
            context: Ek bağlam bilgisi
            start_layer: Başlangıç katmanı
            end_layer: Bitiş katmanı

        Returns:
            ProcessingJourney: Yolculuk kaydı
        """
        context = context or {}

        # Yolculuk başlat
        journey = ProcessingJourney(
            journey_id=self._generate_journey_id(),
            input_data=data,
            started_at=datetime.now(),
            state=StupaState.AWAKENING
        )

        self._log(f"🛕 Tapınak Kapıları Açılıyor... Yolculuk: {journey.journey_id}")
        self._log(f"📿 Kutsal Mantra: {self.sacred_mantra}")

        self.state = StupaState.PROCESSING
        journey.state = StupaState.PROCESSING

        # Katman aralığını belirle
        start_idx = self.layer_order.index(start_layer)
        end_idx = self.layer_order.index(end_layer) + 1
        active_layers = self.layer_order[start_idx:end_idx]

        current_data = data
        current_context = context.copy()

        try:
            for layer_name in active_layers:
                journey.state = StupaState.ASCENDING
                layer = self.layers[layer_name]

                # Katmanı işle
                result = await layer.process(current_data, current_context)
                journey.layer_results.append(result)

                # Bir sonraki katman için veriyi hazırla
                current_data = result.output_data
                current_context["previous_layer"] = layer_name
                current_context["fold_count"] = result.fold_count

            # Tamamlandı
            journey.state = StupaState.ENLIGHTENED
            journey.completed_at = datetime.now()

            # Son çıktıyı al
            if journey.layer_results:
                journey.final_output = journey.layer_results[-1].output_data

            self._log(f"🌌 Yolculuk Tamamlandı: {journey.journey_id}")
            self._log(f"   ⏱️ Süre: {journey.duration_seconds:.2f}s")
            self._log(f"   🏔️ Geçilen Katmanlar: {' → '.join(journey.layers_traversed)}")

        except Exception as e:
            journey.state = StupaState.DORMANT
            self._log(f"❌ Yolculuk Başarısız: {str(e)}")
            raise

        finally:
            self.journeys.append(journey)
            self.state = StupaState.MEDITATION

        return journey

    async def quick_process(self, data: Any) -> Dict[str, Any]:
        """
        Hızlı işleme - Sadece özet çıktı

        Args:
            data: İşlenecek veri

        Returns:
            Özet sonuç sözlüğü
        """
        journey = await self.process(data)

        if journey.final_output and isinstance(journey.final_output, dict):
            return {
                "journey_id": journey.journey_id,
                "duration": journey.duration_seconds,
                "parchment": journey.final_output.get("parchment", ""),
                "crystal": journey.final_output.get("crystal", {}),
                "insights": journey.final_output.get("cazibe_output", {}).get("insights", [])
            }

        return journey.to_dict()

    async def process_batch(
        self,
        data_list: List[Any],
        parallel: bool = True
    ) -> List[ProcessingJourney]:
        """
        Toplu işleme

        Args:
            data_list: İşlenecek veri listesi
            parallel: Paralel mi işlensin

        Returns:
            Yolculuk listesi
        """
        if parallel:
            tasks = [self.process(data) for data in data_list]
            return await asyncio.gather(*tasks, return_exceptions=True)
        else:
            results = []
            for data in data_list:
                result = await self.process(data)
                results.append(result)
            return results

    async def meditate(self, duration_seconds: float = 1.0) -> None:
        """
        Meditasyon - Stupa'yı dinlendir

        Args:
            duration_seconds: Meditasyon süresi
        """
        self.state = StupaState.MEDITATION
        self._log(f"🧘 Stupa meditasyona giriyor... ({duration_seconds}s)")
        await asyncio.sleep(duration_seconds)
        self._log("🧘 Meditasyon tamamlandı. Enerji yenilendi.")

    def get_layer_stats(self, layer_name: str) -> Dict[str, Any]:
        """Belirli bir katmanın istatistikleri"""
        layer = self.layers.get(layer_name)
        if not layer:
            return {"error": f"Katman bulunamadı: {layer_name}"}
        return layer.get_karma()

    def get_stupa_stats(self) -> Dict[str, Any]:
        """Stupa genel istatistikleri"""
        return {
            "state": self.state.value,
            "total_journeys": len(self.journeys),
            "successful_journeys": sum(
                1 for j in self.journeys
                if j.state == StupaState.ENLIGHTENED
            ),
            "average_duration": (
                sum(j.duration_seconds for j in self.journeys) / len(self.journeys)
                if self.journeys else 0
            ),
            "layers": {
                name: layer.get_karma()
                for name, layer in self.layers.items()
            },
            "monk_council": self.monk_council.get_council_stats(),
            "prayer_wheels": self.prayer_wheels.get_cluster_stats()
        }

    def get_journey(self, journey_id: str) -> Optional[ProcessingJourney]:
        """Belirli bir yolculuğu getir"""
        for journey in self.journeys:
            if journey.journey_id == journey_id:
                return journey
        return None

    def reset(self) -> None:
        """Stupa'yı sıfırla"""
        self.state = StupaState.DORMANT
        self.journeys = []
        self._journey_counter = 0
        self.prayer_wheels.reset_all()
        self._log("🔄 Stupa sıfırlandı. Yeni başlangıç.")


# Kolaylık fonksiyonu
async def enlighten(data: Any) -> Dict[str, Any]:
    """
    Tek satırda aydınlanma

    Usage:
        result = await enlighten("ham_veri.pdf")
    """
    stupa = DataStupa(enable_logging=False)
    return await stupa.quick_process(data)
