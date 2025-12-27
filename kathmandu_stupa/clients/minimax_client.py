"""
🧘 MINIMAX CLIENT - Sentez Rahibi
=================================

MiniMax M2 API entegrasyonu.
Domain: Sentez, birleştirme ve final kararlar.

MiniMax M2: 230B total, 10B active parameters.
Agentic ve coding görevlerinde güçlü.
"""

import asyncio
import os
import aiohttp
from typing import Any, Dict, List, Optional

from .base import BaseLLMClient, LLMConfig, LLMResponse, MockMode


class MiniMaxClient(BaseLLMClient):
    """
    🧘 MiniMax Rahibi - Sentez Ustası

    "Sentezi tamamladım."

    Tüm perspektifleri birleştirip final karar verir.
    Kathmandu Stupa'nın kalbi - yerli teknoloji.
    """

    MONK_NAME = "MiniMax"
    MONK_DOMAIN = "synthesis"
    MONK_MANTRA = "Sentezi tamamladım"
    DEFAULT_MODEL = "MiniMax-M2"
    BASE_URL = "https://api.minimax.chat/v1/text/chatcompletion_v2"

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)

        self.api_key = self.config.api_key or os.getenv("MINIMAX_API_KEY")
        self.group_id = os.getenv("MINIMAX_GROUP_ID", "")

        if not self.api_key and self.config.mock_mode == MockMode.DISABLED:
            self.config.mock_mode = MockMode.ENABLED

    async def _call_api(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """MiniMax API çağrısı"""
        if not self.api_key:
            return self._generate_mock_response(messages, **kwargs)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        # MiniMax format
        payload = {
            "model": kwargs.get("model", self.DEFAULT_MODEL),
            "messages": messages,
            "temperature": kwargs.get("temperature", self.config.temperature),
            "top_p": kwargs.get("top_p", self.config.top_p),
            "max_tokens": kwargs.get("max_tokens", self.config.max_tokens),
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=self.config.timeout)
                ) as response:
                    data = await response.json()

                    if response.status != 200:
                        raise Exception(f"MiniMax API error: {data}")

                    # Yanıtı parse et
                    choice = data.get("choices", [{}])[0]
                    message = choice.get("message", {})
                    content = message.get("content", "")

                    # Think tag'leri koru (MiniMax M2 özelliği)
                    # <think>...</think> formatını sakla

                    usage = data.get("usage", {})

                    return LLMResponse(
                        id=data.get("id", "minimax_response"),
                        model=data.get("model", self.DEFAULT_MODEL),
                        content=content,
                        finish_reason=choice.get("finish_reason", "stop"),
                        usage={
                            "prompt_tokens": usage.get("prompt_tokens", 0),
                            "completion_tokens": usage.get("completion_tokens", 0),
                            "total_tokens": usage.get("total_tokens", 0),
                        },
                        is_mock=False,
                        metadata={
                            "provider": "minimax",
                            "monk": self.MONK_NAME,
                            "has_thinking": "<think>" in content,
                        },
                    )

        except Exception as e:
            if self.config.mock_mode == MockMode.FALLBACK:
                self._errors.append(f"MiniMax API error: {e}")
                return self._generate_mock_response(messages, **kwargs)
            raise

    async def synthesize(self, perspectives: List[str]) -> LLMResponse:
        """
        Sentez - özel metod.

        Birden fazla perspektifi birleştirip tek bir sonuç çıkarır.
        """
        combined = "\n\n".join([
            f"Perspektif {i+1}:\n{p}"
            for i, p in enumerate(perspectives)
        ])

        system = """Sen bir sentez uzmanısın. Birden fazla perspektifi analiz edip
ortak noktaları, farklılıkları ve en güçlü argümanları belirle.
Sonunda tek bir birleşik görüş oluştur.

Format:
1. Ortak Noktalar
2. Farklılıklar
3. Sentez Sonucu
4. Güven Skoru (0-100)"""

        return await self.generate(
            prompt=f"Bu perspektifleri sentezle:\n\n{combined}",
            system=system,
        )

    async def agent_task(self, task: str, tools: Optional[List[Dict]] = None) -> LLMResponse:
        """
        Agent görevi - MiniMax M2'nin güçlü olduğu alan.

        Tool calling ve multi-step reasoning.
        """
        system = """Sen güçlü bir AI agent'ısın. Verilen görevi adım adım çöz.
Düşünce sürecini <think>...</think> içinde paylaş.
Gerekirse araçları kullan."""

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": task},
        ]

        if tools:
            # Tool definitions ekle
            pass  # MiniMax tool format

        return await self.chat(messages)


# Kısa yol factory
def create_minimax_client(
    api_key: Optional[str] = None,
    mock: bool = False
) -> MiniMaxClient:
    """MiniMax client oluştur"""
    config = LLMConfig(
        api_key=api_key,
        mock_mode=MockMode.ENABLED if mock else MockMode.FALLBACK,
    )
    return MiniMaxClient(config)
