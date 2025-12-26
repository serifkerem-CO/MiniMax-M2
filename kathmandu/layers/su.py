"""
🌊 KATMAN 2: SU (SHERPA ROTASI)
================================
"Nehirler Birleşiyor & Arınma"

Topraktan çıkan veri, akışa kapılır.
Verinin yıkandığı nehir.

Aktörler: CORE FLOW (111 Persona) + Global Şerpalar
Kod Adı: PURIFICATION_FLOW
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from enum import Enum

from .base import BaseLayer, Element, LayerResult


class PurityLevel(Enum):
    """Arınma Seviyeleri"""
    MUDDY = "muddy"           # Çamurlu
    CLOUDY = "cloudy"         # Bulanık
    CLEARING = "clearing"     # Durulmakta
    CLEAR = "clear"           # Berrak
    CRYSTAL = "crystal"       # Kristal
    SACRED = "sacred"         # Kutsal (Ganga seviyesi)


@dataclass
class Sherpa:
    """
    Şerpa - Veri Taşıyıcısı ve Arındırıcısı

    Global Gençlik ekibi: Dilara (JP), Ali (AU), Kenan (RU)
    İnsan gözüyle halüsinasyonu eler.
    """

    name: str
    origin: str               # Ülke kodu
    specialty: str            # Uzmanlık alanı
    purification_count: int = 0
    hallucination_catches: int = 0  # Yakaladığı halüsinasyon sayısı

    def __post_init__(self):
        self.id = f"SHERPA_{self.name.upper()}"

    async def wash(self, dirty_data: str) -> tuple[str, int]:
        """
        Veriyi yıka - Çamuru temizle

        Returns:
            (temiz_veri, çıkarılan_token_sayısı)
        """
        original_len = len(dirty_data)

        # 1. Gereksiz boşlukları temizle
        cleaned = re.sub(r'\s+', ' ', dirty_data)

        # 2. Tekrar eden kelimeleri kaldır
        words = cleaned.split()
        seen: Set[str] = set()
        unique_words = []
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen or len(word) < 3:
                unique_words.append(word)
                seen.add(word_lower)
        cleaned = ' '.join(unique_words)

        # 3. Özel karakterleri normalize et
        cleaned = re.sub(r'[^\w\s.,;:!?()-]', '', cleaned)

        # 4. Boş satırları kaldır
        cleaned = re.sub(r'\n\s*\n', '\n', cleaned)

        removed_tokens = original_len - len(cleaned)
        self.purification_count += 1

        return cleaned.strip(), removed_tokens

    async def detect_hallucination(self, data: str) -> List[str]:
        """
        Halüsinasyon tespiti - İnsan Gözü

        LLM'lerin ürettiği saçmalıkları yakala.
        """
        hallucinations = []

        # Şüpheli kalıplar
        suspicious_patterns = [
            r'(?:kesinlikle|mutlaka|asla).*(?:kesinlikle|mutlaka|asla)',  # Çelişkili kesinlik
            r'\d{4}\'te.*\d{4}\'te',  # Çelişen tarihler
            r'(%\d+).*\1.*\1',  # Tekrar eden yüzdeler
            r'(milyar|milyon)\s+\1',  # Tekrar eden büyüklükler
        ]

        for pattern in suspicious_patterns:
            matches = re.findall(pattern, data, re.IGNORECASE)
            if matches:
                hallucinations.extend([f"Şüpheli kalıp: {m}" for m in matches[:3]])
                self.hallucination_catches += 1

        return hallucinations


# Global Şerpa Ekibi
GLOBAL_SHERPAS = [
    Sherpa(name="Dilara", origin="JP", specialty="Teknoloji & Veri Bilimi"),
    Sherpa(name="Ali", origin="AU", specialty="Finans & Ekonomi"),
    Sherpa(name="Kenan", origin="RU", specialty="Enerji & Sanayi"),
    Sherpa(name="Maya", origin="NP", specialty="Çevre & Sürdürülebilirlik"),
    Sherpa(name="Raj", origin="IN", specialty="Yazılım & AI"),
    Sherpa(name="Sofia", origin="BR", specialty="Tarım & Biyoteknoloji"),
    Sherpa(name="Kim", origin="KR", specialty="Üretim & Lojistik"),
]


@dataclass
class PurifiedData:
    """Arındırılmış Veri Paketi"""

    original_size: int
    purified_size: int
    content: str
    purity_level: PurityLevel
    sherpa_id: str
    hallucinations_found: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def reduction_ratio(self) -> float:
        """Küçülme oranı"""
        if self.original_size == 0:
            return 0.0
        return 1 - (self.purified_size / self.original_size)

    @property
    def is_clean(self) -> bool:
        """Temiz mi?"""
        return self.purity_level in [PurityLevel.CLEAR, PurityLevel.CRYSTAL, PurityLevel.SACRED]


class SuLayer(BaseLayer):
    """
    🌊 SU KATMANI

    Sherpa Rotası - Nehirde Arınma

    Görev: Yükü hafiflet, çamuru yıka, halüsinasyonu ele
    Teknoloji: Minimax M2 (hızlı akış) + İnsan Gözü
    Çıktı: Saf, temizlenmiş, doğrulanmış metin
    """

    def __init__(self, sherpas: Optional[List[Sherpa]] = None):
        super().__init__("SU", Element.SU)
        self.code_name = "PURIFICATION_FLOW"
        self.sherpas = sherpas or GLOBAL_SHERPAS.copy()
        self.river_flow: List[PurifiedData] = []
        self.mantra = "AKIŞ_ARINMA_DÖNÜŞÜM"

        # Nehir istatistikleri
        self.total_tokens_removed = 0
        self.total_hallucinations_caught = 0

    async def fold(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Su Katlama Ritüeli

        Veriyi nehirde yıka, Şerpalar gözetiminde arındır.
        """
        context = context or {}

        # Gelen veriyi string'e dönüştür
        if isinstance(data, dict) and "packets" in data:
            # Toprak katmanından geliyor
            raw_texts = [
                p.get("origin", str(p)) for p in data.get("packets", [])
            ]
            input_text = " | ".join(raw_texts)
        elif isinstance(data, str):
            input_text = data
        else:
            input_text = str(data)

        self._notify(f"🌊 [SU] Şerpalar veriyi nehire bırakıyor... ({len(input_text)} karakter)")

        # Şerpa döngüsü - her şerpa bir kez yıkar
        current_text = input_text
        total_removed = 0
        all_hallucinations = []
        processing_sherpas = []

        for sherpa in self.sherpas[:3]:  # İlk 3 şerpa aktif
            # Yıkama
            washed, removed = await sherpa.wash(current_text)
            total_removed += removed

            # Halüsinasyon kontrolü
            hallucinations = await sherpa.detect_hallucination(washed)
            all_hallucinations.extend(hallucinations)

            current_text = washed
            processing_sherpas.append(sherpa.name)

            self._notify(f"   ↳ 🏔️ {sherpa.name} ({sherpa.origin}): -{removed} token, {len(hallucinations)} halüsinasyon")

        # Saflık seviyesini belirle
        reduction = 1 - (len(current_text) / len(input_text)) if input_text else 0
        purity = self._calculate_purity(reduction, len(all_hallucinations))

        purified = PurifiedData(
            original_size=len(input_text),
            purified_size=len(current_text),
            content=current_text,
            purity_level=purity,
            sherpa_id=",".join(processing_sherpas),
            hallucinations_found=all_hallucinations
        )

        self.river_flow.append(purified)
        self.total_tokens_removed += total_removed
        self.total_hallucinations_caught += len(all_hallucinations)

        self._notify(f"🌊 [SU] Arınma tamamlandı | Saflık: {purity.value} | Küçülme: {purified.reduction_ratio:.1%}")

        return LayerResult(
            layer_name=self.name,
            element=self.element,
            input_data={"original_text": input_text[:200] + "..."},
            output_data={
                "purified_text": current_text,
                "purity_level": purity.value,
                "original_size": len(input_text),
                "purified_size": len(current_text),
                "reduction_ratio": purified.reduction_ratio,
                "tokens_removed": total_removed,
                "hallucinations": all_hallucinations,
                "processing_sherpas": processing_sherpas
            },
            fold_count=len(processing_sherpas),  # Her şerpa bir katlama
            metadata={
                "code_name": self.code_name,
                "mantra": self.mantra,
                "active_sherpas": len(self.sherpas)
            }
        )

    def _calculate_purity(self, reduction: float, hallucination_count: int) -> PurityLevel:
        """Saflık seviyesi hesapla"""
        score = (reduction * 50) + (50 - hallucination_count * 10)

        if score >= 90:
            return PurityLevel.SACRED
        elif score >= 75:
            return PurityLevel.CRYSTAL
        elif score >= 60:
            return PurityLevel.CLEAR
        elif score >= 40:
            return PurityLevel.CLEARING
        elif score >= 20:
            return PurityLevel.CLOUDY
        else:
            return PurityLevel.MUDDY

    def get_river_stats(self) -> Dict[str, Any]:
        """Nehir istatistikleri"""
        return {
            "total_purified": len(self.river_flow),
            "total_tokens_removed": self.total_tokens_removed,
            "total_hallucinations_caught": self.total_hallucinations_caught,
            "sherpa_stats": [
                {
                    "name": s.name,
                    "origin": s.origin,
                    "purification_count": s.purification_count,
                    "hallucination_catches": s.hallucination_catches
                }
                for s in self.sherpas
            ]
        }
