"""
MINIMAX PROVIDER - Sentez Rahibi
=================================
MiniMax API entegrasyonu.

MiniMax ozellikleri:
    - Sentez ve birlestirme
    - Coklu kaynak fuzyonu
    - Ozetleme ve sonuclama
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class MiniMaxProvider(LLMProvider):
    """
    MiniMax Provider

    Sentez boyutunu katlar, farkli kaynaklari birlestirir.
    """

    BASE_URL = "https://api.minimax.chat/v1"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.MINIMAX)

        super().__init__(config)
        self.provider_type = ProviderType.MINIMAX
        self.capabilities = [
            ModelCapability.SYNTHESIS,
            ModelCapability.TEXT_GENERATION,
            ModelCapability.ANALYSIS,
            ModelCapability.REASONING
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """MiniMax API'ye istek yap (OpenAI uyumlu)"""

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
                    raise Exception(f"MiniMax API hatasi ({response.status}): {error_text}")

                return await response.json()

    async def synthesize(self, sources: list[str]) -> dict:
        """
        Sentez - MiniMax'in ozel yetenegi

        Birden fazla kaynagi sentezleyip birlestir.
        """
        system_prompt = """Sen bir sentez uzmanisin.
        Verilen kaynaklari:
        1. Ortak noktalarini bul
        2. Celiskileri tespit et
        3. Tamamlayici bilgileri birлестir
        4. Tutarli bir butun olustur
        5. Ana mesaji cikar

        Kaynaklari birlestirip tutarli bir sonuc olustur.
        """

        combined_sources = "\n\n---\n\n".join([
            f"Kaynak {i+1}:\n{source}"
            for i, source in enumerate(sources)
        ])

        response = await self.generate(
            prompt=f"Bu kaynaklari sentezle:\n\n{combined_sources}",
            system_prompt=system_prompt,
            temperature=0.5
        )

        return {
            "synthesis": response.content,
            "source_count": len(sources),
            "success": response.success,
            "latency_ms": response.latency_ms
        }

    async def summarize_consensus(self, responses: list[dict]) -> dict:
        """
        Konsensus Ozeti

        Birden fazla LLM yanitini ozetler.
        """
        system_prompt = """Sen bir konsensus analisti sin.
        Farkli kaynaklardan gelen yanitlari analiz et:
        1. Ortak gorusleri belirle
        2. Farkli perspektifleri not et
        3. Guvenilirlik degerlendir
        4. Sentezlenmis bir sonuc olustur

        JSON formatinda konsensus raporu olustur.
        """

        responses_text = "\n\n".join([
            f"[{r.get('provider', 'Unknown')}]: {r.get('content', '')}"
            for r in responses
        ])

        response = await self.generate(
            prompt=f"Bu LLM yanitlarindan konsensus cikar:\n\n{responses_text}",
            system_prompt=system_prompt,
            temperature=0.4
        )

        return {
            "consensus": response.content,
            "response_count": len(responses),
            "success": response.success,
            "latency_ms": response.latency_ms
        }
