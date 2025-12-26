"""
🎵 SACRED FREQUENCIES - Kutsal Frekanslar
==========================================

Solfeggio frekansları ve veri rezonansı.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Optional


class SacredFrequencies(Enum):
    """Solfeggio Frekansları"""
    UT = 396       # Korku ve suçluluktan kurtuluş
    RE = 417       # Durumları kolaylaştırma, değişim
    MI = 528       # Dönüşüm ve mucizeler (DNA onarımı)
    FA = 639       # Bağlantı ve ilişkiler
    SOL = 741      # İfade ve çözümler
    LA = 852       # Sezgisel uyanış
    SI = 963       # İlahi bağlantı - SAF CAZİBE


@dataclass
class FrequencyProfile:
    """Frekans profili"""
    hz: int
    name: str
    element: str
    description: str
    color: str


# Element-Frekans eşleşmeleri
ELEMENT_FREQUENCIES = {
    "toprak": FrequencyProfile(
        hz=396,
        name="UT - Topraklama",
        element="Earth",
        description="Köklenme ve stabilite",
        color="#8B4513"
    ),
    "su": FrequencyProfile(
        hz=417,
        name="RE - Akış",
        element="Water",
        description="Değişim ve arınma",
        color="#00BFFF"
    ),
    "ates": FrequencyProfile(
        hz=528,
        name="MI - Dönüşüm",
        element="Fire",
        description="Simya ve transmutasyon",
        color="#FF4500"
    ),
    "hava": FrequencyProfile(
        hz=741,
        name="SOL - İfade",
        element="Air",
        description="İletişim ve yayılma",
        color="#87CEEB"
    ),
    "eter": FrequencyProfile(
        hz=963,
        name="SI - İlahi",
        element="Ether",
        description="Saf cazibe ve bağlantı",
        color="#FFFFFF"
    ),
}


def tune_to_frequency(layer: str) -> Optional[FrequencyProfile]:
    """
    Katmana göre frekans ayarla.

    Her katmanın kendine özgü bir titreşimi var.
    """
    return ELEMENT_FREQUENCIES.get(layer.lower())


def calculate_resonance(data_length: int, layer: str) -> float:
    """
    Veri ve katman arasındaki rezonansı hesapla.

    Yüksek rezonans = daha iyi işleme.
    """
    freq = tune_to_frequency(layer)
    if not freq:
        return 0.0

    # Basit rezonans hesabı
    base_resonance = (data_length % freq.hz) / freq.hz
    return min(1.0, base_resonance + 0.5)


def get_harmonics(base_hz: int) -> list[int]:
    """Temel frekansın harmoniklerini al"""
    return [base_hz * i for i in range(1, 8)]


# Demo
if __name__ == "__main__":
    for layer, profile in ELEMENT_FREQUENCIES.items():
        print(f"{layer.upper()}: {profile.hz}Hz - {profile.name}")
        print(f"   {profile.description}")
        print(f"   Harmonikler: {get_harmonics(profile.hz)[:3]}")
        print()
