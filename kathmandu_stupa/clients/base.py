"""
🧘 BASE LLM CLIENT - Rahip Temel Sınıfı
=======================================

Tüm LLM client'larının miras aldığı temel sınıf.
Mock mode ile test edilebilir.
"""

import asyncio
import hashlib
import random
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class MockMode(Enum):
    """Mock modları"""
    DISABLED = "disabled"       # Gerçek API kullan
    ENABLED = "enabled"         # Her zaman mock
    FALLBACK = "fallback"       # API hata verirse mock'a düş


@dataclass
class LLMResponse:
    """LLM yanıt paketi"""
    id: str
    model: str
    content: str
    role: str = "assistant"
    finish_reason: str = "stop"
    usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
    })
    latency_ms: float = 0.0
    is_mock: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    @property
    def text(self) -> str:
        """Kısa erişim"""
        return self.content


@dataclass
class LLMConfig:
    """LLM konfigürasyonu"""
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    model: str = "default"
    temperature: float = 1.0
    top_p: float = 0.95
    top_k: int = 40
    max_tokens: int = 4096
    timeout: int = 30
    mock_mode: MockMode = MockMode.FALLBACK
    retry_attempts: int = 3
    retry_delay: float = 1.0


class BaseLLMClient(ABC):
    """
    🧘 Temel LLM Client

    Tüm rahiplerin (LLM'lerin) ortak arayüzü.
    """

    # Rahip özellikleri - alt sınıflar override eder
    MONK_NAME: str = "Unknown"
    MONK_DOMAIN: str = "general"
    MONK_MANTRA: str = "Bilgelik paylaştım"
    DEFAULT_MODEL: str = "default"

    def __init__(self, config: Optional[LLMConfig] = None):
        self.config = config or LLMConfig()
        self._request_count = 0
        self._total_tokens = 0
        self._total_latency = 0.0
        self._errors: List[str] = []

    @abstractmethod
    async def _call_api(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Gerçek API çağrısı - alt sınıflar implement eder"""
        pass

    def _generate_mock_response(self, messages: List[Dict], **kwargs) -> LLMResponse:
        """Mock yanıt üret"""
        # Son kullanıcı mesajını al
        last_message = messages[-1]["content"] if messages else "empty"

        # Domain'e göre mock yanıt
        mock_responses = {
            "ethics": f"[ETİK ANALİZ] '{last_message[:50]}' değerlendirildi. Sürdürülebilirlik skoru: A+",
            "logistics": f"[LOJİSTİK] Operasyonel verimlilik analizi tamamlandı. Optimizasyon önerisi mevcut.",
            "code": f"[KOD] ```python\ndef process(data): return transform(data)\n```",
            "analysis": f"[ANALİZ] Veri setinde 3 kritik pattern tespit edildi. Trend: Yükseliş.",
            "creativity": f"[YARATICI] Alternatif 5 senaryo oluşturuldu. En umut verici: Senaryo C.",
            "security": f"[GÜVENLİK] Risk değerlendirmesi: DÜŞÜK. Öneri: MFA aktivasyonu.",
            "synthesis": f"[SENTEZ] Tüm perspektifler birleştirildi. Konsensus: Dönüşüm fırsatı.",
            "general": f"[GENEL] Analiz tamamlandı: {last_message[:30]}... -> İşlendi.",
        }

        content = mock_responses.get(self.MONK_DOMAIN, mock_responses["general"])
        content = f"{self.MONK_MANTRA}. {content}"

        # Simüle edilmiş token sayısı
        prompt_tokens = sum(len(m.get("content", "").split()) for m in messages)
        completion_tokens = len(content.split())

        return LLMResponse(
            id=f"mock_{hashlib.md5(str(time.time()).encode()).hexdigest()[:12]}",
            model=f"{self.MONK_NAME.lower()}-mock",
            content=content,
            usage={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": prompt_tokens + completion_tokens,
            },
            latency_ms=random.uniform(50, 200),
            is_mock=True,
            metadata={"monk": self.MONK_NAME, "domain": self.MONK_DOMAIN},
        )

    async def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Tek prompt ile yanıt üret.
        """
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        return await self.chat(messages, **kwargs)

    async def chat(
        self,
        messages: List[Dict],
        **kwargs
    ) -> LLMResponse:
        """
        Chat formatında yanıt üret.

        Mock mode'a göre gerçek veya sahte yanıt döner.
        """
        start_time = time.time()
        self._request_count += 1

        try:
            if self.config.mock_mode == MockMode.ENABLED:
                response = self._generate_mock_response(messages, **kwargs)
            elif self.config.mock_mode == MockMode.DISABLED:
                response = await self._call_api(messages, **kwargs)
            else:  # FALLBACK
                try:
                    response = await self._call_api(messages, **kwargs)
                except Exception as e:
                    self._errors.append(f"API error, falling back to mock: {e}")
                    response = self._generate_mock_response(messages, **kwargs)

            # Metrikleri güncelle
            elapsed = (time.time() - start_time) * 1000
            response.latency_ms = elapsed
            self._total_latency += elapsed
            self._total_tokens += response.usage.get("total_tokens", 0)

            return response

        except Exception as e:
            self._errors.append(str(e))
            raise

    async def fold(self, content: str, context: Optional[str] = None) -> LLMResponse:
        """
        Veriyi "katla" - domain perspektifinden işle.

        Bu, ATEŞ katmanındaki katlama ritueli için.
        """
        system_prompt = f"""Sen {self.MONK_NAME} rahibisin.
Uzmanlık alanın: {self.MONK_DOMAIN}
Mantran: "{self.MONK_MANTRA}"

Verilen içeriği kendi perspektifinden analiz et ve katla.
Kısa, öz ve etkili ol. Türkçe yanıt ver."""

        if context:
            system_prompt += f"\n\nEk bağlam: {context}"

        return await self.generate(
            prompt=f"Bu içeriği katla ve dönüştür:\n\n{content}",
            system=system_prompt,
        )

    def get_stats(self) -> Dict:
        """İstatistikler"""
        return {
            "monk_name": self.MONK_NAME,
            "domain": self.MONK_DOMAIN,
            "requests": self._request_count,
            "total_tokens": self._total_tokens,
            "avg_latency_ms": self._total_latency / max(1, self._request_count),
            "errors": len(self._errors),
            "mock_mode": self.config.mock_mode.value,
        }

    def __repr__(self):
        return f"🧘 {self.MONK_NAME}Client(domain={self.MONK_DOMAIN}, mode={self.config.mock_mode.value})"
