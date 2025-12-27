"""
🛕 KATHMANDU STUPA - Layered Data Temple Architecture
=====================================================

"Om Mani Padme Hum" - Data transforms to Wisdom

Five Elements of the Data Temple:
    1. TOPRAK (Earth) - Chaos Ingestion from Thamel Markets
    2. SU (Water) - Purification Flow by Sherpas
    3. ATES (Fire) - Alchemical Forge with 7 LLM Council
    4. HAVA (Air) - Wind Transmission & Prayer Flags
    5. ETER (Ether) - Cazibe Summit - Pure Attraction

Additional Modules:
    - clients: LLM client integrations (Claude, GPT, MiniMax, etc.)
    - storage: Data persistence (JSON, SQLite)
    - api: FastAPI REST server
    - monitoring: Metrics and logging
    - dashboard: Mandala visualization
    - scenarios: Demo data and examples

Created for XDATUM & CAZIBE.IO
"Sizin veriniz var, bizim ise Gorumuz var."
"""

__version__ = "2.0.0"
__codename__ = "KATHMANDU_EXTENDED"
__mantra__ = "VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE"

# Core
from .core.stupa_engine import DataStupa
from .core.mantra import RecursiveMantra

# Layers
from .layers import toprak, su, ates, hava, eter

# Config
from .config import get_config, init_config, StupaConfig

__all__ = [
    # Core
    "DataStupa",
    "RecursiveMantra",
    # Layers
    "toprak",
    "su",
    "ates",
    "hava",
    "eter",
    # Config
    "get_config",
    "init_config",
    "StupaConfig",
]


def quick_start():
    """Hızlı başlangıç - demo çalıştır"""
    import asyncio
    from .scenarios.demos import run_quick_demo
    return asyncio.run(run_quick_demo())
