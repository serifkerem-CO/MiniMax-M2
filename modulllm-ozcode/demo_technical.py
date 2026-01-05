"""
MODULllm.com - Technical Question Demo
Karmaşık teknik soru ile 111 Akıl sistemini test et
"""

import asyncio
import httpx
import json


async def demo_technical_question():
    """Karmaşık teknik soru demo"""

    soru = """
    Mikroservis mimarisi ile monolitik mimari arasında nasıl seçim yapmalıyım?
    Projem 10,000 günlük aktif kullanıcı için tasarlanıyor.
    Backend: Python FastAPI, Frontend: React, Database: PostgreSQL
    """

    print("\n" + "="*80)
    print("🧠 111 AKIL SİSTEMİ - TEKNİK SORU DEMO")
    print("="*80 + "\n")

    print(f"📝 SORU:\n{soru}\n")
    print("⏳ 11 Akıl Harmanları çalışıyor...\n")

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                "http://localhost:8000/api/soru",
                json={
                    "soru": soru,
                    "context": "startup project, limited budget"
                }
            )

            if response.status_code == 200:
                result = response.json()

                print("🎭 11 AKIL PERSPEKTİFLERİ:\n")

                # İlk 5 Akıl'ı göster
                for i, akil in enumerate(result['11_akil_harmanlari'][:5], 1):
                    print(f"{i}. {akil['akil_tipi']}:")
                    print(f"   {akil['yanit'][:200]}...")
                    print(f"   Güven Skoru: {akil['guven_skoru']:.0%}\n")

                print(f"   ... ve {len(result['11_akil_harmanlari']) - 5} perspektif daha\n")

                print("\n🌟 ULTIMATE SENTEZ (12. Akıl):")
                print("="*80)
                print(result['sentez'])
                print("="*80)

                print(f"\n💾 Öz Veritabanı: {'✅ Eklendi' if result.get('oz_kaydi_eklendi') else '❌ Eklenemedi'}")
                print(f"⚡ Platform: {result.get('platform', 'MODULllm.com')}")

            else:
                print(f"❌ Hata: HTTP {response.status_code}")
                print(f"Response: {response.text}")

    except httpx.ConnectError:
        print("❌ Platform'a bağlanılamıyor!")
        print("   Çözüm: ./modulllm-ozcode/deploy_everything.sh çalıştır")
    except httpx.TimeoutException:
        print("⏰ Timeout! Sorular çok karmaşık olabilir.")
        print("   11 Akıl sistemi tüm perspektifleri değerlendiriyor...")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(demo_technical_question())
