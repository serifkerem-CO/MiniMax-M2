"""
KATMANDU ENGINE v1.0
====================
"Om Mani Padme Hum" for Data Processing

Veri Stupasi - The Temple of Data Transformation
5 Elemental Layers ascending toward digital enlightenment.

Layers:
    1. TOPRAK (Earth)  - Chaos Ingestion
    2. SU (Water)      - Purification Flow
    3. ATES (Fire)     - Alchemical Forge
    4. HAVA (Air)      - Wind Transmission
    5. ETER (Ether)    - Cazibe (Attraction)

Author: XDATUM & CAZIBE Team
Frequency: 963Hz (Saf Cazibe Frekansi)
"""

__version__ = "1.0.0"
__codename__ = "KATMANDU"
__mantra__ = "VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE"

from .stupa import DataStupa
from .layers import ToprakLayer, SuLayer, AtesLayer, HavaLayer, EterLayer

__all__ = [
    "DataStupa",
    "ToprakLayer",
    "SuLayer",
    "AtesLayer",
    "HavaLayer",
    "EterLayer"
]
