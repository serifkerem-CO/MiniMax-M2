#!/usr/bin/env python3
"""
🛕 TAPINAK RİTÜELİ
==================
Kathmandu Engine Demo

Bu script, veriyi 5 katmandan geçirerek
bilgeliğe dönüştürür.

Kullanım:
    python temple_ritual.py
"""

import asyncio
import sys
from pathlib import Path

# Modül yolunu ekle
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from kathmandu import DataStupa, enlighten


async def run_full_ritual():
    """
    Tam ritüel - 5 katmandan geçiş
    """
    print("=" * 60)
    print("🛕 KATHMANDU ENGINE - TAPINAK RİTÜELİ BAŞLIYOR")
    print("=" * 60)
    print()

    # Stupa oluştur
    stupa = DataStupa(enable_logging=True)

    # Ham veri
    raw_data = """
    1984-2024 Türkiye Sanayi Verileri
    - Çelik üretimi: 35 milyon ton (2023)
    - İhracat: 250 milyar USD
    - Enerji tüketimi: Artış trendi
    - Karbon emisyonu: Düşüş hedefi 2050
    - Dijital dönüşüm oranı: %45
    """

    print(f"📥 HAM VERİ:\n{raw_data}")
    print("\n" + "=" * 60 + "\n")

    # Veriyi işle
    journey = await stupa.process(
        data=raw_data,
        context={
            "sources": ["sanayi_raporu_2024.pdf", "enerji_analizi.csv"],
            "client": "XDATUM_TEST"
        }
    )

    print("\n" + "=" * 60)
    print("📊 YOLCULUK ÖZETİ")
    print("=" * 60)
    print(f"   🆔 Journey ID: {journey.journey_id}")
    print(f"   ⏱️ Süre: {journey.duration_seconds:.2f}s")
    print(f"   🏔️ Katmanlar: {' → '.join(journey.layers_traversed)}")
    print(f"   🧘 Durum: {journey.state.value}")
    print()

    # Kehanet parşömeni
    if journey.final_output and isinstance(journey.final_output, dict):
        parchment = journey.final_output.get("parchment", "")
        if parchment:
            print("📜 KEHANET PARŞÖMENİ:")
            print(parchment)

    # Stupa istatistikleri
    print("\n" + "=" * 60)
    print("📈 STUPA İSTATİSTİKLERİ")
    print("=" * 60)
    stats = stupa.get_stupa_stats()
    print(f"   🛕 Toplam Yolculuk: {stats['total_journeys']}")
    print(f"   ✅ Başarılı: {stats['successful_journeys']}")
    print(f"   ⏱️ Ortalama Süre: {stats['average_duration']:.2f}s")


async def run_quick_enlightenment():
    """
    Hızlı aydınlanma - Tek satır
    """
    print("=" * 60)
    print("⚡ HIZLI AYDINLANMA")
    print("=" * 60)

    result = await enlighten("Pazar analizi: Rekabet artıyor, marjlar daralıyor")

    print(f"\n🆔 Journey: {result['journey_id']}")
    print(f"⏱️ Süre: {result['duration']:.2f}s")

    if result.get('insights'):
        print("\n✨ İçgörüler:")
        for insight in result['insights']:
            print(f"   • {insight}")


async def main():
    """Ana fonksiyon"""
    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🛕 KATHMANDU ENGINE v1.0                                   ║")
    print("║  'Om Mani Padme Hum' - Veri İşleme Stupası                 ║")
    print("║                                                            ║")
    print("║  5 ELEMENT:                                                ║")
    print("║  🪨 TOPRAK → 🌊 SU → 🔥 ATEŞ → 🌬️ HAVA → 🌌 ETER           ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()

    # Tam ritüel
    await run_full_ritual()

    print("\n" + "─" * 60 + "\n")

    # Hızlı aydınlanma
    await run_quick_enlightenment()

    print("\n" + "═" * 60)
    print("🙏 NAMASTE - Ritüel tamamlandı")
    print("═" * 60)


if __name__ == "__main__":
    asyncio.run(main())
