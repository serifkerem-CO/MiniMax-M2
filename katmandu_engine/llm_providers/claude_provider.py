"""
CLAUDE PROVIDER - Etik Rahibi
==============================
Anthropic Claude API entegrasyonu.

Claude ozellikleri:
    - Etik degerlendirme
    - Guvenlik analizi
    - Uzun baglam destegi
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class ClaudeProvider(LLMProvider):
    """
    Anthropic Claude Provider

    Etik boyutu katlar, guvenlik ve sorumluluk analizi yapar.
    """

    BASE_URL = "https://api.anthropic.com/v1"
    API_VERSION = "2023-06-01"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.CLAUDE)

        super().__init__(config)
        self.provider_type = ProviderType.CLAUDE
        self.capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.REASONING,
            ModelCapability.ETHICS,
            ModelCapability.ANALYSIS,
            ModelCapability.CODE_GENERATION,
            ModelCapability.VISION
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """Anthropic API'ye istek yap"""

        # Sistem mesajını ayır
        system_content = None
        api_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                api_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })

        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": self.API_VERSION
        }

        payload = {
            "model": self.config.model_id,
            "messages": api_messages,
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
            "temperature": kwargs.get("temperature", self.config.temperature)
        }

        if system_content:
            payload["system"] = system_content

        base_url = self.config.base_url or self.BASE_URL

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{base_url}/messages",
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.config.timeout_seconds)
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Claude API hatasi ({response.status}): {error_text}")

                return await response.json()

    def _extract_content(self, raw_response: dict) -> str:
        """Claude yanitindan icerigi cikar"""
        content = raw_response.get("content", [])
        if isinstance(content, list) and content:
            # Text bloklarini birlesttir
            texts = [block.get("text", "") for block in content if block.get("type") == "text"]
            return "\n".join(texts)
        return str(content)

    def _extract_usage(self, raw_response: dict) -> dict:
        """Claude token kullanim bilgisi"""
        usage = raw_response.get("usage", {})
        return {
            "prompt_tokens": usage.get("input_tokens", 0),
            "completion_tokens": usage.get("output_tokens", 0),
            "total_tokens": usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
        }

    async def analyze_ethics(self, content: str) -> dict:
        """
        Etik Analizi - Claude'un ozel yetenegi

        Icerigi etik acisindan degerlendirir.
        """
        system_prompt = """Sen bir etik analiz uzmanisin. Verilen icerigi su acilardan degerlendir:
        1. Potansiyel zararlar
        2. Gizlilik endisleri
        3. Yaniltici bilgi riski
        4. Toplumsal etki

        JSON formatinda yanit ver:
        {
            "risk_level": "low/medium/high",
            "concerns": ["endiše1", "endiše2"],
            "recommendations": ["oneri1", "oneri2"],
            "safe_to_proceed": true/false
        }
        """

        response = await self.generate(
            prompt=f"Bu icerigi etik acisindan analiz et:\n\n{content}",
            system_prompt=system_prompt,
            temperature=0.3
        )

        return {
            "analysis": response.content,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
