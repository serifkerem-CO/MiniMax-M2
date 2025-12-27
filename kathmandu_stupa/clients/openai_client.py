"""
🧘 GPT CLIENT - Yaratıcılık Rahibi
==================================

OpenAI GPT API entegrasyonu.
Domain: Yaratıcı çözümler ve alternatif senaryolar.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from .base import BaseLLMClient, LLMConfig, LLMResponse, MockMode

# Opsiyonel import
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


class GPTClient(BaseLLMClient):
    """
    🧘 GPT Rahibi - Yaratıcılık Ustası

    "Yaratıcı boyutu katladım."

    Alternatif senaryolar ve out-of-box düşünce.
    """

    MONK_NAME = "GPT"
    MONK_DOMAIN = "creativity"
    MONK_MANTRA = "Yaratıcı boyutu katladım"
    DEFAULT_MODEL = "gpt-4-turbo"

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)

        self.api_key = self.config.api_key or os.getenv("OPENAI_API_KEY")

        if HAS_OPENAI and self.api_key:
            self.client = openai.AsyncOpenAI(api_key=self.api_key)
        else:
            self.client = None
            if self.config.mock_mode == MockMode.DISABLED:
                self.config.mock_mode = MockMode.ENABLED

    async def _call_api(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """OpenAI API çağrısı"""
        if not self.client:
            return self._generate_mock_response(messages, **kwargs)

        model = kwargs.get("model", self.config.model or self.DEFAULT_MODEL)

        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                temperature=kwargs.get("temperature", self.config.temperature),
                top_p=kwargs.get("top_p", self.config.top_p),
            )

            choice = response.choices[0]
            content = choice.message.content or ""

            return LLMResponse(
                id=response.id,
                model=response.model,
                content=content,
                finish_reason=choice.finish_reason or "stop",
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                is_mock=False,
                metadata={"provider": "openai", "monk": self.MONK_NAME},
            )

        except Exception as e:
            if self.config.mock_mode == MockMode.FALLBACK:
                self._errors.append(f"GPT API error: {e}")
                return self._generate_mock_response(messages, **kwargs)
            raise

    async def brainstorm(self, topic: str, num_ideas: int = 5) -> LLMResponse:
        """
        Beyin fırtınası - özel metod.

        Verilen konu için yaratıcı fikirler üretir.
        """
        system = f"""Sen yaratıcı bir düşünür ve inovasyon uzmanısın.
Verilen konu için {num_ideas} farklı ve yaratıcı fikir/senaryo üret.
Her fikir için kısa açıklama ve potansiyel etki belirt.
Türkçe yanıt ver."""

        return await self.generate(
            prompt=f"Bu konu için yaratıcı fikirler üret:\n\n{topic}",
            system=system,
        )


# Kısa yol factory
def create_gpt_client(
    api_key: Optional[str] = None,
    mock: bool = False
) -> GPTClient:
    """GPT client oluştur"""
    config = LLMConfig(
        api_key=api_key,
        mock_mode=MockMode.ENABLED if mock else MockMode.FALLBACK,
    )
    return GPTClient(config)
