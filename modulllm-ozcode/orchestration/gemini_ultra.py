"""
MODULllm.com - Gemini Ultra Integration
111 Akıl Sistemi: Gemini Ultra + 11 Akıl Harmanları
"""

import asyncio
import httpx
from typing import List, Dict, Any, Optional
from enum import Enum


class GeminiModel(str, Enum):
    """Gemini modelleri"""
    ULTRA = "gemini-ultra"
    PRO = "gemini-pro"
    PRO_VISION = "gemini-pro-vision"


class GeminiUltraClient:
    """
    Gemini Ultra AI Client

    Google'ın en güçlü modeli ile MODULllm.com entegrasyonu
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.client = httpx.AsyncClient(timeout=60)

    async def generate(
        self,
        prompt: str,
        model: GeminiModel = GeminiModel.ULTRA,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> Dict[str, Any]:
        """
        Gemini Ultra ile content generation
        """
        url = f"{self.base_url}/models/{model.value}:generateContent"

        # Request body
        contents = []

        # System instruction (Gemini'de system message parts olarak gönderilir)
        if system_instruction:
            contents.append({
                "role": "user",
                "parts": [{"text": f"[SYSTEM]: {system_instruction}"}]
            })

        # Main prompt
        contents.append({
            "role": "user",
            "parts": [{"text": prompt}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.95,
                "topK": 40
            },
            "safetySettings": [
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_NONE"
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                    "threshold": "BLOCK_NONE"
                }
            ]
        }

        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
            )

            response.raise_for_status()
            result = response.json()

            # Extract text from response
            text = result["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "success": True,
                "text": text,
                "model": model.value,
                "usage": {
                    "prompt_tokens": result.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "completion_tokens": result.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    "total_tokens": result.get("usageMetadata", {}).get("totalTokenCount", 0)
                }
            }

        except httpx.HTTPStatusError as e:
            return {
                "success": False,
                "error": f"HTTP {e.response.status_code}: {e.response.text}",
                "model": model.value
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": model.value
            }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: GeminiModel = GeminiModel.ULTRA,
        temperature: float = 0.7
    ) -> Dict[str, Any]:
        """
        Multi-turn conversation

        messages format:
        [
            {"role": "user", "content": "Merhaba"},
            {"role": "assistant", "content": "Merhaba! Nasıl yardımcı olabilirim?"},
            {"role": "user", "content": "MODULllm nedir?"}
        ]
        """
        url = f"{self.base_url}/models/{model.value}:generateContent"

        # Convert to Gemini format
        contents = []
        for msg in messages:
            role = "model" if msg["role"] == "assistant" else "user"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": 8192
            }
        }

        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
            )

            response.raise_for_status()
            result = response.json()

            text = result["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "success": True,
                "text": text,
                "model": model.value
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def vision(
        self,
        prompt: str,
        image_data: str,  # base64 encoded image
        mime_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        Gemini Pro Vision - image understanding
        """
        url = f"{self.base_url}/models/{GeminiModel.PRO_VISION.value}:generateContent"

        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": image_data
                        }
                    }
                ]
            }]
        }

        try:
            response = await self.client.post(
                url,
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-goog-api-key": self.api_key
                }
            )

            response.raise_for_status()
            result = response.json()

            text = result["candidates"][0]["content"]["parts"][0]["text"]

            return {
                "success": True,
                "text": text,
                "model": GeminiModel.PRO_VISION.value
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Integration with 111 Akıl Sistemi
class AkillarWithGemini:
    """
    111 Akıl Sistemi

    11 Akıl (Original) + Gemini Ultra (100 perspektif) = 111 Akıl!
    """

    def __init__(
        self,
        gemini_api_key: str,
        original_orchestrator=None
    ):
        self.gemini = GeminiUltraClient(gemini_api_key)
        self.original_orchestrator = original_orchestrator

    async def get_gemini_perspectives(
        self,
        soru: str,
        oz_context: str
    ) -> List[Dict[str, Any]]:
        """
        Gemini Ultra'dan 100 farklı perspektif al
        (Simülasyon: Gerçekte 10-20 özel perspektif yeterli)
        """

        gemini_perspectives = [
            {
                "name": "Global Strategy",
                "prompt": f"Küresel strateji perspektifinden değerlendir:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Scientific Research",
                "prompt": f"Bilimsel araştırma metodolojisiyle yaklaş:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Creative Innovation",
                "prompt": f"Yaratıcı inovasyon açısından bak:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Cultural Synthesis",
                "prompt": f"Kültürlerarası sentez perspektifiyle:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Economic Impact",
                "prompt": f"Ekonomik etki analizi yap:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Ethical Considerations",
                "prompt": f"Etik boyutları değerlendir:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Future Scenarios",
                "prompt": f"Gelecek senaryoları oluştur:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "User Experience",
                "prompt": f"Kullanıcı deneyimi odaklı yaklaş:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Technical Architecture",
                "prompt": f"Teknik mimari perspektifiyle:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            },
            {
                "name": "Sustainability",
                "prompt": f"Sürdürülebilirlik açısından:\n\nKontext: {oz_context}\n\nSoru: {soru}"
            }
        ]

        # Paralel Gemini queries
        tasks = []
        for perspective in gemini_perspectives:
            task = self.gemini.generate(
                prompt=perspective["prompt"],
                system_instruction="Sen MODULllm.com'un Gemini Ultra Akıl'ısın. Derinlemesine analiz yap."
            )
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Format results
        perspectives_data = []
        for i, result in enumerate(results):
            if result["success"]:
                perspectives_data.append({
                    "perspective": gemini_perspectives[i]["name"],
                    "analysis": result["text"],
                    "model": "gemini-ultra",
                    "tokens": result["usage"]["total_tokens"]
                })

        return perspectives_data

    async def ultimate_synthesis(
        self,
        soru: str,
        original_11_akil: List[Dict],
        gemini_perspectives: List[Dict]
    ) -> str:
        """
        Ultimate Sentez: 11 Akıl + Gemini Ultra = 111 Akıl Sentezi!
        """

        # Tüm perspektifleri birleştir
        all_insights = "## 11 AKIL HARMANLARI:\n\n"
        for akil in original_11_akil:
            all_insights += f"### {akil['akil']}:\n{akil['icerik'][:300]}...\n\n"

        all_insights += "\n## GEMİNİ ULTRA PERSPEKTİFLERİ:\n\n"
        for persp in gemini_perspectives:
            all_insights += f"### {persp['perspective']}:\n{persp['analysis'][:300]}...\n\n"

        # Gemini Ultra ile ultimate sentez
        synthesis_prompt = f"""Sen MODULllm.com'un 111. AKL'ısın - ULTIMATE SENTEZ USTASI!

ORİJİNAL SORU:
{soru}

11 AKIL HARMANLAR + GEMİNİ ULTRA PERSPEKTİFLERİ:
{all_insights}

GÖREVİN:
1. Tüm 111 perspektifi harmonize et
2. En değerli içgörüleri çıkar
3. Özgün, kapsamlı, derinlemesine sentez üret
4. Pratik öneriler sun
5. Vizyoner bakış ekle

ULTIMATE SENTEZİNİ OLUŞTUR:"""

        result = await self.gemini.generate(
            prompt=synthesis_prompt,
            temperature=0.8,
            max_tokens=8192
        )

        if result["success"]:
            return result["text"]
        else:
            return f"Sentez hatası: {result['error']}"


# Test
async def test_gemini_ultra():
    """Test Gemini Ultra integration"""

    # API KEY - .env'den al
    import os
    from dotenv import load_dotenv

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ GEMINI_API_KEY bulunamadı! .env dosyasına ekle.")
        return

    print("\n" + "="*80)
    print("🌟 Gemini Ultra Test Başlıyor...")
    print("="*80 + "\n")

    gemini = GeminiUltraClient(api_key)

    # Test 1: Simple generation
    print("📝 Test 1: Simple Generation\n")
    result = await gemini.generate(
        prompt="MODULllm.com nedir? 3 cümlede açıkla.",
        system_instruction="Sen MODULllm.com platformunun Gemini Ultra AI asistanısın."
    )

    if result["success"]:
        print(f"✅ Başarılı!")
        print(f"Model: {result['model']}")
        print(f"Tokens: {result['usage']['total_tokens']}")
        print(f"\nYanıt:\n{result['text']}\n")
    else:
        print(f"❌ Hata: {result['error']}\n")

    # Test 2: Multi-turn chat
    print("\n" + "-"*80)
    print("💬 Test 2: Multi-turn Chat\n")

    messages = [
        {"role": "user", "content": "Merhaba! Ben Şerif."},
        {"role": "assistant", "content": "Merhaba Şerif! MODULllm.com'a hoş geldin!"},
        {"role": "user", "content": "111 Akıl sistemi nasıl çalışır?"}
    ]

    chat_result = await gemini.chat(messages)

    if chat_result["success"]:
        print(f"✅ Chat başarılı!")
        print(f"\nYanıt:\n{chat_result['text']}\n")
    else:
        print(f"❌ Hata: {chat_result['error']}\n")

    await gemini.close()

    print("="*80)
    print("✅ Test tamamlandı!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(test_gemini_ultra())
