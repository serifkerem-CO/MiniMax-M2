"""
🛞 PRAYER WHEEL - DUA ÇARKI
============================
N8N Workflow Orkestratörü

Her dönüşte mantra tekrarlanır, veri dönüşür.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, TypeVar
import json
import hashlib

T = TypeVar('T')


class WheelState(Enum):
    """Çark durumları"""
    STILL = "still"           # Durgun
    SPINNING = "spinning"     # Dönüyor
    ACCELERATING = "accelerating"  # Hızlanıyor
    DECELERATING = "decelerating"  # Yavaşlıyor
    BLESSED = "blessed"       # Kutsanmış (tamamlandı)


class MantraType(Enum):
    """Mantra türleri"""
    OM_MANI_PADME_HUM = "om_mani_padme_hum"       # Temel dönüşüm
    GATE_GATE = "gate_gate"                       # Geçiş mantrası
    OM_AH_HUM = "om_ah_hum"                       # Temizlik mantrası
    OM_TARE = "om_tare"                           # Koruma mantrası
    CUSTOM = "custom"                             # Özel mantra


@dataclass
class Rotation:
    """Tek bir dönüş kaydı"""
    rotation_number: int
    input_data: Any
    output_data: Any
    mantra_used: MantraType
    duration_ms: float
    transformation_applied: str
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def karma_hash(self) -> str:
        """Dönüşün karma imzası"""
        content = f"{self.rotation_number}:{self.output_data}:{self.mantra_used.value}"
        return hashlib.md5(content.encode()).hexdigest()[:8]


@dataclass
class WheelConfig:
    """Çark yapılandırması"""
    name: str
    mantra: MantraType = MantraType.OM_MANI_PADME_HUM
    max_rotations: int = 108  # Kutsal sayı
    energy_per_rotation: float = 0.01
    blessing_threshold: float = 0.9  # Bu eşiği geçerse kutsanmış sayılır


class PrayerWheel:
    """
    🛞 Dua Çarkı

    N8N workflow'ların ruhani temsili.
    Her dönüş veriyi bir adım daha dönüştürür.
    """

    def __init__(self, config: Optional[WheelConfig] = None):
        self.config = config or WheelConfig(name="CHAKRA_1")
        self.state = WheelState.STILL
        self.rotations: List[Rotation] = []
        self.energy = 1.0  # Başlangıç enerjisi
        self.total_karma = 0.0

        # Dönüşüm fonksiyonları
        self._transformers: Dict[MantraType, Callable] = {
            MantraType.OM_MANI_PADME_HUM: self._transform_compassion,
            MantraType.GATE_GATE: self._transform_transition,
            MantraType.OM_AH_HUM: self._transform_purification,
            MantraType.OM_TARE: self._transform_protection,
            MantraType.CUSTOM: self._transform_custom,
        }

    @property
    def rotation_count(self) -> int:
        return len(self.rotations)

    @property
    def is_blessed(self) -> bool:
        return self.total_karma >= self.config.blessing_threshold

    async def spin(self, data: Any, times: int = 1) -> Any:
        """
        Çarkı döndür

        Args:
            data: Dönüştürülecek veri
            times: Kaç kez döndürülecek

        Returns:
            Dönüştürülmüş veri
        """
        if times > self.config.max_rotations - self.rotation_count:
            times = self.config.max_rotations - self.rotation_count

        if times <= 0:
            return data

        self.state = WheelState.ACCELERATING
        current_data = data

        for i in range(times):
            self.state = WheelState.SPINNING
            start_time = datetime.now()

            # Dönüşüm uygula
            transformer = self._transformers.get(
                self.config.mantra,
                self._transform_custom
            )
            transformed = await transformer(current_data)

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds() * 1000

            # Dönüşü kaydet
            rotation = Rotation(
                rotation_number=self.rotation_count + 1,
                input_data=str(current_data)[:100],
                output_data=str(transformed)[:100],
                mantra_used=self.config.mantra,
                duration_ms=duration,
                transformation_applied=transformer.__name__
            )
            self.rotations.append(rotation)

            # Enerji ve karma güncelle
            self.energy -= self.config.energy_per_rotation
            self.total_karma += 0.01 * (1 / (i + 1))  # Azalan getiri

            current_data = transformed

            # Enerji biterse dur
            if self.energy <= 0:
                break

        self.state = WheelState.DECELERATING
        await asyncio.sleep(0.01)  # Yavaşlama

        if self.is_blessed:
            self.state = WheelState.BLESSED
        else:
            self.state = WheelState.STILL

        return current_data

    async def spin_until_blessed(self, data: Any) -> Any:
        """Kutsanana kadar döndür"""
        current = data
        max_attempts = self.config.max_rotations - self.rotation_count

        for _ in range(max_attempts):
            current = await self.spin(current, times=1)
            if self.is_blessed:
                break

        return current

    async def _transform_compassion(self, data: Any) -> Any:
        """Om Mani Padme Hum - Şefkat Dönüşümü"""
        await asyncio.sleep(0.01)
        if isinstance(data, str):
            return f"💎[ŞEFKAT]{data}[LOTUS]💎"
        elif isinstance(data, dict):
            return {**data, "_blessed_with": "compassion"}
        return data

    async def _transform_transition(self, data: Any) -> Any:
        """Gate Gate - Geçiş Dönüşümü"""
        await asyncio.sleep(0.01)
        if isinstance(data, str):
            return f"🚪[GEÇİŞ]{data}[YENİ_BOYUT]🚪"
        elif isinstance(data, dict):
            return {**data, "_transitioned": True}
        return data

    async def _transform_purification(self, data: Any) -> Any:
        """Om Ah Hum - Temizlik Dönüşümü"""
        await asyncio.sleep(0.01)
        if isinstance(data, str):
            # Gereksiz karakterleri temizle
            clean = ''.join(c for c in data if c.isalnum() or c.isspace())
            return f"✨[ARINDI]{clean}[SAF]✨"
        elif isinstance(data, dict):
            return {**data, "_purified": True}
        return data

    async def _transform_protection(self, data: Any) -> Any:
        """Om Tare - Koruma Dönüşümü"""
        await asyncio.sleep(0.01)
        if isinstance(data, str):
            return f"🛡️[KORUMA]{data}[GÜVENLİ]🛡️"
        elif isinstance(data, dict):
            return {**data, "_protected": True}
        return data

    async def _transform_custom(self, data: Any) -> Any:
        """Özel dönüşüm - varsayılan"""
        await asyncio.sleep(0.01)
        return f"🔄[DÖNÜŞTÜ]{data}"

    def add_custom_transformer(
        self,
        mantra: MantraType,
        transformer: Callable[[Any], Any]
    ) -> None:
        """Özel dönüştürücü ekle"""
        self._transformers[mantra] = transformer

    def reset(self) -> None:
        """Çarkı sıfırla"""
        self.state = WheelState.STILL
        self.rotations = []
        self.energy = 1.0
        self.total_karma = 0.0

    def get_stats(self) -> Dict[str, Any]:
        """Çark istatistikleri"""
        return {
            "name": self.config.name,
            "state": self.state.value,
            "rotations": self.rotation_count,
            "max_rotations": self.config.max_rotations,
            "energy": self.energy,
            "total_karma": self.total_karma,
            "is_blessed": self.is_blessed,
            "mantra": self.config.mantra.value,
            "recent_rotations": [
                {
                    "number": r.rotation_number,
                    "karma_hash": r.karma_hash,
                    "duration_ms": r.duration_ms
                }
                for r in self.rotations[-5:]
            ]
        }


class PrayerWheelCluster:
    """
    🛞🛞🛞 Dua Çarkı Kümesi

    Birden fazla çarkın paralel çalışması.
    N8N workflow orkestrasyon katmanı.
    """

    def __init__(self, num_wheels: int = 7):
        self.wheels = [
            PrayerWheel(WheelConfig(
                name=f"CHAKRA_{i+1}",
                mantra=list(MantraType)[i % len(MantraType)]
            ))
            for i in range(num_wheels)
        ]

    async def spin_all(self, data: Any, times_per_wheel: int = 3) -> List[Any]:
        """Tüm çarkları paralel döndür"""
        tasks = [wheel.spin(data, times_per_wheel) for wheel in self.wheels]
        return await asyncio.gather(*tasks)

    async def cascade_spin(self, data: Any) -> Any:
        """Kaskad dönüşüm - her çarkın çıktısı bir sonrakine girer"""
        current = data
        for wheel in self.wheels:
            current = await wheel.spin(current, times=1)
        return current

    def get_cluster_stats(self) -> Dict[str, Any]:
        """Küme istatistikleri"""
        return {
            "total_wheels": len(self.wheels),
            "total_rotations": sum(w.rotation_count for w in self.wheels),
            "total_karma": sum(w.total_karma for w in self.wheels),
            "blessed_wheels": sum(1 for w in self.wheels if w.is_blessed),
            "wheels": [w.get_stats() for w in self.wheels]
        }

    def reset_all(self) -> None:
        """Tüm çarkları sıfırla"""
        for wheel in self.wheels:
            wheel.reset()
