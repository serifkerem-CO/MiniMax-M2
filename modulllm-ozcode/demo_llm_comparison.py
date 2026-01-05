"""
MODULllm.com - LLM Performance Comparison Demo
Aynı soruyu farklı yöntemlerle sor, performans karşılaştır
"""

import asyncio
import httpx
import time
from typing import Dict, Any


async def benchmark_llms():
    """LLM benchmark demo"""

    soru = "React hooks nedir, kısaca açıkla (3-4 cümle)"

    print("\n🏎️  LLM PERFORMANS KARŞILAŞTIRMASI")
    print("="*80)
    print(f"Test Sorusu: {soru}\n")

    results = {}

    # Test 1: n8n ile (paralel, tüm LLM'ler)
    print("Test 1: n8n ile 111 Akıl (5 LLM paralel)...")
    try:
        start_n8n = time.time()
        async with httpx.AsyncClient(timeout=90.0) as client:
            n8n_response = await client.post(
                "http://localhost:5678/webhook/111-akil",
                json={"soru": soru}
            )
            n8n_time = time.time() - start_n8n

            if n8n_response.status_code == 200:
                n8n_result = n8n_response.json()
                results['n8n'] = {
                    'time': n8n_time,
                    'result': n8n_result,
                    'status': 'success'
                }
                print(f"✅ Tamamlandı: {n8n_time:.2f}s\n")
            else:
                results['n8n'] = {'time': 0, 'status': 'error', 'error': f"HTTP {n8n_response.status_code}"}
                print(f"❌ Hata: HTTP {n8n_response.status_code}\n")

    except httpx.ConnectError:
        results['n8n'] = {'time': 0, 'status': 'offline'}
        print(f"❌ n8n offline (http://localhost:5678)\n")
    except Exception as e:
        results['n8n'] = {'time': 0, 'status': 'error', 'error': str(e)}
        print(f"❌ Hata: {e}\n")

    # Test 2: Platform API ile (11 Akıl sistem)
    print("Test 2: MODULllm Platform (11 Akıl)...")
    try:
        start_platform = time.time()
        async with httpx.AsyncClient(timeout=90.0) as client:
            platform_response = await client.post(
                "http://localhost:8000/api/soru",
                json={"soru": soru}
            )
            platform_time = time.time() - start_platform

            if platform_response.status_code == 200:
                platform_result = platform_response.json()
                results['platform'] = {
                    'time': platform_time,
                    'result': platform_result,
                    'status': 'success'
                }
                print(f"✅ Tamamlandı: {platform_time:.2f}s\n")
            else:
                results['platform'] = {'time': 0, 'status': 'error', 'error': f"HTTP {platform_response.status_code}"}
                print(f"❌ Hata: HTTP {platform_response.status_code}\n")

    except httpx.ConnectError:
        results['platform'] = {'time': 0, 'status': 'offline'}
        print(f"❌ Platform offline (http://localhost:8000)\n")
    except Exception as e:
        results['platform'] = {'time': 0, 'status': 'error', 'error': str(e)}
        print(f"❌ Hata: {e}\n")

    # Karşılaştırma
    print("\n" + "="*80)
    print("📊 PERFORMANS ÖZET:")
    print("="*80)

    if results.get('n8n', {}).get('status') == 'success':
        print(f"\n✅ n8n (5 LLM paralel): {results['n8n']['time']:.2f}s")
        n8n_data = results['n8n']['result']
        if 'perspectives' in n8n_data:
            perspectives = n8n_data['perspectives']
            print(f"   - Gemini Ultra: {perspectives.get('gemini_creative', 'N/A')[:80]}...")
            print(f"   - GPT-4: {perspectives.get('gpt4_analytical', 'N/A')[:80]}...")
            print(f"   - Claude: {perspectives.get('claude_strategic', 'N/A')[:80]}...")
            print(f"   - MiniMax: {perspectives.get('minimax_technical', 'N/A')[:80]}...")
            print(f"   - Llama: {perspectives.get('llama_pragmatic', 'N/A')[:80]}...")
    else:
        print(f"\n❌ n8n: {results.get('n8n', {}).get('status', 'unknown')}")

    if results.get('platform', {}).get('status') == 'success':
        print(f"\n✅ MODULllm Platform (11 Akıl): {results['platform']['time']:.2f}s")
        platform_data = results['platform']['result']
        print(f"   - Sentez: {platform_data.get('sentez', 'N/A')[:150]}...")
        print(f"   - Perspektif sayısı: {len(platform_data.get('11_akil_harmanlari', []))}")
    else:
        print(f"\n❌ Platform: {results.get('platform', {}).get('status', 'unknown')}")

    # Sonuç analizi
    print("\n" + "="*80)
    print("💡 DEĞERLENDİRME:")
    print("="*80)

    successful_tests = [k for k, v in results.items() if v.get('status') == 'success']

    if successful_tests:
        # En hızlı bul
        fastest = min(
            [(k, v['time']) for k, v in results.items() if v.get('status') == 'success'],
            key=lambda x: x[1]
        )
        print(f"\n🏆 En Hızlı: {fastest[0].upper()} ({fastest[1]:.2f}s)")

        # Öneriler
        print("\n📌 KULLANIM ÖNERİLERİ:")
        print("   - Basit sorular: Tek LLM (hızlı, ekonomik)")
        print("   - Orta seviye: Platform 11 Akıl (dengeli)")
        print("   - Kritik kararlar: n8n 111 Akıl (en kapsamlı, 5 farklı LLM)")
        print("   - Maliyet hassas: Local Llama ile başla, gerektiğinde cloud LLM")
    else:
        print("\n⚠️  Hiçbir test başarılı olamadı!")
        print("   Çözüm: ./modulllm-ozcode/deploy_everything.sh çalıştır")

    print("\n" + "="*80)


if __name__ == "__main__":
    asyncio.run(benchmark_llms())
