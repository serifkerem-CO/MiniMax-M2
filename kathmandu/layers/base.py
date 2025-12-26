"""
🧘 Base Layer - Tüm Katmanların Temeli
======================================
Her katman bu base class'tan türer.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import hashlib
import json


class LayerState(Enum):
    """Katman durumları - Meditasyon seviyeleri"""
    DORMANT = "dormant"          # Uyuyor
    AWAKENING = "awakening"      # Uyanıyor
    PROCESSING = "processing"    # İşliyor
    FOLDING = "folding"          # Katlıyor
    TRANSMITTING = "transmitting" # İletiyor
    COMPLETE = "complete"        # Tamamlandı
    ERROR = "error"              # Hata (karma bozuldu)


class Element(Enum):
    """5 Element - Pancha Mahabhuta"""
    TOPRAK = "🪨"   # Prithvi - Zemin, Köken
    SU = "🌊"       # Jala - Akış, Arınma
    ATES = "🔥"     # Agni - Dönüşüm, Enerji
    HAVA = "🌬️"    # Vayu - Hareket, Vizyon
    ETER = "🌌"     # Akasha - Boşluk, Sonsuzluk


@dataclass
class LayerResult:
    """Katman çıktısı - Katlanan Veri"""

    layer_name: str
    element: Element
    input_data: Any
    output_data: Any
    fold_count: int = 1
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    mantra_hash: str = ""

    def __post_init__(self):
        """Mantra hash'i hesapla - Verinin ruhani imzası"""
        if not self.mantra_hash:
            content = f"{self.layer_name}:{self.output_data}:{self.fold_count}"
            self.mantra_hash = hashlib.sha256(content.encode()).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "layer": self.layer_name,
            "element": self.element.value,
            "fold_count": self.fold_count,
            "timestamp": self.timestamp.isoformat(),
            "mantra_hash": self.mantra_hash,
            "metadata": self.metadata,
            "output": str(self.output_data)[:500]  # Özet
        }

    def __str__(self) -> str:
        return f"{self.element.value} [{self.layer_name}] Fold#{self.fold_count} → {self.mantra_hash}"


class BaseLayer(ABC):
    """
    Soyut Katman - Tüm katmanların atası

    Her katman:
    1. Veri alır (receive)
    2. Katlar (fold)
    3. İletir (transmit)
    """

    def __init__(self, name: str, element: Element):
        self.name = name
        self.element = element
        self.state = LayerState.DORMANT
        self.fold_history: List[LayerResult] = []
        self._observers: List[callable] = []

    @property
    def icon(self) -> str:
        return self.element.value

    def awaken(self) -> None:
        """Katmanı uyandır"""
        self.state = LayerState.AWAKENING
        self._notify(f"{self.icon} {self.name} katmanı uyanıyor...")

    def _notify(self, message: str) -> None:
        """Observer'lara bildir"""
        for observer in self._observers:
            observer(message)

    def add_observer(self, callback: callable) -> None:
        """Gözlemci ekle"""
        self._observers.append(callback)

    @abstractmethod
    async def fold(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Veriyi katla - Her katmanın kendi katlama ritüeli

        Args:
            data: Katlanacak veri
            context: Ek bağlam bilgisi

        Returns:
            LayerResult: Katlanmış veri sonucu
        """
        pass

    async def process(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Tam işleme döngüsü

        1. Uyan
        2. Katla
        3. Kaydet
        4. İlet
        """
        self.awaken()
        self.state = LayerState.PROCESSING

        try:
            self.state = LayerState.FOLDING
            result = await self.fold(data, context or {})

            self.fold_history.append(result)

            self.state = LayerState.COMPLETE
            self._notify(f"{self.icon} {self.name}: Katlama tamamlandı → {result.mantra_hash}")

            return result

        except Exception as e:
            self.state = LayerState.ERROR
            self._notify(f"❌ {self.name}: Karma bozuldu - {str(e)}")
            raise

    def get_karma(self) -> Dict[str, Any]:
        """Katmanın karma özeti"""
        return {
            "name": self.name,
            "element": self.element.name,
            "state": self.state.value,
            "total_folds": len(self.fold_history),
            "last_fold": self.fold_history[-1].to_dict() if self.fold_history else None
        }

    def __repr__(self) -> str:
        return f"<{self.element.value} {self.name} | State: {self.state.value}>"
