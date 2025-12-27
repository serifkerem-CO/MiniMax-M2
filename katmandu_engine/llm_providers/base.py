"""
LLM PROVIDER BASE - Temel Sinif ve Arayuzler
=============================================
Tum LLM provider'larin implement edecegi temel sinif.
"""

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, AsyncIterator
import json
import os


class ProviderType(Enum):
    """Provider Tipleri"""
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    LLAMA = "llama"
    MINIMAX = "minimax"


class ModelCapability(Enum):
    """Model Yetenekleri"""
    TEXT_GENERATION = "text"
    CODE_GENERATION = "code"
    REASONING = "reasoning"
    ANALYSIS = "analysis"
    ETHICS = "ethics"
    CREATIVITY = "creativity"
    SYNTHESIS = "synthesis"
    TOOL_USE = "tool_use"
    VISION = "vision"


@dataclass
class LLMConfig:
    """LLM Yapilandirmasi"""
    api_key: str
    model_id: str
    base_url: Optional[str] = None
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout_seconds: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0

    @classmethod
    def from_env(cls, provider: ProviderType, model_id: Optional[str] = None) -> "LLMConfig":
        """Environment degiskenlerinden yukle"""
        env_prefix = provider.value.upper()

        api_key = os.environ.get(f"{env_prefix}_API_KEY", "")
        base_url = os.environ.get(f"{env_prefix}_BASE_URL")

        default_models = {
            ProviderType.CLAUDE: "claude-sonnet-4-20250514",
            ProviderType.OPENAI: "gpt-4o",
            ProviderType.GEMINI: "gemini-2.0-flash",
            ProviderType.MISTRAL: "mistral-large-latest",
            ProviderType.DEEPSEEK: "deepseek-chat",
            ProviderType.LLAMA: "meta-llama/Llama-3.3-70B-Instruct-Turbo",
            ProviderType.MINIMAX: "MiniMax-Text-01"
        }

        return cls(
            api_key=api_key,
            model_id=model_id or default_models.get(provider, ""),
            base_url=base_url
        )


@dataclass
class LLMResponse:
    """LLM Yaniti"""
    provider: ProviderType
    model_id: str
    content: str
    raw_response: Optional[dict] = None
    usage: dict = field(default_factory=dict)
    latency_ms: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    error: Optional[str] = None
    success: bool = True

    def to_dict(self) -> dict:
        return {
            "provider": self.provider.value,
            "model": self.model_id,
            "content": self.content,
            "usage": self.usage,
            "latency_ms": self.latency_ms,
            "timestamp": self.timestamp.isoformat(),
            "success": self.success,
            "error": self.error
        }


class LLMProvider(ABC):
    """
    Soyut LLM Provider Sinifi

    Tum LLM provider'lar bu sinifi miras alir.
    """

    def __init__(self, config: LLMConfig):
        self.config = config
        self.provider_type: ProviderType = ProviderType.CLAUDE  # Override in subclass
        self.capabilities: list[ModelCapability] = []
        self._request_count = 0
        self._total_tokens = 0
        self._total_latency = 0.0

    @property
    def is_configured(self) -> bool:
        """API key mevcut mu?"""
        return bool(self.config.api_key)

    @abstractmethod
    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """
        API'ye istek yap (alt siniflar implement eder)

        Args:
            messages: Mesaj listesi [{"role": "user", "content": "..."}]
            **kwargs: Ek parametreler

        Returns:
            API'den gelen ham yanit
        """
        pass

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Metin uret

        Args:
            prompt: Kullanici promptu
            system_prompt: Sistem promptu (opsiyonel)
            **kwargs: Ek parametreler

        Returns:
            LLMResponse: Yanityi iceren nesne
        """
        if not self.is_configured:
            return LLMResponse(
                provider=self.provider_type,
                model_id=self.config.model_id,
                content="",
                error="API key yapilandirilmamis",
                success=False
            )

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        start_time = time.time()
        last_error = None

        # Retry mekanizmasi
        for attempt in range(self.config.retry_count):
            try:
                raw_response = await self._make_request(messages, **kwargs)
                latency = (time.time() - start_time) * 1000

                # Yaniti parse et
                content = self._extract_content(raw_response)
                usage = self._extract_usage(raw_response)

                self._request_count += 1
                self._total_tokens += usage.get("total_tokens", 0)
                self._total_latency += latency

                return LLMResponse(
                    provider=self.provider_type,
                    model_id=self.config.model_id,
                    content=content,
                    raw_response=raw_response,
                    usage=usage,
                    latency_ms=latency,
                    success=True
                )

            except Exception as e:
                last_error = str(e)
                if attempt < self.config.retry_count - 1:
                    await asyncio.sleep(self.config.retry_delay * (attempt + 1))

        # Tum denemeler basarisiz
        return LLMResponse(
            provider=self.provider_type,
            model_id=self.config.model_id,
            content="",
            error=last_error,
            latency_ms=(time.time() - start_time) * 1000,
            success=False
        )

    async def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Streaming metin uretimi (varsa)

        Varsayilan olarak non-streaming generate kullanir.
        """
        response = await self.generate(prompt, system_prompt, **kwargs)
        if response.success:
            yield response.content
        else:
            yield f"[HATA: {response.error}]"

    def _extract_content(self, raw_response: dict) -> str:
        """Yanittan icerigi cikar (alt siniflar override edebilir)"""
        # OpenAI formatı
        if "choices" in raw_response:
            return raw_response["choices"][0]["message"]["content"]
        # Anthropic formatı
        if "content" in raw_response:
            content = raw_response["content"]
            if isinstance(content, list):
                return content[0].get("text", "")
            return content
        return str(raw_response)

    def _extract_usage(self, raw_response: dict) -> dict:
        """Token kullanim bilgisini cikar"""
        if "usage" in raw_response:
            return raw_response["usage"]
        return {}

    def get_stats(self) -> dict:
        """Provider istatistikleri"""
        return {
            "provider": self.provider_type.value,
            "model": self.config.model_id,
            "configured": self.is_configured,
            "capabilities": [c.value for c in self.capabilities],
            "total_requests": self._request_count,
            "total_tokens": self._total_tokens,
            "average_latency_ms": (
                self._total_latency / self._request_count
                if self._request_count > 0 else 0
            )
        }

    def __repr__(self):
        status = "configured" if self.is_configured else "not configured"
        return f"<{self.__class__.__name__} model={self.config.model_id} {status}>"


class MockLLMProvider(LLMProvider):
    """
    Mock LLM Provider - Test ve fallback icin

    API key olmadığında kullanılır.
    """

    def __init__(self, provider_type: ProviderType):
        config = LLMConfig(
            api_key="mock",
            model_id=f"mock-{provider_type.value}"
        )
        super().__init__(config)
        self.provider_type = provider_type
        self.capabilities = list(ModelCapability)

    @property
    def is_configured(self) -> bool:
        return True  # Mock her zaman hazir

    async def _make_request(self, messages: list[dict], **kwargs) -> dict:
        """Simule edilmis yanit"""
        await asyncio.sleep(0.1)  # Gecikme simule

        user_message = messages[-1]["content"] if messages else ""

        # Provider'a gore farkli yanit stilleri
        responses = {
            ProviderType.CLAUDE: f"[Claude/Etik] Bu konuda etik bir degerlendirme yapiyorum: {user_message[:100]}...",
            ProviderType.OPENAI: f"[GPT/Yaratici] Yaratici bir bakis acisiyla: {user_message[:100]}...",
            ProviderType.GEMINI: f"[Gemini/Analiz] Analitik olarak degerlendirildiginde: {user_message[:100]}...",
            ProviderType.MISTRAL: f"[Mistral/Lojistik] Lojistik perspektiften: {user_message[:100]}...",
            ProviderType.DEEPSEEK: f"[DeepSeek/Kod] Teknik olarak incelendiginde: {user_message[:100]}...",
            ProviderType.LLAMA: f"[Llama/Bilgelik] Butunsel bir bakisla: {user_message[:100]}...",
            ProviderType.MINIMAX: f"[MiniMax/Sentez] Sentezlendiginde: {user_message[:100]}..."
        }

        return {
            "choices": [{
                "message": {
                    "content": responses.get(self.provider_type, f"Mock yanit: {user_message[:100]}")
                }
            }],
            "usage": {
                "prompt_tokens": len(user_message.split()),
                "completion_tokens": 50,
                "total_tokens": len(user_message.split()) + 50
            }
        }
