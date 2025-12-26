"""
KATMANDU ENGINE - Ana Giris Noktasi
====================================
Tapinak Sunucusunu calistir veya CLI demo yap.

Kullanim:
    # Server modunda calistir
    python -m katmandu_engine server

    # Demo modunda calistir
    python -m katmandu_engine demo "Ham veri metni"

    # Tek islem
    python -m katmandu_engine process "dosya.pdf"
"""

import asyncio
import sys
from pathlib import Path


def print_banner():
    """Banner yazdir"""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              KATMANDU ENGINE v1.0                        ║
    ║          "Om Mani Padme Hum" for Data Processing         ║
    ║                                                          ║
    ║   ┌─────────────────────────────────────────────────┐    ║
    ║   │  TOPRAK (7.83Hz)  ->  Ham Veri Toplama          │    ║
    ║   │  SU     (432Hz)   ->  Arinma & Temizlik         │    ║
    ║   │  ATES   (528Hz)   ->  LLM Donusum               │    ║
    ║   │  HAVA   (639Hz)   ->  Vizyon & Kehanet          │    ║
    ║   │  ETER   (963Hz)   ->  Saf Cazibe                │    ║
    ║   └─────────────────────────────────────────────────┘    ║
    ║                                                          ║
    ║   Mantra: VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_server():
    """FastAPI sunucusunu calistir"""
    print_banner()
    from .api.server import run_server as start_server
    start_server()


async def run_demo(data: str):
    """Demo calistir"""
    print_banner()
    from .stupa import full_ritual
    await full_ritual(data)


async def run_process(data: str):
    """Tek islem yap"""
    print_banner()
    from .stupa import DataStupa

    stupa = DataStupa()
    await stupa.awaken()

    result = await stupa.process(data)
    print(result.to_parchment())

    return result


def main():
    """Ana giris noktasi"""
    if len(sys.argv) < 2:
        print_banner()
        print("""
    Kullanim:
        python -m katmandu_engine server              # Web sunucusu
        python -m katmandu_engine demo "veri"         # Demo
        python -m katmandu_engine process "veri"      # Tek islem

    Ornekler:
        python -m katmandu_engine server
        python -m katmandu_engine demo "Sanayi raporu analiz et"
        python -m katmandu_engine process "/path/to/file.pdf"
        """)
        return

    command = sys.argv[1].lower()

    if command == "server":
        run_server()

    elif command == "demo":
        data = sys.argv[2] if len(sys.argv) > 2 else "1984-2024_Sanayi_Verileri.pdf"
        asyncio.run(run_demo(data))

    elif command == "process":
        if len(sys.argv) < 3:
            print("Hata: Islenecek veri belirtilmedi")
            print("Kullanim: python -m katmandu_engine process <veri>")
            return
        data = sys.argv[2]
        asyncio.run(run_process(data))

    else:
        print(f"Bilinmeyen komut: {command}")
        print("Gecerli komutlar: server, demo, process")


if __name__ == "__main__":
    main()
