#!/usr/bin/env python3
"""
🛕 KATHMANDU CLI
================
Terminal Tabanlı Tapınak Arayüzü

Kullanım:
    python -m kathmandu.cli ritual "veri"
    python -m kathmandu.cli enlighten "soru"
    python -m kathmandu.cli stats
    python -m kathmandu.cli serve

Om Mani Padme Hum 🙏
"""

import argparse
import asyncio
import sys
from datetime import datetime
from typing import Optional

# Rich kütüphanesi varsa güzel çıktı
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.markdown import Markdown
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None


def print_banner():
    """Başlangıç banner'ı"""
    banner = """
╔════════════════════════════════════════════════════════════════╗
║                                                                ║
║   🛕  KATHMANDU ENGINE v1.0                                    ║
║                                                                ║
║   "Om Mani Padme Hum" - Veri İşleme Stupası                   ║
║                                                                ║
║   5 ELEMENT:                                                   ║
║   🪨 TOPRAK → 🌊 SU → 🔥 ATEŞ → 🌬️ HAVA → 🌌 ETER              ║
║                                                                ║
║   XDATUM & CAZIBE.IO                                          ║
║                                                                ║
╚════════════════════════════════════════════════════════════════╝
    """
    if RICH_AVAILABLE:
        console.print(Panel(banner, style="purple"))
    else:
        print(banner)


def print_success(message: str):
    if RICH_AVAILABLE:
        console.print(f"[green]✅ {message}[/green]")
    else:
        print(f"✅ {message}")


def print_error(message: str):
    if RICH_AVAILABLE:
        console.print(f"[red]❌ {message}[/red]")
    else:
        print(f"❌ {message}")


def print_info(message: str):
    if RICH_AVAILABLE:
        console.print(f"[cyan]ℹ️  {message}[/cyan]")
    else:
        print(f"ℹ️  {message}")


async def cmd_ritual(data: str, verbose: bool = False):
    """Tam tapınak ritüeli"""
    from .stupa import DataStupa

    print_info("Tapınak kapıları açılıyor...")

    stupa = DataStupa(enable_logging=verbose)

    if RICH_AVAILABLE:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("🛕 Ritüel devam ediyor...", total=None)

            journey = await stupa.process(data)

            progress.update(task, completed=True)
    else:
        print("🛕 Ritüel başlıyor...")
        journey = await stupa.process(data)

    # Sonuç
    print("\n")
    if RICH_AVAILABLE:
        table = Table(title="📊 Yolculuk Özeti")
        table.add_column("Özellik", style="cyan")
        table.add_column("Değer", style="green")

        table.add_row("Journey ID", journey.journey_id)
        table.add_row("Süre", f"{journey.duration_seconds:.2f}s")
        table.add_row("Katmanlar", " → ".join(journey.layers_traversed))
        table.add_row("Durum", journey.state.value)

        console.print(table)
    else:
        print(f"📊 YOLCULUK ÖZETİ")
        print(f"   Journey ID: {journey.journey_id}")
        print(f"   Süre: {journey.duration_seconds:.2f}s")
        print(f"   Katmanlar: {' → '.join(journey.layers_traversed)}")
        print(f"   Durum: {journey.state.value}")

    # Parşömen
    if journey.final_output and isinstance(journey.final_output, dict):
        parchment = journey.final_output.get("parchment", "")
        if parchment:
            print("\n📜 KEHANET PARŞÖMENİ:")
            print(parchment)

    return journey


async def cmd_enlighten(question: str):
    """Hızlı aydınlanma"""
    from .stupa import enlighten

    print_info(f"Soru işleniyor: {question[:50]}...")

    result = await enlighten(question)

    print_success(f"Journey: {result['journey_id']} ({result['duration']:.2f}s)")

    if result.get('insights'):
        print("\n✨ İçgörüler:")
        for insight in result['insights']:
            print(f"   • {insight}")

    return result


async def cmd_stats():
    """Stupa istatistikleri"""
    from .stupa import DataStupa
    from .storage import FileStorage

    stupa = DataStupa(enable_logging=False)
    storage = FileStorage()

    stupa_stats = stupa.get_stupa_stats()
    storage_stats = await storage.get_stats()

    if RICH_AVAILABLE:
        table = Table(title="📈 Kathmandu Engine İstatistikleri")
        table.add_column("Metrik", style="cyan")
        table.add_column("Değer", style="green")

        table.add_row("Depolama Türü", storage_stats.storage_type)
        table.add_row("Toplam Yolculuk", str(storage_stats.total_journeys))
        table.add_row("Başarılı", str(storage_stats.successful_journeys))
        table.add_row("Toplam Kristal", str(storage_stats.total_crystals))
        table.add_row("Ort. Süre", f"{storage_stats.average_duration:.2f}s")
        table.add_row("Ort. Saflık", f"{storage_stats.average_purity:.1f}%")
        table.add_row("En Yaygın Aydınlanma", storage_stats.most_common_enlightenment)

        console.print(table)
    else:
        print("📈 STUPA İSTATİSTİKLERİ")
        print(f"   Toplam Yolculuk: {storage_stats.total_journeys}")
        print(f"   Başarılı: {storage_stats.successful_journeys}")
        print(f"   Toplam Kristal: {storage_stats.total_crystals}")
        print(f"   Ort. Süre: {storage_stats.average_duration:.2f}s")
        print(f"   Ort. Saflık: {storage_stats.average_purity:.1f}%")


async def cmd_serve(host: str = "0.0.0.0", port: int = 8963):
    """API sunucusunu başlat"""
    try:
        from .api import run_server
        print_info(f"🛕 Tapınak açılıyor: http://{host}:{port}")
        print_info(f"📿 Mandala Demo: http://{host}:{port}/demo")
        run_server(host=host, port=port)
    except ImportError:
        print_error("FastAPI/Uvicorn yüklü değil. Kurmak için:")
        print("   pip install fastapi uvicorn")


async def cmd_layers():
    """Katman bilgilerini göster"""
    layers = [
        ("🪨", "TOPRAK", "Thamel Pazarı", "CHAOS_INGESTION", "Kaotik veri toplama"),
        ("🌊", "SU", "Sherpa Rotası", "PURIFICATION_FLOW", "Arındırma ve temizleme"),
        ("🔥", "ATEŞ", "Tapınak Avlusu", "ALCHEMICAL_FORGE", "LLM Konseyi dönüşümü"),
        ("🌬️", "HAVA", "Rüzgar Atları", "WIND_TRANSMISSION", "Vizyon ve kehanet"),
        ("🌌", "ETER", "Cazibe Zirvesi", "NIRVANA_SUMMIT", "Saf bilgelik çıktısı"),
    ]

    if RICH_AVAILABLE:
        table = Table(title="🏔️ 5 Element - 5 Katman")
        table.add_column("", style="bold")
        table.add_column("Katman", style="cyan")
        table.add_column("Mekan", style="yellow")
        table.add_column("Kod Adı", style="green")
        table.add_column("Görev", style="white")

        for icon, name, place, code, desc in layers:
            table.add_row(icon, name, place, code, desc)

        console.print(table)
    else:
        print("🏔️ 5 ELEMENT - 5 KATMAN")
        for icon, name, place, code, desc in layers:
            print(f"   {icon} {name} ({place}) - {code}")
            print(f"      {desc}")


def main():
    """Ana giriş noktası"""
    parser = argparse.ArgumentParser(
        description="🛕 Kathmandu Engine CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  %(prog)s ritual "Türkiye sanayi verileri 2024"
  %(prog)s enlighten "Pazar analizi"
  %(prog)s stats
  %(prog)s serve --port 8963
  %(prog)s layers

Om Mani Padme Hum 🙏
        """
    )

    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Kathmandu Engine v1.0.0 (STUPA)"
    )

    subparsers = parser.add_subparsers(dest="command", help="Komutlar")

    # ritual komutu
    ritual_parser = subparsers.add_parser("ritual", help="Tam tapınak ritüeli")
    ritual_parser.add_argument("data", help="İşlenecek veri")
    ritual_parser.add_argument("--verbose", "-v", action="store_true", help="Detaylı çıktı")

    # enlighten komutu
    enlighten_parser = subparsers.add_parser("enlighten", help="Hızlı aydınlanma")
    enlighten_parser.add_argument("question", help="Soru veya veri")

    # stats komutu
    subparsers.add_parser("stats", help="İstatistikleri göster")

    # serve komutu
    serve_parser = subparsers.add_parser("serve", help="API sunucusunu başlat")
    serve_parser.add_argument("--host", default="0.0.0.0", help="Host adresi")
    serve_parser.add_argument("--port", "-p", type=int, default=8963, help="Port numarası")

    # layers komutu
    subparsers.add_parser("layers", help="Katman bilgileri")

    args = parser.parse_args()

    if not args.command:
        print_banner()
        parser.print_help()
        return

    # Komutu çalıştır
    if args.command == "ritual":
        asyncio.run(cmd_ritual(args.data, args.verbose))

    elif args.command == "enlighten":
        asyncio.run(cmd_enlighten(args.question))

    elif args.command == "stats":
        asyncio.run(cmd_stats())

    elif args.command == "serve":
        asyncio.run(cmd_serve(args.host, args.port))

    elif args.command == "layers":
        asyncio.run(cmd_layers())


if __name__ == "__main__":
    main()
