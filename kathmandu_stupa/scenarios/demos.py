"""
🎬 DEMOS - Demonstrasyon Senaryoları
====================================

Hazır kullanımlık demo fonksiyonları.
"""

import asyncio
from datetime import datetime
from typing import Optional

from .sample_data import (
    get_sample_query,
    get_sample_content_for_fold,
    SAMPLE_CED_DATA,
    LEGENDS,
)


async def run_full_demo(verbose: bool = True):
    """
    Tam demo - tüm katmanları göster.

    1. Stupa tam yolculuğu
    2. Konsey kararı
    3. Storage işlemleri
    4. Kehanet oluşturma
    """
    from ..core.stupa_engine import DataStupa
    from ..clients.orchestrator import create_council
    from ..storage.pilgrimage_store import create_store
    from ..monitoring.logger import get_logger

    log = get_logger()

    print("=" * 70)
    print("🛕 KATHMANDU STUPA - TAM DEMO")
    print("=" * 70)

    # 1. Stupa Yolculuğu
    log.stupa("Tam hac yolculuğu başlıyor...")
    stupa = DataStupa()

    try:
        nirvana_packets = await stupa.full_pilgrimage()
        log.stupa(f"Yolculuk tamamlandı! {len(nirvana_packets)} nirvana")
    except Exception as e:
        log.error(f"Yolculuk hatası: {e}")
        nirvana_packets = []

    # 2. Konsey Kararı
    print("\n" + "-" * 50)
    log.council("7 LLM Konseyi toplanıyor...")

    council = create_council(mock=True)
    query = get_sample_query()

    decision = await council.council_decision(query)
    log.council(f"Karar verildi! Kazanan: {decision.winning_response.metadata.get('monk')}")

    if verbose:
        print(f"\n📜 Sorgu: {query}")
        print(f"🏆 Kazanan: {decision.winning_response.metadata.get('monk')}")
        print(f"📊 Konsensüs: {decision.consensus_score:.2%}")
        print(f"💬 Bilgelik: {decision.wisdom[:200]}...")

    # 3. Storage
    print("\n" + "-" * 50)
    log.stupa("Veriler arşivleniyor...")

    store = create_store(use_sqlite=False, base_path="./demo_data")

    for packet in nirvana_packets[:3]:
        await store.save_nirvana(
            wisdom=packet.final_wisdom,
            frequency_hz=packet.frequency.value,
            confidence=packet.confidence,
            source_chain=packet.source_chain,
        )

    stats = await store.get_statistics()
    log.stupa(f"Arşiv durumu: {stats['total_nirvana']} nirvana kaydedildi")

    # 4. Kehanet
    print("\n" + "-" * 50)
    legend = LEGENDS[0]
    log.eter(f"{legend['name']} ({legend['title']}) kehanet veriyor...")

    prophecy_id = await store.save_prophecy(
        title="2025 Sanayi Vizyonu",
        wisdom=decision.wisdom,
        legend_name=legend["name"],
    )
    log.eter(f"Kehanet kaydedildi: {prophecy_id}")

    # Özet
    print("\n" + "=" * 70)
    print("📊 DEMO ÖZETİ")
    print("=" * 70)

    summary = stupa.get_journey_summary()
    print(f"   Paketler işlendi: {summary['metrics']['packets_processed']}")
    print(f"   Tokenlar temizlendi: {summary['metrics']['tokens_cleaned']}")
    print(f"   Katlamalar: {summary['metrics']['folds_performed']}")
    print(f"   Nirvanalar: {summary['metrics']['nirvana_achieved']}")
    print(f"   Süre: {summary['metrics']['duration_seconds']:.2f} saniye")

    return {
        "nirvana_packets": nirvana_packets,
        "council_decision": decision,
        "storage_stats": stats,
    }


async def run_quick_demo():
    """
    Hızlı demo - tek dua çarkı döngüsü.
    """
    from ..core.stupa_engine import DataStupa

    print("=" * 50)
    print("🛕 HIZLI DEMO - Tek Dua Çarkı")
    print("=" * 50)

    stupa = DataStupa()
    content = get_sample_content_for_fold()

    print(f"\n📄 Giriş: {content[:80]}...")

    nirvana = await stupa.prayer_wheel_spin(content)

    print("\n" + nirvana.to_prophetic_format())

    return nirvana


async def run_council_demo(query: Optional[str] = None, num_monks: int = 5):
    """
    Konsey demo - LLM oylama sistemi.
    """
    from ..clients.orchestrator import MonkOrchestrator, VotingMethod

    print("=" * 50)
    print("🎭 KONSEY DEMO - LLM Oylama")
    print("=" * 50)

    query = query or get_sample_query()
    print(f"\n📝 Sorgu: {query}")

    council = MonkOrchestrator(
        voting_method=VotingMethod.WEIGHTED
    )

    print(f"\n🧘 Aktif Rahipler: {list(council.clients.keys())}")
    print("   Karar bekleniyor...")

    decision = await council.council_decision(query)

    print("\n📊 SONUÇLAR")
    print("-" * 40)
    print(f"🏆 Kazanan: {decision.winning_response.metadata.get('monk')}")
    print(f"📈 Konsensüs: {decision.consensus_score:.2%}")
    print(f"\n📊 Oy Dağılımı:")
    for monk, score in sorted(decision.vote_breakdown.items(), key=lambda x: -x[1]):
        bar = "█" * int(score * 20)
        print(f"   {monk:12} {bar} {score:.2f}")

    print(f"\n💬 Bilgelik:")
    print(f"   {decision.wisdom[:300]}...")

    return decision


async def run_storage_demo():
    """
    Storage demo - veri kalıcılığı.
    """
    from ..storage.pilgrimage_store import create_store

    print("=" * 50)
    print("💾 STORAGE DEMO - Veri Kalıcılığı")
    print("=" * 50)

    # JSON storage
    json_store = create_store(use_sqlite=False, base_path="./demo_json")

    # SQLite storage
    sqlite_store = create_store(use_sqlite=True, base_path="./demo_sqlite")

    # Test verileri
    test_nirvanas = [
        ("Dijitalleşme Türkiye'nin geleceğidir", 963, 0.92),
        ("Yeşil dönüşüm kaçınılmaz bir süreç", 852, 0.88),
        ("İnovasyon rekabet gücünün anahtarı", 741, 0.85),
    ]

    print("\n📁 JSON Storage:")
    for wisdom, freq, conf in test_nirvanas:
        nid = await json_store.save_nirvana(
            wisdom=wisdom,
            frequency_hz=freq,
            confidence=conf,
            source_chain=["DEMO"],
        )
        print(f"   ✅ {nid}")

    print("\n🗄️ SQLite Storage:")
    for wisdom, freq, conf in test_nirvanas:
        nid = await sqlite_store.save_nirvana(
            wisdom=wisdom,
            frequency_hz=freq,
            confidence=conf,
            source_chain=["DEMO"],
        )
        print(f"   ✅ {nid}")

    # İstatistikler
    json_stats = await json_store.get_statistics()
    sqlite_stats = await sqlite_store.get_statistics()

    print("\n📊 JSON İstatistikleri:")
    print(f"   Nirvana: {json_stats['total_nirvana']}")

    print("\n📊 SQLite İstatistikleri:")
    print(f"   Nirvana: {sqlite_stats['total_nirvana']}")

    return {"json": json_stats, "sqlite": sqlite_stats}


async def run_api_demo():
    """
    API demo - server'a istek gönder.

    Not: Önce server'ın çalışıyor olması gerekir.
    """
    try:
        import aiohttp
    except ImportError:
        print("❌ aiohttp yüklü değil")
        return

    print("=" * 50)
    print("🌐 API DEMO")
    print("=" * 50)

    base_url = "http://localhost:8000"

    async with aiohttp.ClientSession() as session:
        # Health check
        try:
            async with session.get(f"{base_url}/health") as resp:
                data = await resp.json()
                print(f"✅ API durumu: {data['status']}")
        except Exception as e:
            print(f"❌ API'ye bağlanılamadı: {e}")
            print("   Önce server'ı başlatın: python -m kathmandu_stupa.api.server")
            return

        # Status
        async with session.get(f"{base_url}/status") as resp:
            status = await resp.json()
            print(f"📊 Stupa durumu: {status['status']}")

        # Council decision
        query = get_sample_query()
        async with session.post(
            f"{base_url}/council",
            json={"query": query}
        ) as resp:
            decision = await resp.json()
            print(f"🎭 Konsey kararı: {decision['winning_monk']}")
            print(f"   Konsensüs: {decision['consensus_score']:.2%}")


# Ana demo runner
async def main():
    """Tüm demoları çalıştır"""
    import sys

    demos = {
        "full": run_full_demo,
        "quick": run_quick_demo,
        "council": run_council_demo,
        "storage": run_storage_demo,
    }

    demo_name = sys.argv[1] if len(sys.argv) > 1 else "quick"

    if demo_name in demos:
        await demos[demo_name]()
    else:
        print(f"Mevcut demolar: {list(demos.keys())}")


if __name__ == "__main__":
    asyncio.run(main())
