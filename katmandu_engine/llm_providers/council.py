"""
LLM COUNCIL - 7 Rahip Konseyi
==============================
Tum LLM'leri bir araya getiren oylama ve konsensus sistemi.

Her rahip kendi boyutundan katlar:
    - Claude: Etik
    - GPT: Yaraticilik
    - Gemini: Analiz
    - Mistral: Lojistik
    - DeepSeek: Kod
    - Llama: Bilgelik
    - MiniMax: Sentez
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json

from .base import (
    LLMProvider, LLMResponse, LLMConfig, ProviderType,
    ModelCapability, MockLLMProvider
)
from .claude_provider import ClaudeProvider
from .openai_provider import OpenAIProvider
from .gemini_provider import GeminiProvider
from .mistral_provider import MistralProvider
from .deepseek_provider import DeepSeekProvider
from .llama_provider import LlamaProvider
from .minimax_provider import MiniMaxProvider


class VoteDimension(Enum):
    """Oy Boyutlari - Her rahibin uzmanligi"""
    ETHICS = "etik"              # Claude
    CREATIVITY = "yaraticilik"   # GPT
    ANALYSIS = "analiz"          # Gemini
    LOGIC = "lojistik"           # Mistral
    CODE = "kod"                 # DeepSeek
    WISDOM = "bilgelik"          # Llama
    SYNTHESIS = "sentez"         # MiniMax


@dataclass
class CouncilVote:
    """Konsey Oyu"""
    provider: ProviderType
    dimension: VoteDimension
    content: str
    confidence: float  # 0-1 arasi
    reasoning: str
    latency_ms: float
    success: bool
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "provider": self.provider.value,
            "dimension": self.dimension.value,
            "content": self.content[:500],  # Kisa ozet
            "confidence": self.confidence,
            "reasoning": self.reasoning[:200],
            "latency_ms": self.latency_ms,
            "success": self.success,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class CouncilDecision:
    """Konsey Karari"""
    votes: list[CouncilVote]
    consensus_content: str
    consensus_confidence: float
    total_latency_ms: float
    participating_providers: list[str]
    dimension_coverage: dict  # Hangi boyutlar kapsandi
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "votes": [v.to_dict() for v in self.votes],
            "consensus": self.consensus_content,
            "confidence": self.consensus_confidence,
            "latency_ms": self.total_latency_ms,
            "providers": self.participating_providers,
            "dimensions": self.dimension_coverage,
            "timestamp": self.timestamp.isoformat()
        }


class LLMCouncil:
    """
    LLM Konseyi - 7 Rahibin Toplantisi

    Birden fazla LLM'i paralel calistirip konsensus saglar.
    """

    # Provider -> Dimension eslesmesi
    PROVIDER_DIMENSIONS = {
        ProviderType.CLAUDE: VoteDimension.ETHICS,
        ProviderType.OPENAI: VoteDimension.CREATIVITY,
        ProviderType.GEMINI: VoteDimension.ANALYSIS,
        ProviderType.MISTRAL: VoteDimension.LOGIC,
        ProviderType.DEEPSEEK: VoteDimension.CODE,
        ProviderType.LLAMA: VoteDimension.WISDOM,
        ProviderType.MINIMAX: VoteDimension.SYNTHESIS
    }

    def __init__(self, use_mock_fallback: bool = True):
        """
        Konseyi baslat

        Args:
            use_mock_fallback: API key yoksa mock provider kullan
        """
        self.use_mock_fallback = use_mock_fallback
        self.providers: dict[ProviderType, LLMProvider] = {}
        self._initialize_providers()
        self.decision_history: list[CouncilDecision] = []

    def _initialize_providers(self):
        """Tum provider'lari baslat"""
        provider_classes = {
            ProviderType.CLAUDE: ClaudeProvider,
            ProviderType.OPENAI: OpenAIProvider,
            ProviderType.GEMINI: GeminiProvider,
            ProviderType.MISTRAL: MistralProvider,
            ProviderType.DEEPSEEK: DeepSeekProvider,
            ProviderType.LLAMA: LlamaProvider,
            ProviderType.MINIMAX: MiniMaxProvider
        }

        for ptype, pclass in provider_classes.items():
            try:
                provider = pclass()
                if provider.is_configured:
                    self.providers[ptype] = provider
                    print(f"   [COUNCIL] {ptype.value} provider aktif")
                elif self.use_mock_fallback:
                    self.providers[ptype] = MockLLMProvider(ptype)
                    print(f"   [COUNCIL] {ptype.value} mock provider aktif")
            except Exception as e:
                if self.use_mock_fallback:
                    self.providers[ptype] = MockLLMProvider(ptype)
                    print(f"   [COUNCIL] {ptype.value} mock provider (hata: {e})")

    def get_active_providers(self) -> list[ProviderType]:
        """Aktif provider listesi"""
        return list(self.providers.keys())

    def get_configured_providers(self) -> list[ProviderType]:
        """Gercek API ile yapilandirilmis provider'lar"""
        return [
            ptype for ptype, provider in self.providers.items()
            if provider.is_configured and not isinstance(provider, MockLLMProvider)
        ]

    async def _get_vote(
        self,
        provider_type: ProviderType,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> CouncilVote:
        """Tek bir provider'dan oy al"""
        provider = self.providers.get(provider_type)
        dimension = self.PROVIDER_DIMENSIONS.get(provider_type, VoteDimension.SYNTHESIS)

        if not provider:
            return CouncilVote(
                provider=provider_type,
                dimension=dimension,
                content="",
                confidence=0.0,
                reasoning="Provider bulunamadi",
                latency_ms=0,
                success=False
            )

        # Boyuta ozel sistem promptu ekle
        dimension_context = {
            VoteDimension.ETHICS: "Etik ve guvenlik perspektifinden degerlendir.",
            VoteDimension.CREATIVITY: "Yaratici ve yenilikci bir bakis acisiyla incele.",
            VoteDimension.ANALYSIS: "Derinlemesine analitik bir degerlendirme yap.",
            VoteDimension.LOGIC: "Mantiksal ve yapisal acisindan analiz et.",
            VoteDimension.CODE: "Teknik ve kod perspektifinden incele.",
            VoteDimension.WISDOM: "Butunsel ve bilge bir bakis acisi sun.",
            VoteDimension.SYNTHESIS: "Tum boyutlari sentezle ve sonuc cikar."
        }

        full_system = system_prompt or ""
        full_system += f"\n\n{dimension_context.get(dimension, '')}"
        full_system += "\n\nYanitinin sonunda guven seviyeni 0-100 arasi belirt: [GUVEN: XX]"

        response = await provider.generate(
            prompt=prompt,
            system_prompt=full_system
        )

        # Guven skorunu cikar
        confidence = 0.75  # Varsayilan
        content = response.content
        if "[GUVEN:" in content.upper():
            try:
                import re
                match = re.search(r'\[GUVEN:\s*(\d+)\]', content, re.IGNORECASE)
                if match:
                    confidence = int(match.group(1)) / 100
                    content = re.sub(r'\[GUVEN:\s*\d+\]', '', content, flags=re.IGNORECASE).strip()
            except:
                pass

        return CouncilVote(
            provider=provider_type,
            dimension=dimension,
            content=content,
            confidence=confidence if response.success else 0.0,
            reasoning=f"{dimension.value} boyutundan degerlendirme",
            latency_ms=response.latency_ms,
            success=response.success
        )

    async def convene(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        required_providers: Optional[list[ProviderType]] = None,
        min_votes: int = 3,
        consensus_threshold: float = 0.6
    ) -> CouncilDecision:
        """
        Konseyi Topla - Paralel Oylama

        Args:
            prompt: Degerlendirilecek icerik
            system_prompt: Ek sistem talimatı
            required_providers: Zorunlu provider listesi (None = hepsi)
            min_votes: Minimum oy sayisi
            consensus_threshold: Konsensus esigi (0-1)

        Returns:
            CouncilDecision: Konsey karari
        """
        start_time = datetime.now()

        # Hangi provider'lar katilacak?
        participants = required_providers or list(self.providers.keys())
        participants = [p for p in participants if p in self.providers]

        if len(participants) < min_votes:
            # Mock provider'larla doldur
            for ptype in ProviderType:
                if ptype not in participants and len(participants) < min_votes:
                    if ptype not in self.providers:
                        self.providers[ptype] = MockLLMProvider(ptype)
                    participants.append(ptype)

        # Paralel oylama
        tasks = [
            self._get_vote(ptype, prompt, system_prompt)
            for ptype in participants
        ]

        votes = await asyncio.gather(*tasks)
        votes = [v for v in votes if v.success]

        # Konsensus hesapla
        if votes:
            avg_confidence = sum(v.confidence for v in votes) / len(votes)

            # Icerik sentezi (MiniMax varsa onu kullan, yoksa en yuksek guvenli)
            minimax_vote = next(
                (v for v in votes if v.provider == ProviderType.MINIMAX),
                None
            )

            if minimax_vote:
                consensus_content = minimax_vote.content
            else:
                best_vote = max(votes, key=lambda v: v.confidence)
                consensus_content = best_vote.content

            consensus_confidence = avg_confidence
        else:
            consensus_content = "Konsensus saglanamadi - yeterli oy yok"
            consensus_confidence = 0.0

        # Boyut kapsami
        dimension_coverage = {}
        for vote in votes:
            dim = vote.dimension.value
            if dim not in dimension_coverage:
                dimension_coverage[dim] = []
            dimension_coverage[dim].append(vote.provider.value)

        total_latency = (datetime.now() - start_time).total_seconds() * 1000

        decision = CouncilDecision(
            votes=votes,
            consensus_content=consensus_content,
            consensus_confidence=consensus_confidence,
            total_latency_ms=total_latency,
            participating_providers=[v.provider.value for v in votes],
            dimension_coverage=dimension_coverage
        )

        self.decision_history.append(decision)
        return decision

    async def quick_vote(
        self,
        prompt: str,
        providers: list[ProviderType] = None
    ) -> CouncilDecision:
        """
        Hizli Oylama - 3 provider ile

        Varsayilan: Claude (etik), Gemini (analiz), MiniMax (sentez)
        """
        if providers is None:
            providers = [
                ProviderType.CLAUDE,
                ProviderType.GEMINI,
                ProviderType.MINIMAX
            ]

        return await self.convene(
            prompt=prompt,
            required_providers=providers,
            min_votes=3
        )

    async def full_council(
        self,
        prompt: str,
        system_prompt: Optional[str] = None
    ) -> CouncilDecision:
        """
        Tam Konsey - 7 provider ile
        """
        return await self.convene(
            prompt=prompt,
            system_prompt=system_prompt,
            min_votes=7
        )

    def get_stats(self) -> dict:
        """Konsey istatistikleri"""
        configured_count = len(self.get_configured_providers())
        total_decisions = len(self.decision_history)

        avg_confidence = 0
        if self.decision_history:
            avg_confidence = sum(
                d.consensus_confidence for d in self.decision_history
            ) / total_decisions

        provider_stats = {}
        for ptype, provider in self.providers.items():
            provider_stats[ptype.value] = {
                "configured": provider.is_configured,
                "is_mock": isinstance(provider, MockLLMProvider),
                "dimension": self.PROVIDER_DIMENSIONS.get(ptype, VoteDimension.SYNTHESIS).value
            }

        return {
            "total_providers": len(self.providers),
            "configured_providers": configured_count,
            "mock_providers": len(self.providers) - configured_count,
            "total_decisions": total_decisions,
            "average_confidence": round(avg_confidence, 4),
            "providers": provider_stats
        }

    def __repr__(self):
        configured = len(self.get_configured_providers())
        total = len(self.providers)
        return f"<LLMCouncil providers={total} configured={configured}>"


# Factory fonksiyonu
def create_council(use_mock: bool = True) -> LLMCouncil:
    """
    Yeni konsey olustur

    Args:
        use_mock: API key yoksa mock provider kullan

    Returns:
        LLMCouncil: Hazir konsey
    """
    print("\n   7 Rahip Konseyi kuruluyor...")
    council = LLMCouncil(use_mock_fallback=use_mock)
    print(f"   Konsey hazir: {council}")
    return council
