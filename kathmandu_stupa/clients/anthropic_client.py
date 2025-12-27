"""
🧘 CLAUDE CLIENT - Etik Rahibi
==============================

Anthropic Claude API entegrasyonu.
Domain: Etik analiz ve değer değerlendirmesi.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional

from .base import BaseLLMClient, LLMConfig, LLMResponse, MockMode

# Opsiyonel import
try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False


class ClaudeClient(BaseLLMClient):
    """
    🧘 Claude Rahibi - Etik Uzmanı

    "Etik boyutu katladım."

    Sürdürülebilirlik, adalet ve değer perspektifinden analiz.
    """

    MONK_NAME = "Claude"
    MONK_DOMAIN = "ethics"
    MONK_MANTRA = "Etik boyutu katladım"
    DEFAULT_MODEL = "claude-3-opus-20240229"

    def __init__(self, config: Optional[LLMConfig] = None):
        super().__init__(config)

        # API key kontrolü
        self.api_key = self.config.api_key or os.getenv("ANTHROPIC_API_KEY")

        if HAS_ANTHROPIC and self.api_key:
            self.client = anthropic.AsyncAnthropic(api_key=self.api_key)
        else:
            self.client = None
            if self.config.mock_mode == MockMode.DISABLED:
                self.config.mock_mode = MockMode.ENABLED

    async def _call_api(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Anthropic API çağrısı"""
        if not self.client:
            return self._generate_mock_response(messages, **kwargs)

        # System mesajını ayır
        system_content = None
        api_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                api_messages.append(msg)

        # API çağrısı
        model = kwargs.get("model", self.config.model or self.DEFAULT_MODEL)

        try:
            response = await self.client.messages.create(
                model=model,
                max_tokens=kwargs.get("max_tokens", self.config.max_tokens),
                system=system_content or "Sen yardımcı bir asistansın.",
                messages=api_messages,
                temperature=kwargs.get("temperature", self.config.temperature),
                top_p=kwargs.get("top_p", self.config.top_p),
            )

            # Yanıtı dönüştür
            content = response.content[0].text if response.content else ""

            return LLMResponse(
                id=response.id,
                model=response.model,
                content=content,
                finish_reason=response.stop_reason or "stop",
                usage={
                    "prompt_tokens": response.usage.input_tokens,
                    "completion_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                },
                is_mock=False,
                metadata={"provider": "anthropic", "monk": self.MONK_NAME},
            )

        except Exception as e:
            if self.config.mock_mode == MockMode.FALLBACK:
                self._errors.append(f"Claude API error: {e}")
                return self._generate_mock_response(messages, **kwargs)
            raise

    async def ethical_review(self, content: str) -> LLMResponse:
        """
        Etik inceleme - özel metod.

        İçeriği etik perspektiften değerlendirir.
        """
        system = """Sen bir etik danışmanısın. Verilen içeriği şu açılardan değerlendir:
1. Sürdürülebilirlik etkisi
2. Sosyal adalet boyutu
3. Çevresel etki
4. Şeffaflık ve hesap verebilirlik

Kısa ve öz değerlendirme yap. A-F arası not ver."""

        return await self.generate(
            prompt=f"Etik değerlendirme yap:\n\n{content}",
            system=system,
        )


# Kısa yol factory
def create_claude_client(
    api_key: Optional[str] = None,
    mock: bool = False
) -> ClaudeClient:
    """Claude client oluştur"""
    config = LLMConfig(
        api_key=api_key,
        mock_mode=MockMode.ENABLED if mock else MockMode.FALLBACK,
    )
    return ClaudeClient(config)
