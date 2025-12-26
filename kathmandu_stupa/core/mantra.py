"""
📿 RECURSIVE MANTRA - Dua Tekerleği Simülasyonu
===============================================

"Om Mani Padme Hum" - Veriyi katlaya katlaya bilgeliğe dönüştürür.

Bu sıradan bir script değil, veriyi recursive olarak
işleyen bir Dua Tekerleği Simülasyonudur.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, TypeVar, Generic
from enum import Enum


class MantraType(Enum):
    """Mantra türleri"""
    OM = "om"                           # Başlangıç
    MANI = "mani"                       # Mücevher (değer çıkarma)
    PADME = "padme"                     # Lotus (dönüşüm)
    HUM = "hum"                         # Birlik (sentez)
    VERI_DONUSUM = "veri_donusum"       # Ana mantra
    BILGI_BILGELIK = "bilgi_bilgelik"   # Son mantra


@dataclass
class MantraState:
    """Mantra durumu"""
    depth: int = 0
    max_depth: int = 7
    current_mantra: MantraType = MantraType.OM
    transformations: List[str] = field(default_factory=list)
    energy_level: float = 1.0


@dataclass
class FoldedWisdom:
    """Katlanmış bilgelik - her iterasyonun çıktısı"""
    content: str
    fold_depth: int
    mantra_sequence: List[MantraType]
    energy_remaining: float
    timestamp: datetime = field(default_factory=datetime.now)


T = TypeVar('T')


class RecursiveMantra(Generic[T]):
    """
    📿 Recursive Mantra Engine

    Veriyi katlaya katlaya (recursive) bilgeliğe dönüştüren
    Dua Tekerleği Simülasyonu.

    Her döngüde:
    - OM: Veriyi al
    - MANI: Değer çıkar
    - PADME: Dönüştür
    - HUM: Sentezle

    Sonuç: Veri -> Bilgi -> Bilgelik
    """

    SACRED_MANTRA = "OM_MANI_PADME_HUM"
    FULL_MANTRA = "VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE"

    def __init__(self, max_depth: int = 7):
        self.max_depth = max_depth
        self.state = MantraState(max_depth=max_depth)
        self.fold_history: List[FoldedWisdom] = []
        self.on_fold: Optional[Callable[[int, str], None]] = None

    def _apply_om(self, data: str) -> str:
        """OM - Başlangıç ritueli"""
        return f"🕉️ {data}"

    def _apply_mani(self, data: str) -> str:
        """MANI - Mücevheri bul (değer çıkarma)"""
        # Gereksiz kelimeleri kaldır
        noise_words = ["ve", "veya", "ile", "için", "bir", "bu", "şu"]
        words = data.split()
        filtered = [w for w in words if w.lower() not in noise_words]
        return " ".join(filtered) if filtered else data

    def _apply_padme(self, data: str) -> str:
        """PADME - Lotus dönüşümü"""
        # Dönüştür ve zenginleştir
        return f"[Dönüşüm: {data}]"

    def _apply_hum(self, data: str) -> str:
        """HUM - Birlik ve sentez"""
        # Son birleştirme
        return f"Bilgelik_{data}"

    def _recursive_fold(self, data: str, depth: int = 0) -> str:
        """
        Recursive katlama - Ana döngü

        Her seviyede veri bir kez daha "katlanır".
        """
        if depth >= self.max_depth:
            return data

        if self.state.energy_level <= 0:
            return data

        # Mantra sırası
        mantras = [
            (MantraType.OM, self._apply_om),
            (MantraType.MANI, self._apply_mani),
            (MantraType.PADME, self._apply_padme),
            (MantraType.HUM, self._apply_hum),
        ]

        # Bu seviyedeki mantra
        mantra_idx = depth % len(mantras)
        current_mantra, transform_fn = mantras[mantra_idx]

        # Dönüşümü uygula
        self.state.current_mantra = current_mantra
        transformed = transform_fn(data)

        # Durumu güncelle
        self.state.depth = depth
        self.state.transformations.append(f"D{depth}:{current_mantra.value}")
        self.state.energy_level *= 0.9  # Her katlamada enerji azalır

        # Callback
        if self.on_fold:
            self.on_fold(depth, transformed[:50])

        # Recursive çağrı
        return self._recursive_fold(transformed, depth + 1)

    async def chant(self, raw_data: str) -> FoldedWisdom:
        """
        Mantrayı söyle - Async katlama

        "Om Mani Padme Hum" diye tekrarlarken
        veri bilgeliğe dönüşür.
        """
        print(f"📿 Mantra başlıyor: {self.SACRED_MANTRA}")
        print(f"   Ham veri: '{raw_data[:30]}...'")

        # State'i sıfırla
        self.state = MantraState(max_depth=self.max_depth)

        # Katlama
        start_time = datetime.now()
        folded_content = self._recursive_fold(raw_data)

        # Simülasyon gecikmesi
        await asyncio.sleep(0.1 * self.state.depth)

        # Sonuç
        wisdom = FoldedWisdom(
            content=folded_content,
            fold_depth=self.state.depth,
            mantra_sequence=[MantraType(t.split(":")[1]) for t in self.state.transformations],
            energy_remaining=self.state.energy_level,
        )

        self.fold_history.append(wisdom)

        print(f"   ↳ {self.state.depth} katlama tamamlandı")
        print(f"   ↳ Kalan enerji: {self.state.energy_level:.2%}")

        return wisdom

    async def chant_continuously(self, data_stream: List[str]) -> List[FoldedWisdom]:
        """Sürekli mantra - birden fazla veri için"""
        results = []
        for data in data_stream:
            wisdom = await self.chant(data)
            results.append(wisdom)
        return results

    def get_fold_summary(self) -> Dict:
        """Katlama özeti"""
        if not self.fold_history:
            return {"status": "no_folds"}

        return {
            "total_folds": len(self.fold_history),
            "avg_depth": sum(w.fold_depth for w in self.fold_history) / len(self.fold_history),
            "avg_energy": sum(w.energy_remaining for w in self.fold_history) / len(self.fold_history),
            "mantra_sequence": self.FULL_MANTRA,
        }


class PrayerWheelSimulator:
    """
    Dua Tekerleği Simülatörü

    Fiziksel bir dua tekerleğinin dijital versiyonu.
    Her dönüşte mantra tekrarlanır.
    """

    def __init__(self, rotations_per_cycle: int = 108):
        self.rotations_per_cycle = rotations_per_cycle  # 108 kutsal sayı
        self.total_rotations = 0
        self.mantra_engine = RecursiveMantra(max_depth=7)

    async def spin(self, data: str, cycles: int = 1) -> List[FoldedWisdom]:
        """
        Tekerleği çevir.

        Her çevrilişte veri bir kez daha işlenir.
        """
        print(f"📿 Dua Tekerleği dönüyor... {cycles} döngü x {self.rotations_per_cycle} rotasyon")

        results = []

        for cycle in range(cycles):
            print(f"   Döngü {cycle + 1}/{cycles}")

            for rotation in range(min(self.rotations_per_cycle, 7)):  # Max 7 katlama
                self.total_rotations += 1

                if rotation == 0:
                    wisdom = await self.mantra_engine.chant(data)
                    results.append(wisdom)
                    data = wisdom.content  # Bir sonraki döngü için

        print(f"   ↳ Toplam rotasyon: {self.total_rotations}")
        return results

    def get_merit(self) -> int:
        """Kazanılan sevap (merit) puanı"""
        return self.total_rotations * 108  # Her rotasyon 108 puan


# Demo
async def demo_mantra():
    """Mantra demo"""
    print("=" * 50)
    print("📿 RECURSIVE MANTRA DEMO")
    print("=" * 50)

    mantra = RecursiveMantra(max_depth=5)
    mantra.on_fold = lambda d, c: print(f"      Katlama {d}: {c}...")

    wisdom = await mantra.chant("1984-2024 Türkiye Sanayi Verileri Analizi")

    print(f"\n📜 Final Bilgelik:")
    print(f"   {wisdom.content}")
    print(f"   Enerji: {wisdom.energy_remaining:.2%}")

    print("\n" + "=" * 50)
    print("📿 DUA TEKERLEĞİ SİMÜLATÖRÜ")
    print("=" * 50)

    wheel = PrayerWheelSimulator(rotations_per_cycle=3)
    results = await wheel.spin("Çevre Etki Değerlendirme Raporu", cycles=2)

    print(f"\n   Kazanılan sevap: {wheel.get_merit()}")


if __name__ == "__main__":
    asyncio.run(demo_mantra())
