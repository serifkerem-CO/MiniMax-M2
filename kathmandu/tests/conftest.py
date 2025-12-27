"""
🔧 Pytest Configuration
=======================
Test yapılandırması ve fixture'lar
"""

import pytest
import asyncio
import sys
from pathlib import Path

# Modül yolunu ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))


@pytest.fixture(scope="session")
def event_loop():
    """Oturum genelinde event loop"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_raw_data():
    """Örnek ham veri"""
    return """
    Türkiye Sanayi Raporu 2024
    ==========================

    Çelik Üretimi: 35 milyon ton
    İhracat: 250 milyar USD
    Enerji Tüketimi: Artış trendi
    Karbon Emisyonu: Düşüş hedefi 2050
    Dijital Dönüşüm: %45
    """


@pytest.fixture
def sample_purified_data():
    """Örnek arındırılmış veri"""
    return {
        "purified_text": "Türkiye Sanayi Raporu 2024 Çelik 35 milyon ton",
        "purity_level": "clear",
        "reduction_ratio": 0.3
    }


@pytest.fixture
def sample_forged_data():
    """Örnek dönüştürülmüş veri"""
    return {
        "forged_wisdom": "[ETİK][LOJİSTİK][ANALİZ] Sanayi dönüşüm analizi tamamlandı",
        "steel_score": 0.75,
        "monk_contributions": {
            "Claude": {"role": "ethicist"},
            "Mistral": {"role": "logistician"}
        }
    }


@pytest.fixture
def sample_vision_data():
    """Örnek vizyon verisi"""
    return {
        "prophecies": [
            "Sektör dönüşüm eşiğinde",
            "Enerji verimliliği kritik"
        ],
        "prayer_flags": [
            {"color": "blue", "message": "Teknoloji vizyonu"},
            {"color": "green", "message": "Sürdürülebilirlik"}
        ],
        "vision_score": 0.82
    }


# Pytest markers
def pytest_configure(config):
    """Pytest yapılandırması"""
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers",
        "integration: marks tests as integration tests"
    )
