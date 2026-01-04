"""
LLAMA PROVIDER - Bilgelik Rahibi
=================================
Meta Llama API entegrasyonu (Together AI veya Groq uzerinden).

Llama ozellikleri:
    - Acik kaynak bilgeligi
    - Genel amacli yetenekler
    - Topluluk destekli
"""

import aiohttp
from typing import Optional
import os

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class LlamaProvider(LLMProvider):
    """
    Llama Provider (Together AI / Groq)

    Bilgelik boyutunu katlar, butunsel perspektif sunar.
    """

    # Together AI varsayilan
    TOGETHER_URL = "https://api.together.xyz/v1"
    GROQ_URL = "https://api.groq.com/openai/v1"

    def __init__(self, config: Optional[LLMConfig] = None, backend: str = "together"):
        if config is None:
            config = LLMConfig.from_env(ProviderType.LLAMA)

        super().__init__(config)
        self.provider_type = ProviderType.LLAMA
        self.backend = backend
        self.capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.WISDOM,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION
        ]

        # Backend'e gore URL ayarla
        if backend == "groq":
            self.base_url = self.GROQ_URL
            # Groq icin API key kontrolu
            if not config.api_key:
                config.api_key = os.environ.get("GROQ_API_KEY", "")
        else:
            self.base_url = self.TOGETHER_URL

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """Llama API'ye istek yap (OpenAI uyumlu)"""

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }

        payload = {
            "model": self.config.model_id,
            "messages": messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }

        url = self.config.base_url or self.base_url

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Llama API hatasi ({response.status}): {error_text}")

                return await response.json()

    async def holistic_wisdom(self, topic: str) -> dict:
        """
        Butunsel Bilgelik - Llama'nin ozel yetenegi

        Konuyu cok boyutlu perspektiften degerlendirir.
        """
        system_prompt = """Sen bir bilgelik ustasisin.
        Verilen konuyu su perspektiflerden degerlendir:
        1. Tarihsel baglam
        2. Felsefi boyut
        3. Pratik uygulamalar
        4. Gelecek vizyonu
        5. Butunsel sonuc

        Derin ve anlamli icgoruler sun.
        """

        response = await self.generate(
            prompt=f"Bu konu hakkinda butunsel bir degerlendirme yap:\n\n{topic}",
            system_prompt=system_prompt,
            temperature=0.6
        )

        return {
            "wisdom": response.content,
            "topic": topic,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
