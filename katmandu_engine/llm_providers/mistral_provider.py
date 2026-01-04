"""
MISTRAL PROVIDER - Lojistik Rahibi
===================================
Mistral AI API entegrasyonu.

Mistral ozellikleri:
    - Hizli ve verimli islem
    - Yapisal dusunme
    - Kod uretimi
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class MistralProvider(LLMProvider):
    """
    Mistral AI Provider

    Lojistik boyutunu katlar, yapisal ve sistematik analiz yapar.
    """

    BASE_URL = "https://api.mistral.ai/v1"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.MISTRAL)

        super().__init__(config)
        self.provider_type = ProviderType.MISTRAL
        self.capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.CODE_GENERATION,
            ModelCapability.ANALYSIS
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """Mistral API'ye istek yap"""

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

        base_url = self.config.base_url or self.BASE_URL

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Mistral API hatasi ({response.status}): {error_text}")

                return await response.json()

    async def structural_analysis(self, content: str) -> dict:
        """
        Yapisal Analiz - Mistral'in ozel yetenegi

        Icerigin yapisini ve akisini analiz eder.
        """
        system_prompt = """Sen bir yapi ve lojistik analiz uzmanisin.
        Verilen icerigin:
        1. Genel yapisini
        2. Mantiksal akisini
        3. Bagimlilikları
        4. Darbogazlari
        5. Optimizasyon noktalarini

        analiz et ve sistematik bir rapor sun.
        """

        response = await self.generate(
            prompt=f"Bu icerigin yapisini analiz et:\n\n{content}",
            system_prompt=system_prompt,
            temperature=0.3
        )

        return {
            "structural_analysis": response.content,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
