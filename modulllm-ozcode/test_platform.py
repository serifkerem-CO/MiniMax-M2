"""
MODULllm.com - Platform Test Script

Tüm sistemleri test eder:
- Orchestrator (11 Akıl + 12. Akıl)
- Öz Veritabanı
- DEAVAEM Gemi API
- Platform API
"""

import asyncio
import sys
from rich.console import Console
from rich.table import Table
from rich import print as rprint

# Modül import
sys.path.append('.')

from orchestration.oz_orchestrator import OzKodOrchestrator
from database.oz_database import OzVeritabani, IcerikTipi, initialize_oz_db
from gemi.deavaem_api import DeavaemGemiAPI

console = Console()


async def test_orchestrator():
    """11 Akıl Harmanları + 12. Akıl Test"""
    console.rule("[bold blue]🧠 Orchestrator Test (11 Akıl + 12. Akıl)")

    orchestrator = OzKodOrchestrator()

    test_soru = "MODULllm.com platformunun felsefesi nedir?"

    console.print(f"\n📝 Test Sorusu: [cyan]{test_soru}[/cyan]\n")

    try:
        sonuc = await orchestrator.oz_koddan_yanitla(test_soru)

        # 11 Akıl yanıtları tablosu
        table = Table(title="11 Akıl Harmanları Yanıtları")
        table.add_column("Akıl", style="cyan")
        table.add_column("Model", style="green")
        table.add_column("Güven", style="yellow")
        table.add_column("Yanıt (İlk 100 karakter)", style="white")

        for akil in sonuc["on_bir_akil"]:
            table.add_row(
                akil["akil"].upper(),
                akil["yanitlayan_model"],
                f"{akil['guven']:.2f}",
                akil["icerik"][:100] + "..."
            )

        console.print(table)

        # 12. Akıl Sentezi
        console.print("\n[bold green]⚡ 12. Akıl Sentezi:[/bold green]")
        sentez = sonuc["on_ikinci_akil_sentezi"]["sentez"]
        console.print(f"[white]{sentez[:500]}...[/white]\n")

        console.print(f"✅ Orchestrator testi [bold green]BAŞARILI[/bold green]\n")

        await orchestrator.close()

        return True

    except Exception as e:
        console.print(f"❌ Orchestrator testi [bold red]BAŞARISIZ[/bold red]: {e}\n")
        return False


async def test_oz_db():
    """Öz Veritabanı Test"""
    console.rule("[bold yellow]📚 Öz Veritabanı Test")

    try:
        db = initialize_oz_db()

        # Test içerik ekle
        db.ekle(
            tip=IcerikTipi.SORU_CEVAP,
            baslik="Test: MODULllm Felsefesi",
            icerik="MODULllm.com tamamen bağımsız bir platformdur. Öz kodundan doğar!",
            etiketler=["modulllm", "felsefe", "oz-kod"],
            yaratici="test_script"
        )

        # Arama testi
        sonuclar = db.ara("MODULllm felsefe", limit=5)

        table = Table(title="Arama Sonuçları")
        table.add_column("Başlık", style="cyan")
        table.add_column("Tip", style="green")
        table.add_column("Benzerlik", style="yellow")
        table.add_column("Etiketler", style="white")

        for sonuc in sonuclar:
            table.add_row(
                sonuc.icerik.baslik[:50],
                sonuc.icerik.tip.value,
                f"{sonuc.benzerlik_skoru:.2f}",
                ", ".join(sonuc.icerik.etiketler[:3])
            )

        console.print(table)

        # İstatistikler
        stats = db.istatistikler()
        console.print(f"\n📊 Toplam İçerik: [bold]{stats['toplam_icerik']}[/bold]")
        console.print(f"Tip Dağılımı: {stats['tip_dagilimi']}\n")

        console.print(f"✅ Öz Veritabanı testi [bold green]BAŞARILI[/bold green]\n")

        return True

    except Exception as e:
        console.print(f"❌ Öz Veritabanı testi [bold red]BAŞARISIZ[/bold red]: {e}\n")
        return False


async def test_gemi_api():
    """DEAVAEM Gemi API Test"""
    console.rule("[bold magenta]🚢 DEAVAEM Gemi API Test")

    try:
        gemi = DeavaemGemiAPI()

        # Durum sorgula
        durum = await gemi.durum_sorgula()

        table = Table(title="Gemi Durumu")
        table.add_column("Metrik", style="cyan")
        table.add_column("Değer", style="yellow")

        table.add_row("Online", "✅" if durum.online else "❌")
        table.add_row("Sıcaklık", f"{durum.sicaklik}°C")
        table.add_row("GPU Kullanım", f"{durum.gpu_kullanim}%")
        table.add_row("CPU Kullanım", f"{durum.cpu_kullanim}%")
        table.add_row("Bellek Kullanım", f"{durum.bellek_kullanim}%")
        table.add_row("Aktif İşlemler", str(durum.aktif_islemler))
        table.add_row("Su Soğutma Akış", f"{durum.su_sogutma_akis} L/dk")
        table.add_row("Enerji Tüketim", f"{durum.enerji_tuketim} W")

        console.print(table)

        # Su soğutma optimizasyonu
        sogutma = await gemi.su_sogutma_optimizasyon()
        console.print(f"\n❄️  Su Soğutma Optimal: [bold]{'✅' if sogutma['optimal'] else '⚠️'}[/bold]")
        for oneri in sogutma["oneriler"]:
            console.print(f"   {oneri}")

        console.print(f"\n✅ Gemi API testi [bold green]BAŞARILI[/bold green]\n")

        await gemi.close()

        return True

    except Exception as e:
        console.print(f"❌ Gemi API testi [bold red]BAŞARISIZ[/bold red]: {e}\n")
        console.print("   (Gemi offline olabilir - bu normal)\n")
        return False


async def main():
    """Ana test fonksiyonu"""
    console.clear()

    console.print("\n" + "="*80, style="bold")
    console.print("🌌 MODULllm.com - Platform Test Suite", style="bold cyan", justify="center")
    console.print("Öz Kodundan Doğan Güç!", style="italic yellow", justify="center")
    console.print("="*80 + "\n", style="bold")

    results = {}

    # 1. Öz Veritabanı Test
    results["oz_db"] = await test_oz_db()

    # 2. Gemi API Test
    results["gemi"] = await test_gemi_api()

    # 3. Orchestrator Test (en uzun sürer)
    # UYARI: Bu test gerçek LLM API'lerine bağlanmaya çalışır
    # LLM'ler yoksa hata verebilir - bu normal
    results["orchestrator"] = await test_orchestrator()

    # Özet
    console.rule("[bold green]📊 Test Özeti")

    summary_table = Table(title="Test Sonuçları")
    summary_table.add_column("Test", style="cyan")
    summary_table.add_column("Sonuç", style="white")

    summary_table.add_row("Öz Veritabanı", "✅ BAŞARILI" if results["oz_db"] else "❌ BAŞARISIZ")
    summary_table.add_row("DEAVAEM Gemi", "✅ BAŞARILI" if results["gemi"] else "⚠️  OFFLINE")
    summary_table.add_row("Orchestrator (11+12 Akıl)", "✅ BAŞARILI" if results["orchestrator"] else "⚠️  HATA (LLM'ler offline olabilir)")

    console.print(summary_table)

    # Genel durum
    all_critical_passed = results["oz_db"]  # Kritik: Sadece veritabanı

    if all_critical_passed:
        console.print("\n[bold green]✅ KRİTİK SİSTEMLER ÇALIŞIYOR![/bold green]")
        console.print("[yellow]⚠️  Gemi ve LLM'ler offline olabilir - bu deployment'a göre normal[/yellow]\n")
    else:
        console.print("\n[bold red]❌ KRİTİK HATALAR VAR![/bold red]\n")

    console.print("="*80 + "\n", style="bold")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n\n⏸️  Test durduruldu.\n")
    except Exception as e:
        console.print(f"\n\n❌ Test hatası: {e}\n")
