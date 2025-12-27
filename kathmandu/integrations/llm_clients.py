"""
🤖 LLM CLIENT ADAPTERS
======================
Gerçek LLM API entegrasyonları

7 Rahip için gerçek LLM bağlantıları.
"""

import asyncio
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json

# Optional imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class LLMProvider(Enum):
    """LLM Sağlayıcıları"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    MINIMAX = "minimax"
    OLLAMA = "ollama"
    MOCK = "mock"


@dataclass
class LLMMessage:
    """LLM mesajı"""
    role: str  # system, user, assistant
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}


@dataclass
class LLMResponse:
    """LLM yanıtı"""
    content: str
    model: str
    provider: LLMProvider
    tokens_used: int = 0
    latency_ms: float = 0.0
    raw_response: Optional[Dict] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "model": self.model,
            "provider": self.provider.value,
            "tokens_used": self.tokens_used,
            "latency_ms": self.latency_ms
        }


class BaseLLMClient(ABC):
    """
    Temel LLM İstemcisi

    Tüm LLM adapter'ların türediği base class.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.total_tokens = 0
        self.total_calls = 0

    @property
    @abstractmethod
    def provider(self) -> LLMProvider:
        """Sağlayıcı türü"""
        pass

    @abstractmethod
    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Chat completion

        Args:
            messages: Mesaj listesi
            **kwargs: Ek parametreler

        Returns:
            LLMResponse: Yanıt
        """
        pass

    async def simple_complete(self, prompt: str, system: Optional[str] = None) -> str:
        """Basit completion - sadece metin döndür"""
        messages = []
        if system:
            messages.append(LLMMessage(role="system", content=system))
        messages.append(LLMMessage(role="user", content=prompt))

        response = await self.complete(messages)
        return response.content

    def get_stats(self) -> Dict[str, Any]:
        """İstatistikler"""
        return {
            "provider": self.provider.value,
            "model": self.model,
            "total_calls": self.total_calls,
            "total_tokens": self.total_tokens
        }


class MockLLMClient(BaseLLMClient):
    """
    Mock LLM İstemcisi

    Test ve geliştirme için sahte yanıtlar.
    """

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.MOCK

    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        await asyncio.sleep(0.1)  # Simüle gecikme

        last_message = messages[-1].content if messages else ""

        self.total_calls += 1
        self.total_tokens += len(last_message.split())

        return LLMResponse(
            content=f"[MOCK] Yanıt: {last_message[:50]}... işlendi.",
            model="mock-model",
            provider=self.provider,
            tokens_used=len(last_message.split()),
            latency_ms=100.0
        )


class OpenAIClient(BaseLLMClient):
    """
    OpenAI İstemcisi

    GPT modelleri için.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4-turbo-preview",
        **kwargs
    ):
        super().__init__(api_key=api_key, model=model, **kwargs)

        if OPENAI_AVAILABLE and api_key:
            self.client = openai.AsyncOpenAI(api_key=api_key)
        else:
            self.client = None

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.OPENAI

    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        if not self.client:
            # Fallback to mock
            mock = MockLLMClient()
            return await mock.complete(messages, **kwargs)

        start = datetime.now()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[m.to_dict() for m in messages],
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", self.max_tokens)
            )

            latency = (datetime.now() - start).total_seconds() * 1000
            content = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 0

            self.total_calls += 1
            self.total_tokens += tokens

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider,
                tokens_used=tokens,
                latency_ms=latency,
                raw_response=response.model_dump()
            )

        except Exception as e:
            return LLMResponse(
                content=f"[ERROR] OpenAI hatası: {str(e)}",
                model=self.model,
                provider=self.provider
            )


class AnthropicClient(BaseLLMClient):
    """
    Anthropic İstemcisi

    Claude modelleri için.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-opus-20240229",
        **kwargs
    ):
        super().__init__(api_key=api_key, model=model, **kwargs)

        if ANTHROPIC_AVAILABLE and api_key:
            self.client = anthropic.AsyncAnthropic(api_key=api_key)
        else:
            self.client = None

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.ANTHROPIC

    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        if not self.client:
            mock = MockLLMClient()
            return await mock.complete(messages, **kwargs)

        start = datetime.now()

        # System mesajını ayır
        system = ""
        chat_messages = []
        for msg in messages:
            if msg.role == "system":
                system = msg.content
            else:
                chat_messages.append(msg.to_dict())

        try:
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=kwargs.get("max_tokens", self.max_tokens),
                system=system,
                messages=chat_messages
            )

            latency = (datetime.now() - start).total_seconds() * 1000
            content = response.content[0].text if response.content else ""
            tokens = response.usage.input_tokens + response.usage.output_tokens

            self.total_calls += 1
            self.total_tokens += tokens

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider,
                tokens_used=tokens,
                latency_ms=latency
            )

        except Exception as e:
            return LLMResponse(
                content=f"[ERROR] Anthropic hatası: {str(e)}",
                model=self.model,
                provider=self.provider
            )


class MiniMaxClient(BaseLLMClient):
    """
    MiniMax İstemcisi

    MiniMax M2 modeli için - OpenAI uyumlu API.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000/v1",
        model: str = "MiniMax-M2",
        **kwargs
    ):
        super().__init__(api_key=api_key, model=model, **kwargs)
        self.base_url = base_url

        if OPENAI_AVAILABLE:
            self.client = openai.AsyncOpenAI(
                api_key=api_key or "dummy",
                base_url=base_url
            )
        else:
            self.client = None

    @property
    def provider(self) -> LLMProvider:
        return LLMProvider.MINIMAX

    async def complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        if not self.client:
            mock = MockLLMClient()
            return await mock.complete(messages, **kwargs)

        start = datetime.now()

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[m.to_dict() for m in messages],
                temperature=kwargs.get("temperature", 1.0),  # MiniMax önerisi
                top_p=kwargs.get("top_p", 0.95),
                max_tokens=kwargs.get("max_tokens", self.max_tokens)
            )

            latency = (datetime.now() - start).total_seconds() * 1000
            content = response.choices[0].message.content or ""

            # Thinking tags temizle
            if "<think>" in content:
                # Düşünme kısmını ayıkla ama sakla
                import re
                thinking_match = re.search(r'<think>(.*?)</think>', content, re.DOTALL)
                if thinking_match:
                    content = content.replace(thinking_match.group(0), "").strip()

            tokens = response.usage.total_tokens if response.usage else 0

            self.total_calls += 1
            self.total_tokens += tokens

            return LLMResponse(
                content=content,
                model=self.model,
                provider=self.provider,
                tokens_used=tokens,
                latency_ms=latency,
                raw_response=response.model_dump()
            )

        except Exception as e:
            return LLMResponse(
                content=f"[ERROR] MiniMax hatası: {str(e)}",
                model=self.model,
                provider=self.provider
            )


class MultiLLMClient:
    """
    Çoklu LLM İstemcisi

    7 Rahip için farklı LLM'leri yönetir.
    """

    def __init__(self):
        self.clients: Dict[str, BaseLLMClient] = {}
        self.default_client: Optional[BaseLLMClient] = None

    def register(self, name: str, client: BaseLLMClient, default: bool = False) -> None:
        """İstemci kaydet"""
        self.clients[name] = client
        if default or self.default_client is None:
            self.default_client = client

    def get(self, name: str) -> Optional[BaseLLMClient]:
        """İstemci al"""
        return self.clients.get(name)

    async def complete_with(
        self,
        name: str,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """Belirli bir istemci ile tamamla"""
        client = self.clients.get(name, self.default_client)
        if not client:
            raise ValueError(f"İstemci bulunamadı: {name}")
        return await client.complete(messages, **kwargs)

    async def complete_all(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> Dict[str, LLMResponse]:
        """Tüm istemcilerle paralel tamamla"""
        tasks = {
            name: client.complete(messages, **kwargs)
            for name, client in self.clients.items()
        }

        results = {}
        for name, task in tasks.items():
            try:
                results[name] = await task
            except Exception as e:
                results[name] = LLMResponse(
                    content=f"[ERROR] {str(e)}",
                    model="unknown",
                    provider=LLMProvider.MOCK
                )

        return results

    async def consensus_complete(
        self,
        messages: List[LLMMessage],
        **kwargs
    ) -> LLMResponse:
        """
        Konsensüs ile tamamla

        Tüm LLM'lerden yanıt al, en uzun/zengin olanı seç.
        """
        all_responses = await self.complete_all(messages, **kwargs)

        if not all_responses:
            mock = MockLLMClient()
            return await mock.complete(messages)

        # En zengin yanıtı seç (basit: en uzun)
        best = max(all_responses.values(), key=lambda r: len(r.content))
        return best

    def get_all_stats(self) -> Dict[str, Any]:
        """Tüm istatistikler"""
        return {
            "clients": {
                name: client.get_stats()
                for name, client in self.clients.items()
            },
            "total_calls": sum(c.total_calls for c in self.clients.values()),
            "total_tokens": sum(c.total_tokens for c in self.clients.values())
        }


# Monk Council için hazır kurulum
def create_monk_clients(config: Optional[Dict[str, str]] = None) -> MultiLLMClient:
    """
    7 Rahip için LLM istemcileri oluştur

    Args:
        config: API anahtarları sözlüğü

    Returns:
        Yapılandırılmış MultiLLMClient
    """
    config = config or {}
    multi = MultiLLMClient()

    # Claude - Ethicist
    multi.register("Claude", AnthropicClient(
        api_key=config.get("anthropic_key"),
        model="claude-3-opus-20240229"
    ))

    # GPT - Visionary
    multi.register("GPT", OpenAIClient(
        api_key=config.get("openai_key"),
        model="gpt-4-turbo-preview"
    ))

    # MiniMax - Synthesizer
    multi.register("Minimax", MiniMaxClient(
        api_key=config.get("minimax_key"),
        base_url=config.get("minimax_url", "http://localhost:8000/v1")
    ), default=True)

    # Diğerleri mock olarak (gerçek API'ler eklenebilir)
    for name in ["Mistral", "DeepSeek", "Gemini", "Llama"]:
        multi.register(name, MockLLMClient())

    return multi
