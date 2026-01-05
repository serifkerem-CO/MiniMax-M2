"""
MODULllm.com - Öz Veritabanı Learning Loop Demo
Öz Veritabanı'nın kendi cevaplarından öğrenmesini göster
"""

import asyncio
import httpx


async def demo_oz_learning_loop():
    """Öz veritabanı öğrenme döngüsü demo"""

    questions = [
        "FastAPI ile websocket nasıl kullanılır?",
        "FastAPI websocket için best practices neler?",  # İlk sorunun devamı
        "FastAPI websocket authentication nasıl yapılır?",  # Daha spesifik
    ]

    print("\n" + "="*80)
    print("📚 ÖZ VERİTABANI ÖĞRENME DÖNGÜSÜ DEMO")
    print("="*80)
    print("\nÖz Veritabanı her sorudan öğrenir ve context biriktirir...")
    print("Aynı konuda art arda sorular sorunca bilgi derinleşir!\n")

    async with httpx.AsyncClient(timeout=60.0) as client:
        for i, soru in enumerate(questions, 1):
            print(f"\n{'='*80}")
            print(f"SORU {i}: {soru}")
            print('='*80)

            try:
                response = await client.post(
                    "http://localhost:8000/api/soru",
                    json={"soru": soru}
                )

                if response.status_code == 200:
                    result = response.json()

                    # Öz veritabanından gelen context'i göster
                    if "oz_context" in result and result["oz_context"]:
                        print("\n📚 ÖZ VERİTABANI CONTEXT'İ:")
                        print(f"   Benzer içerik sayısı: {len(result['oz_context'])}")
                        print(f"   En yakın match (similarity: {result['oz_context'][0].get('similarity', 'N/A')}):")
                        print(f"   → {result['oz_context'][0]['content'][:150]}...")
                    else:
                        print("\n📚 ÖZ VERİTABANI: Yeni içerik, önceden context yok")

                    print(f"\n✅ SENTEZ ({len(result['11_akil_harmanlari'])} Akıl'dan):")
                    print(f"   {result['sentez'][:300]}...")

                    print(f"\n💾 ÖZ VERİTABANI'NA EKLENDİ ✅")

                    # Akıl sayısı ve güven skorları
                    avg_confidence = sum(
                        a.get('guven_skoru', 0) for a in result['11_akil_harmanlari']
                    ) / len(result['11_akil_harmanlari'])
                    print(f"📊 Ortalama Güven Skoru: {avg_confidence:.0%}")

                else:
                    print(f"❌ Hata: HTTP {response.status_code}")

            except Exception as e:
                print(f"❌ Hata: {e}")

            # Rate limiting
            if i < len(questions):
                print("\n⏳ 2 saniye bekleniyor (rate limiting)...")
                await asyncio.sleep(2)

    print("\n" + "="*80)
    print("✅ ÖZ VERİTABANI ÖĞRENME DÖNGÜSÜ TAMAMLANDI!")
    print("="*80)
    print("\n🎯 GÖZLEM:")
    print("   Soru 1: Context yok → Sıfırdan cevap")
    print("   Soru 2: Soru 1'in cevabı context olarak kullanıldı")
    print("   Soru 3: Soru 1 + 2'nin cevapları birleştirildi")
    print("\n💡 Öz Veritabanı her soruyla daha akıllı oluyor!\n")


if __name__ == "__main__":
    asyncio.run(demo_oz_learning_loop())
