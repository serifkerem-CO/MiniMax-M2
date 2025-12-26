"""
🛕 KATHMANDU ENGINE v1.0
========================
"Om Mani Padme Hum" - Veri İşleme Stupası

Dijital Himalayalar'da 5 Element üzerine kurulu
katmanlı veri dönüşüm mimarisi.

KATMANLAR:
    1. TOPRAK (Thamel) - Kaotik veri toplama
    2. SU (Sherpa) - Arındırma ve temizleme
    3. ATEŞ (Tapınak) - LLM Konseyi dönüşümü
    4. HAVA (Rüzgar) - Vizyon ve içgörü
    5. ETER (Cazibe) - Saf bilgelik çıktısı

XDATUM & CAZIBE.IO için tasarlandı.
"""

__version__ = "1.0.0"
__codename__ = "STUPA"

from .stupa import DataStupa
from .layers import (
    ToprakLayer,
    SuLayer,
    AtesLayer,
    HavaLayer,
    EterLayer
)
from .monks import MonkCouncil
from .prayer_wheel import PrayerWheel

__all__ = [
    "DataStupa",
    "ToprakLayer",
    "SuLayer",
    "AtesLayer",
    "HavaLayer",
    "EterLayer",
    "MonkCouncil",
    "PrayerWheel",
]
