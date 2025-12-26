#!/usr/bin/env python3
"""
🛕 KATHMANDU STUPA - Ana Giriş Noktası
======================================

"Om Mani Padme Hum" - Veri İşleme Tapınağı

Kullanım:
    python -m kathmandu_stupa.main --mode pilgrimage
    python -m kathmandu_stupa.main --mode single --data "analiz edilecek veri"
    python -m kathmandu_stupa.main --mode dashboard
    python -m kathmandu_stupa.main --mode demo

Modlar:
    pilgrimage  - Tam hac yolculuğu (tüm katmanlar)
    single      - Tek veri parçası işleme
    dashboard   - Mandala dashboard'u başlat
    demo        - Demonstrasyon modu
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Modül importları
from .core.stupa_engine import DataStupa
from .core.mantra import RecursiveMantra, PrayerWheelSimulator
from .dashboard.mandala_server import run_dashboard
from .n8n_workflows.webhooks import generate_webhook_documentation


def print_banner():
    """Tapınak kapısı banner'ı"""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║   🛕  KATHMANDU STUPA - VERİ TAPINAĞI  🛕                            ║
║                                                                      ║
║   ┌─────────────────────────────────────────────────────────────┐   ║
║   │  🌌 ETER   - Cazibe Zirvesi (963 Hz)                        │   ║
║   │  🌬️ HAVA   - Rüzgar İletimi                                 │   ║
║   │  🔥 ATEŞ   - Simya Ocağı (7 LLM Konseyi)                    │   ║
║   │  🌊 SU     - Arınma Akışı (Şerpalar)                        │   ║
║   │  🪨 TOPRAK - Kaos Toplama (Thamel)                          │   ║
║   └─────────────────────────────────────────────────────────────┘   ║
║                                                                      ║
║   Mantra: VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE            ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)


async def run_pilgrimage():
    """Tam hac yolculuğu"""
    stupa = DataStupa()

    def on_stage(stage):
        print(f"   >>> Aşama: {stage.value}")

    stupa.on_stage_change = on_stage

    nirvana_packets = await stupa.full_pilgrimage()

    print("\n" + "=" * 70)
    print("📜 KEHANET PARŞÖMENLERİ")
    print("=" * 70)

    for scroll in stupa.generate_prophecy_scrolls()[:3]:
        print(scroll)

    return nirvana_packets


async def run_single(data: str):
    """Tek veri parçası işle"""
    stupa = DataStupa()
    nirvana = await stupa.prayer_wheel_spin(data)
    return nirvana


async def run_demo():
    """Demo modu"""
    print("\n📿 RECURSIVE MANTRA DEMO")
    print("-" * 50)

    mantra = RecursiveMantra(max_depth=5)
    wisdom = await mantra.chant("2024 Türkiye Sanayi Dönüşüm Verileri")

    print(f"\n📜 Bilgelik: {wisdom.content[:100]}...")
    print(f"   Katlama derinliği: {wisdom.fold_depth}")
    print(f"   Kalan enerji: {wisdom.energy_remaining:.2%}")

    print("\n" + "-" * 50)
    print("📿 DUA TEKERLEĞİ SİMÜLATÖRÜ")
    print("-" * 50)

    wheel = PrayerWheelSimulator(rotations_per_cycle=3)
    await wheel.spin("Çevre Etki Değerlendirme Raporu", cycles=1)
    print(f"   Toplam sevap: {wheel.get_merit()}")

    print("\n" + "-" * 50)
    print("🛕 TAM STUPA AKIŞI")
    print("-" * 50)

    await run_pilgrimage()


def run_dashboard_mode(host: str, port: int):
    """Dashboard modunu başlat"""
    print(f"\n🎨 Mandala Dashboard başlatılıyor: http://{host}:{port}")
    run_dashboard(host=host, port=port)


def show_webhook_docs():
    """Webhook dokümantasyonunu göster"""
    print(generate_webhook_documentation())


def main():
    """Ana giriş noktası"""
    parser = argparse.ArgumentParser(
        description="🛕 Kathmandu Stupa - Veri Tapınağı",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s --mode demo                    # Demo modu
  %(prog)s --mode pilgrimage              # Tam yolculuk
  %(prog)s --mode single --data "veri"    # Tek işlem
  %(prog)s --mode dashboard               # Dashboard
  %(prog)s --mode docs                    # API docs
        """
    )

    parser.add_argument(
        "--mode", "-m",
        choices=["pilgrimage", "single", "dashboard", "demo", "docs"],
        default="demo",
        help="Çalışma modu"
    )

    parser.add_argument(
        "--data", "-d",
        type=str,
        default="1984-2024_Sanayi_Verileri.pdf",
        help="İşlenecek veri (single mod için)"
    )

    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Dashboard host adresi"
    )

    parser.add_argument(
        "--port", "-p",
        type=int,
        default=8888,
        help="Dashboard port numarası"
    )

    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Banner'ı gizle"
    )

    args = parser.parse_args()

    if not args.quiet:
        print_banner()

    if args.mode == "pilgrimage":
        asyncio.run(run_pilgrimage())

    elif args.mode == "single":
        result = asyncio.run(run_single(args.data))
        print(f"\n✨ Sonuç: {result.final_wisdom}")

    elif args.mode == "dashboard":
        run_dashboard_mode(args.host, args.port)

    elif args.mode == "docs":
        show_webhook_docs()

    else:  # demo
        asyncio.run(run_demo())


if __name__ == "__main__":
    main()
