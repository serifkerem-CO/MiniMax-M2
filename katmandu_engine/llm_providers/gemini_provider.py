"""
GEMINI PROVIDER - Analiz Rahibi
================================
Google Gemini API entegrasyonu.

Gemini ozellikleri:
    - Coklu kaynak analizi
    - Uzun baglam isleme
    - Multimodal yetenekler
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class GeminiProvider(LLMProvider):
    """
    Google Gemini Provider

    Analiz boyutunu katlar, derinlemesine ve coklu kaynak analizi yapar.
    """

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.GEMINI)

        super().__init__(config)
        self.provider_type = ProviderType.GEMINI
        self.capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """Gemini API'ye istek yap"""

        # Mesajlari Gemini formatina cevir
        contents = []
        system_instruction = None

        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                role = "user" if msg["role"] == "user" else "model"
                contents.append({
                    "role": role,
                    "parts": [{"text": msg["content"]}]
                })

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": kwargs.get("max_tokens", self.config.max_tokens),
                "temperature": kwargs.get("temperature", self.config.temperature)
            }
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        base_url = self.config.base_url or self.BASE_URL
        model = self.config.model_id

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/models/{model}:generateContent?key={self.config.api_key}",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Gemini API hatasi ({response.status}): {error_text}")

                return await response.json()

    def _extract_content(self, raw_response: dict) -> str:
        """Gemini yanitindan icerigi cikar"""
        candidates = raw_response.get("candidates", [])
        if candidates:
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                return parts[0].get("text", "")
        return ""

    def _extract_usage(self, raw_response: dict) -> dict:
        """Gemini token kullanim bilgisi"""
        usage = raw_response.get("usageMetadata", {})
        return {
            "prompt_tokens": usage.get("promptTokenCount", 0),
            "completion_tokens": usage.get("candidatesTokenCount", 0),
            "total_tokens": usage.get("totalTokenCount", 0)
        }

    async def deep_analyze(self, content: str, aspects: list[str] = None) -> dict:
        """
        Derin Analiz - Gemini'nin ozel yetenegi

        Coklu boyuttan derinlemesine analiz yapar.
        """
        if aspects is None:
            aspects = ["ana tema", "alt temalar", "oruntler", "anomaliler", "oneriler"]

        system_prompt = f"""Sen bir derin analiz uzmanisin.
        Verilen icerigi su boyutlardan analiz et: {', '.join(aspects)}

        Her boyut icin detayli bulgular sun.
        JSON formatinda yapi kullan.
        """

        response = await self.generate(
            prompt=f"Bu icerigi derinlemesine analiz et:\n\n{content}",
            system_prompt=system_prompt,
            temperature=0.4
        )

        return {
            "deep_analysis": response.content,
            "aspects_analyzed": aspects,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
