"""
DEEPSEEK PROVIDER - Kod Rahibi
===============================
DeepSeek API entegrasyonu.

DeepSeek ozellikleri:
    - Kod uretimi ve analizi
    - Teknik dokumantasyon
    - Problem cozme
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class DeepSeekProvider(LLMProvider):
    """
    DeepSeek Provider

    Kod boyutunu katlar, teknik analiz ve kod uretimi yapar.
    """

    BASE_URL = "https://api.deepseek.com/v1"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.DEEPSEEK)

        super().__init__(config)
        self.provider_type = ProviderType.DEEPSEEK
        self.capabilities = [
            ModelCapability.CODE_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.ANALYSIS,
            ModelCapability.TEXT_GENERATION
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """DeepSeek API'ye istek yap (OpenAI uyumlu)"""

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
                    raise Exception(f"DeepSeek API hatasi ({response.status}): {error_text}")

                return await response.json()

    async def code_analysis(self, code: str, language: str = "python") -> dict:
        """
        Kod Analizi - DeepSeek'in ozel yetenegi

        Kodu analiz eder ve iyilestirme onerileri sunar.
        """
        system_prompt = f"""Sen bir {language} kod analiz uzmanisin.
        Verilen kodu su acılardan analiz et:
        1. Kod kalitesi
        2. Performans
        3. Guvenlik açıkları
        4. Best practices uyumu
        5. Iyilestirme onerileri

        Teknik ve detayli bir analiz sun.
        """

        response = await self.generate(
            prompt=f"Bu {language} kodunu analiz et:\n\n```{language}\n{code}\n```",
            system_prompt=system_prompt,
            temperature=0.2
        )

        return {
            "code_analysis": response.content,
            "language": language,
            "success": response.success,
            "latency_ms": response.latency_ms
        }

    async def generate_code(
        self,
        description: str,
        language: str = "python"
    ) -> dict:
        """
        Kod Uretimi

        Aciklamadan kod uretir.
        """
        system_prompt = f"""Sen bir {language} kod uretim uzmanisin.
        Verilen aciklamaya gore temiz, verimli ve iyi dokumante edilmis kod yaz.
        Kod bloklarini ``` ile isaretле.
        """

        response = await self.generate(
            prompt=f"Su islevselligi {language} ile implement et:\n\n{description}",
            system_prompt=system_prompt,
            temperature=0.3
        )

        return {
            "generated_code": response.content,
            "language": language,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
