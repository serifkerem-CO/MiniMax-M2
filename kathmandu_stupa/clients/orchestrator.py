"""
🎭 MONK ORCHESTRATOR - Rahipler Konseyi Yöneticisi
==================================================

7 LLM rahibini koordine eden orkestratör.
Voting, consensus ve paralel işleme.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Type
from enum import Enum

from .base import BaseLLMClient, LLMConfig, LLMResponse, MockMode
from .anthropic_client import ClaudeClient
from .openai_client import GPTClient
from .minimax_client import MiniMaxClient


class VotingMethod(Enum):
    """Oylama metodları"""
    MAJORITY = "majority"           # Çoğunluk
    WEIGHTED = "weighted"           # Ağırlıklı
    CONSENSUS = "consensus"         # Konsensüs (hepsi aynı fikirde olmalı)
    BEST_CONFIDENCE = "best"        # En yüksek güvenli yanıt


@dataclass
class CouncilDecision:
    """Konsey kararı"""
    id: str
    query: str
    responses: List[LLMResponse]
    winning_response: LLMResponse
    voting_method: VotingMethod
    vote_breakdown: Dict[str, float]
    consensus_score: float
    total_tokens: int
    total_latency_ms: float
    decided_at: datetime = field(default_factory=datetime.now)

    @property
    def wisdom(self) -> str:
        return self.winning_response.content


# Tüm rahip client sınıfları
MONK_CLIENTS: Dict[str, Type[BaseLLMClient]] = {
    "claude": ClaudeClient,
    "gpt": GPTClient,
    "minimax": MiniMaxClient,
}

# Ek rahipler için placeholder'lar (gerçek API olmadan)
class MistralClient(BaseLLMClient):
    MONK_NAME = "Mistral"
    MONK_DOMAIN = "logistics"
    MONK_MANTRA = "Lojistik boyutu katladım"

    async def _call_api(self, messages, **kwargs):
        return self._generate_mock_response(messages, **kwargs)


class DeepSeekClient(BaseLLMClient):
    MONK_NAME = "DeepSeek"
    MONK_DOMAIN = "code"
    MONK_MANTRA = "Kodunu yazdım"

    async def _call_api(self, messages, **kwargs):
        return self._generate_mock_response(messages, **kwargs)


class GeminiClient(BaseLLMClient):
    MONK_NAME = "Gemini"
    MONK_DOMAIN = "analysis"
    MONK_MANTRA = "Analitik boyutu katladım"

    async def _call_api(self, messages, **kwargs):
        return self._generate_mock_response(messages, **kwargs)


class LlamaClient(BaseLLMClient):
    MONK_NAME = "Llama"
    MONK_DOMAIN = "security"
    MONK_MANTRA = "Güvenlik boyutu katladım"

    async def _call_api(self, messages, **kwargs):
        return self._generate_mock_response(messages, **kwargs)


# Tüm rahipleri ekle
MONK_CLIENTS.update({
    "mistral": MistralClient,
    "deepseek": DeepSeekClient,
    "gemini": GeminiClient,
    "llama": LlamaClient,
})


class MonkOrchestrator:
    """
    🎭 Rahipler Konseyi Orkestratörü

    7 LLM rahibini yönetir:
    - Claude (Etik)
    - Mistral (Lojistik)
    - DeepSeek (Kod)
    - Gemini (Analiz)
    - GPT (Yaratıcılık)
    - Llama (Güvenlik)
    - MiniMax (Sentez)

    Dua Çarkı'nın kalbi.
    """

    ALL_MONKS = ["claude", "mistral", "deepseek", "gemini", "gpt", "llama", "minimax"]

    def __init__(
        self,
        monks: Optional[List[str]] = None,
        config: Optional[LLMConfig] = None,
        voting_method: VotingMethod = VotingMethod.WEIGHTED
    ):
        self.config = config or LLMConfig(mock_mode=MockMode.ENABLED)
        self.voting_method = voting_method
        self.monks_to_use = monks or self.ALL_MONKS

        # Client'ları oluştur
        self.clients: Dict[str, BaseLLMClient] = {}
        for monk_name in self.monks_to_use:
            if monk_name in MONK_CLIENTS:
                self.clients[monk_name] = MONK_CLIENTS[monk_name](self.config)

        # Ağırlıklar (domain'e göre)
        self.weights = {
            "claude": 1.2,      # Etik yüksek ağırlık
            "mistral": 1.0,
            "deepseek": 1.5,    # Kod yüksek
            "gemini": 1.3,      # Analiz yüksek
            "gpt": 0.9,
            "llama": 1.4,       # Güvenlik yüksek
            "minimax": 1.1,     # Sentez
        }

        self.council_log: List[CouncilDecision] = []

    async def summon_all(self, prompt: str, system: Optional[str] = None) -> List[LLMResponse]:
        """
        Tüm rahipleri çağır - paralel.

        Her rahip aynı prompt'u kendi perspektifinden yanıtlar.
        """
        tasks = [
            client.generate(prompt, system)
            for client in self.clients.values()
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # Hataları filtrele
        valid_responses = []
        for i, resp in enumerate(responses):
            if isinstance(resp, LLMResponse):
                valid_responses.append(resp)
            else:
                # Hata durumunda mock response
                monk_name = list(self.clients.keys())[i]
                mock = self.clients[monk_name]._generate_mock_response(
                    [{"role": "user", "content": prompt}]
                )
                valid_responses.append(mock)

        return valid_responses

    async def summon_subset(
        self,
        prompt: str,
        monks: List[str],
        system: Optional[str] = None
    ) -> List[LLMResponse]:
        """Belirli rahipleri çağır"""
        tasks = [
            self.clients[monk].generate(prompt, system)
            for monk in monks
            if monk in self.clients
        ]
        return await asyncio.gather(*tasks)

    def _calculate_confidence(self, response: LLMResponse) -> float:
        """Yanıt güvenini hesapla"""
        # Basit heuristik
        content = response.content
        base_confidence = 0.7

        # Uzunluk bonusu
        if len(content) > 200:
            base_confidence += 0.1

        # Domain-specific keywords
        positive_indicators = ["analiz", "sonuç", "öneri", "değerlendirme"]
        for indicator in positive_indicators:
            if indicator in content.lower():
                base_confidence += 0.03

        return min(0.99, base_confidence)

    def _vote(self, responses: List[LLMResponse]) -> tuple[LLMResponse, Dict[str, float], float]:
        """
        Oylama yap.

        Returns: (kazanan yanıt, oy dağılımı, konsensus skoru)
        """
        if not responses:
            raise ValueError("No responses to vote on")

        if len(responses) == 1:
            return responses[0], {"single": 1.0}, 1.0

        # Her yanıt için skor hesapla
        scores: Dict[int, float] = {}
        breakdown: Dict[str, float] = {}

        for i, resp in enumerate(responses):
            monk_name = resp.metadata.get("monk", f"monk_{i}").lower()
            confidence = self._calculate_confidence(resp)
            weight = self.weights.get(monk_name, 1.0)

            if self.voting_method == VotingMethod.WEIGHTED:
                score = confidence * weight
            elif self.voting_method == VotingMethod.BEST_CONFIDENCE:
                score = confidence
            else:  # MAJORITY
                score = 1.0

            scores[i] = score
            breakdown[monk_name] = score

        # En yüksek skorlu yanıtı bul
        winner_idx = max(scores, key=scores.get)
        winner = responses[winner_idx]

        # Konsensüs skoru (yanıtların ne kadar benzer olduğu)
        # Basit: ortalama skor / max skor
        avg_score = sum(scores.values()) / len(scores)
        max_score = max(scores.values())
        consensus = avg_score / max_score if max_score > 0 else 0

        return winner, breakdown, consensus

    async def council_decision(
        self,
        query: str,
        system: Optional[str] = None,
        monks: Optional[List[str]] = None
    ) -> CouncilDecision:
        """
        Konsey kararı al.

        Tüm rahipleri topla, oyla, karar ver.
        """
        # Rahipleri çağır
        if monks:
            responses = await self.summon_subset(query, monks, system)
        else:
            responses = await self.summon_all(query, system)

        # Oyla
        winner, breakdown, consensus = self._vote(responses)

        # Toplam metrikler
        total_tokens = sum(r.usage.get("total_tokens", 0) for r in responses)
        total_latency = sum(r.latency_ms for r in responses)

        decision = CouncilDecision(
            id=f"COUNCIL_{int(datetime.now().timestamp())}",
            query=query,
            responses=responses,
            winning_response=winner,
            voting_method=self.voting_method,
            vote_breakdown=breakdown,
            consensus_score=consensus,
            total_tokens=total_tokens,
            total_latency_ms=total_latency,
        )

        self.council_log.append(decision)
        return decision

    async def fold_with_council(self, content: str, num_folds: int = 3) -> CouncilDecision:
        """
        Konsey ile katlama.

        ATEŞ katmanı için - her rahip veriyi kendi perspektifinden katlar.
        """
        # Rastgele veya sıralı rahip seç
        import random
        selected = random.sample(list(self.clients.keys()), min(num_folds, len(self.clients)))

        # Her rahip katlasın
        fold_tasks = [
            self.clients[monk].fold(content)
            for monk in selected
        ]

        responses = await asyncio.gather(*fold_tasks)

        # Konsey kararı oluştur
        winner, breakdown, consensus = self._vote(list(responses))

        return CouncilDecision(
            id=f"FOLD_{int(datetime.now().timestamp())}",
            query=f"[FOLD] {content[:50]}...",
            responses=list(responses),
            winning_response=winner,
            voting_method=self.voting_method,
            vote_breakdown=breakdown,
            consensus_score=consensus,
            total_tokens=sum(r.usage.get("total_tokens", 0) for r in responses),
            total_latency_ms=sum(r.latency_ms for r in responses),
        )

    def get_stats(self) -> Dict:
        """Orkestratör istatistikleri"""
        return {
            "active_monks": list(self.clients.keys()),
            "voting_method": self.voting_method.value,
            "total_councils": len(self.council_log),
            "avg_consensus": sum(d.consensus_score for d in self.council_log) / max(1, len(self.council_log)),
            "monk_stats": {
                name: client.get_stats()
                for name, client in self.clients.items()
            },
        }

    def __repr__(self):
        return f"🎭 MonkOrchestrator(monks={list(self.clients.keys())}, method={self.voting_method.value})"


# Factory fonksiyonları
def create_council(mock: bool = True) -> MonkOrchestrator:
    """Tam konsey oluştur"""
    config = LLMConfig(mock_mode=MockMode.ENABLED if mock else MockMode.FALLBACK)
    return MonkOrchestrator(config=config)


def create_mini_council(monks: List[str] = None, mock: bool = True) -> MonkOrchestrator:
    """Mini konsey (3 rahip)"""
    monks = monks or ["claude", "gpt", "minimax"]
    config = LLMConfig(mock_mode=MockMode.ENABLED if mock else MockMode.FALLBACK)
    return MonkOrchestrator(monks=monks, config=config)


# Demo
async def demo_orchestrator():
    """Orkestratör demo"""
    print("🎭 Monk Orchestrator Demo")
    print("=" * 50)

    council = create_council(mock=True)
    print(f"Aktif Rahipler: {list(council.clients.keys())}")

    # Konsey kararı
    decision = await council.council_decision(
        "Türkiye'nin 2025 sanayi stratejisi ne olmalı?"
    )

    print(f"\n📜 Konsey Kararı: {decision.id}")
    print(f"   Kazanan: {decision.winning_response.metadata.get('monk')}")
    print(f"   Konsensüs: {decision.consensus_score:.2%}")
    print(f"   Oy Dağılımı: {decision.vote_breakdown}")
    print(f"\n   Bilgelik: {decision.wisdom[:200]}...")


if __name__ == "__main__":
    asyncio.run(demo_orchestrator())
