"""
OPENAI PROVIDER - Yaraticilik Rahibi
=====================================
OpenAI GPT API entegrasyonu.

GPT ozellikleri:
    - Yaratici icerik uretimi
    - Coklu format destegi
    - Tool/Function calling
"""

import aiohttp
from typing import Optional

from .base import LLMProvider, LLMConfig, ProviderType, ModelCapability


class OpenAIProvider(LLMProvider):
    """
    OpenAI GPT Provider

    Yaraticilik boyutunu katlar, alternatif bakis acilari sunar.
    """

    BASE_URL = "https://api.openai.com/v1"

    def __init__(self, config: Optional[LLMConfig] = None):
        if config is None:
            config = LLMConfig.from_env(ProviderType.OPENAI)

        super().__init__(config)
        self.provider_type = ProviderType.OPENAI
        self.capabilities = [
            ModelCapability.TEXT_GENERATION,
            ModelCapability.CREATIVITY,
            ModelCapability.CODE_GENERATION,
            ModelCapability.TOOL_USE,
            ModelCapability.VISION,
            ModelCapability.REASONING
        ]

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """OpenAI API'ye istek yap"""

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

        # Tool calling destegi
        if "tools" in kwargs:
            payload["tools"] = kwargs["tools"]

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
                    raise Exception(f"OpenAI API hatasi ({response.status}): {error_text}")

                return await response.json()

    async def generate_creative(
        self,
        prompt: str,
        style: str = "professional"
    ) -> dict:
        """
        Yaratici Icerik Uretimi - GPT'nin ozel yetenegi

        Farkli stillerde yaratici icerik uretir.
        """
        style_prompts = {
            "professional": "Profesyonel ve resmi bir tonda yaz.",
            "casual": "Samimi ve gunluk bir dilde yaz.",
            "creative": "Yaratici ve etkileyici bir uslupla yaz.",
            "technical": "Teknik ve detayli bir sekilde acikla.",
            "storytelling": "Hikaye anlatir gibi ilgi cekici yaz."
        }

        system_prompt = f"""Sen yaratici bir icerik uzmanisin.
        {style_prompts.get(style, style_prompts['professional'])}
        Alternatif bakis acilari ve yenilikci fikirler sun.
        """

        response = await self.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=0.8
        )

        return {
            "creative_content": response.content,
            "style": style,
            "success": response.success,
            "latency_ms": response.latency_ms
        }
