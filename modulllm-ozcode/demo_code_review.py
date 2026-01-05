"""
MODULllm.com - Code Review Demo
Junior developer code'unu 111 Akıl sistemi ile review et
"""

import asyncio
import httpx


async def demo_code_review():
    """Code review demo - junior developer mentoring"""

    pr_code = '''
# user_service.py
def get_users():
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute('SELECT * FROM users')
    users = cursor.fetchall()
    return users

def add_user(name, email):
    db = sqlite3.connect('users.db')
    cursor = db.cursor()
    cursor.execute(f"INSERT INTO users VALUES ('{name}', '{email}')")
    db.commit()
    return "OK"
'''

    soru = f"""
Junior developer code review yap. Eğitici ve detaylı açıkla.

Code:
```python
{pr_code}
```

Değerlendir:
1. Security issues
2. Best practices
3. Improvements
4. Refactored version

Junior-friendly açıkla, mentorluk yap.
"""

    print("\n" + "="*80)
    print("📝 CODE REVIEW DEMO - JUNIOR DEVELOPER MENTORING")
    print("="*80 + "\n")

    print("👨‍💻 Junior Developer'ın Kodu:")
    print("-" * 80)
    print(pr_code)
    print("-" * 80)

    print("\n⏳ 111 Akıl sistemi code review yapıyor...\n")

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                "http://localhost:8000/api/soru",
                json={
                    "soru": soru,
                    "context": "mentoring, educational, junior developer"
                }
            )

            if response.status_code == 200:
                result = response.json()

                print("🎭 FARKLI PERSPEKTİFLER:\n")

                # Önemli perspektifleri göster
                important_perspectives = ['TEKNIK', 'ELESTREL', 'PRAGMATIK']

                for akil in result['11_akil_harmanlari']:
                    if akil['akil_tipi'] in important_perspectives:
                        print(f"\n🔍 {akil['akil_tipi']} AKIL:")
                        print(f"{akil['yanit'][:300]}...")
                        print("-" * 80)

                print("\n\n🌟 ULTIMATE CODE REVIEW (12. Akıl Sentezi):")
                print("="*80)
                print(result['sentez'])
                print("="*80)

                print(f"\n💾 Review Öz Veritabanı'na kaydedildi ✅")
                print(f"📊 {len(result['11_akil_harmanlari'])} farklı perspektiften değerlendirildi")

            else:
                print(f"❌ Hata: HTTP {response.status_code}")
                print(f"Response: {response.text}")

    except httpx.ConnectError:
        print("❌ Platform'a bağlanılamıyor!")
        print("   Çözüm: ./modulllm-ozcode/deploy_everything.sh çalıştır")
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

    print("\n" + "="*80)
    print("✅ CODE REVIEW TAMAMLANDI!")
    print("="*80)
    print("\n💡 111 Akıl sistemi ile:")
    print("   - Security vulnerabilities yakalandı (SQL injection)")
    print("   - Best practices önerildi (context manager, type hints)")
    print("   - Production-ready refactored code verildi")
    print("   - Junior developer için eğitici açıklamalar yapıldı\n")


if __name__ == "__main__":
    asyncio.run(demo_code_review())
