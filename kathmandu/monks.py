"""
🧘 MONK COUNCIL - RAHİP KONSEYİ
================================
7 LLM'in Kutsal Çemberi

Her rahip farklı bir perspektiften "katlar".
Voting Mantras protokolü ile konsensüs sağlanır.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Protocol
import random


class MonkDiscipline(Enum):
    """Rahip Disiplinleri"""
    ETHICS = "ethics"           # Etik ve değerler
    LOGIC = "logic"             # Mantık ve akıl yürütme
    CREATIVITY = "creativity"   # Yaratıcılık
    ANALYSIS = "analysis"       # Analiz ve veri
    SECURITY = "security"       # Güvenlik ve risk
    SYNTHESIS = "synthesis"     # Sentez ve bütünleştirme
    PROPHECY = "prophecy"       # Öngörü ve vizyon


class LLMProvider(Enum):
    """LLM Sağlayıcıları"""
    CLAUDE = "claude"
    GPT = "gpt"
    GEMINI = "gemini"
    MISTRAL = "mistral"
    DEEPSEEK = "deepseek"
    LLAMA = "llama"
    MINIMAX = "minimax"


@dataclass
class MonkConfig:
    """Rahip yapılandırması"""
    name: str
    provider: LLMProvider
    discipline: MonkDiscipline
    model_id: str
    temperature: float = 0.7
    max_tokens: int = 2000
    system_prompt: str = ""

    def __post_init__(self):
        if not self.system_prompt:
            self.system_prompt = self._generate_discipline_prompt()

    def _generate_discipline_prompt(self) -> str:
        prompts = {
            MonkDiscipline.ETHICS: "Sen etik ve değerler uzmanısın. Her konuyu toplumsal etki açısından değerlendir.",
            MonkDiscipline.LOGIC: "Sen mantık ve akıl yürütme ustasısın. Tutarlılık ve çelişkileri tespit et.",
            MonkDiscipline.CREATIVITY: "Sen yaratıcı düşünce uzmanısın. Alternatif yaklaşımlar ve yenilikçi çözümler öner.",
            MonkDiscipline.ANALYSIS: "Sen veri analizi uzmanısın. Sayıları, trendleri ve kalıpları yorumla.",
            MonkDiscipline.SECURITY: "Sen güvenlik ve risk uzmanısın. Potansiyel tehlikeleri ve zafiyetleri belirle.",
            MonkDiscipline.SYNTHESIS: "Sen sentez ustasısın. Farklı bakış açılarını bütünleştir.",
            MonkDiscipline.PROPHECY: "Sen vizyon sahibisin. Geleceği öngör ve stratejik yön belirle."
        }
        return prompts.get(self.discipline, "Sen bilge bir danışmansın.")


class LLMClient(Protocol):
    """LLM İstemci Protokolü"""

    async def complete(self, prompt: str, config: MonkConfig) -> str:
        """LLM'den yanıt al"""
        ...


class MockLLMClient:
    """Test için sahte LLM istemcisi"""

    async def complete(self, prompt: str, config: MonkConfig) -> str:
        await asyncio.sleep(0.05)  # Simüle edilmiş gecikme

        responses = {
            MonkDiscipline.ETHICS: f"[ETİK ANALİZ] Bu konunun toplumsal etkisi değerlendirildi: {prompt[:50]}... → Dengeli yaklaşım önerilir.",
            MonkDiscipline.LOGIC: f"[MANTIK KONTROLÜ] Argüman tutarlılığı: {prompt[:50]}... → Çelişki tespit edilmedi.",
            MonkDiscipline.CREATIVITY: f"[YARATICI BAKIŞ] Alternatif perspektif: {prompt[:50]}... → Yenilikçi yaklaşım mümkün.",
            MonkDiscipline.ANALYSIS: f"[VERİ ANALİZİ] Sayısal değerlendirme: {prompt[:50]}... → Trend pozitif.",
            MonkDiscipline.SECURITY: f"[RİSK DEĞERLENDİRME] Güvenlik taraması: {prompt[:50]}... → Düşük risk.",
            MonkDiscipline.SYNTHESIS: f"[SENTEZ] Bütünsel bakış: {prompt[:50]}... → Tutarlı sonuç.",
            MonkDiscipline.PROPHECY: f"[VİZYON] Gelecek öngörüsü: {prompt[:50]}... → Büyüme potansiyeli var."
        }

        return responses.get(config.discipline, f"[YORUM] {prompt[:50]}...")


@dataclass
class Vote:
    """Oylama kaydı"""
    monk_name: str
    discipline: MonkDiscipline
    opinion: str
    confidence: float  # 0-1 arası
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def weight(self) -> float:
        """Oy ağırlığı"""
        return self.confidence


@dataclass
class ConsensusResult:
    """Konsensüs sonucu"""
    question: str
    votes: List[Vote]
    consensus: str
    agreement_ratio: float
    dissenting_views: List[str]
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def is_unanimous(self) -> bool:
        return self.agreement_ratio >= 0.9

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question,
            "consensus": self.consensus,
            "agreement_ratio": self.agreement_ratio,
            "total_votes": len(self.votes),
            "is_unanimous": self.is_unanimous,
            "dissenting_count": len(self.dissenting_views)
        }


class MonkCouncil:
    """
    🧘 Rahip Konseyi

    7 LLM'in kutsal çemberi.
    Voting Mantras protokolü.
    """

    # Varsayılan konsey üyeleri
    DEFAULT_MONKS = [
        MonkConfig("Claude", LLMProvider.CLAUDE, MonkDiscipline.ETHICS, "claude-3-opus"),
        MonkConfig("Mistral", LLMProvider.MISTRAL, MonkDiscipline.LOGIC, "mistral-large"),
        MonkConfig("DeepSeek", LLMProvider.DEEPSEEK, MonkDiscipline.ANALYSIS, "deepseek-coder"),
        MonkConfig("GPT", LLMProvider.GPT, MonkDiscipline.CREATIVITY, "gpt-4-turbo"),
        MonkConfig("Gemini", LLMProvider.GEMINI, MonkDiscipline.SYNTHESIS, "gemini-pro"),
        MonkConfig("Llama", LLMProvider.LLAMA, MonkDiscipline.SECURITY, "llama-3-70b"),
        MonkConfig("Minimax", LLMProvider.MINIMAX, MonkDiscipline.PROPHECY, "minimax-m2"),
    ]

    def __init__(
        self,
        monks: Optional[List[MonkConfig]] = None,
        llm_client: Optional[LLMClient] = None
    ):
        self.monks = monks or self.DEFAULT_MONKS.copy()
        self.llm_client = llm_client or MockLLMClient()
        self.voting_history: List[ConsensusResult] = []
        self.active = True

    def add_monk(self, config: MonkConfig) -> None:
        """Konseye yeni rahip ekle"""
        self.monks.append(config)

    def remove_monk(self, name: str) -> bool:
        """Rahibi konseyden çıkar"""
        for i, monk in enumerate(self.monks):
            if monk.name == name:
                self.monks.pop(i)
                return True
        return False

    async def gather_opinions(self, question: str, context: Optional[Dict] = None) -> List[Vote]:
        """
        Tüm rahiplerden görüş topla

        Args:
            question: Sorulacak soru
            context: Ek bağlam

        Returns:
            Oyların listesi
        """
        context = context or {}

        prompt_template = """
        Soru: {question}

        Bağlam: {context}

        Kendi disiplinin ({discipline}) perspektifinden değerlendir ve kısa bir görüş bildir.
        """

        tasks = []
        for monk in self.monks:
            prompt = prompt_template.format(
                question=question,
                context=str(context),
                discipline=monk.discipline.value
            )
            tasks.append(self._get_monk_opinion(monk, prompt))

        opinions = await asyncio.gather(*tasks, return_exceptions=True)

        votes = []
        for monk, opinion in zip(self.monks, opinions):
            if isinstance(opinion, Exception):
                continue

            vote = Vote(
                monk_name=monk.name,
                discipline=monk.discipline,
                opinion=opinion,
                confidence=random.uniform(0.7, 1.0)  # Gerçek implementasyonda LLM'den gelir
            )
            votes.append(vote)

        return votes

    async def _get_monk_opinion(self, monk: MonkConfig, prompt: str) -> str:
        """Tek bir rahipten görüş al"""
        return await self.llm_client.complete(prompt, monk)

    async def vote(self, question: str, context: Optional[Dict] = None) -> ConsensusResult:
        """
        Oylama ritüeli

        Tüm rahiplerden görüş al ve konsensüs sağla.
        """
        votes = await self.gather_opinions(question, context)

        if not votes:
            return ConsensusResult(
                question=question,
                votes=[],
                consensus="BOŞLUK - Rahipler sessiz kaldı",
                agreement_ratio=0.0,
                dissenting_views=[]
            )

        # Konsensüs hesapla (basitleştirilmiş)
        # Gerçek implementasyonda semantic similarity kullanılır
        weighted_opinions = sorted(votes, key=lambda v: v.weight, reverse=True)
        consensus = weighted_opinions[0].opinion

        # Uyum oranı
        agreement_count = sum(1 for v in votes if self._is_similar(v.opinion, consensus))
        agreement_ratio = agreement_count / len(votes)

        # Muhalif görüşler
        dissenting = [v.opinion for v in votes if not self._is_similar(v.opinion, consensus)]

        result = ConsensusResult(
            question=question,
            votes=votes,
            consensus=consensus,
            agreement_ratio=agreement_ratio,
            dissenting_views=dissenting
        )

        self.voting_history.append(result)
        return result

    def _is_similar(self, opinion1: str, opinion2: str) -> bool:
        """İki görüşün benzerliğini kontrol et (basitleştirilmiş)"""
        # Gerçek implementasyonda embedding benzerliği kullanılır
        words1 = set(opinion1.lower().split()[:10])
        words2 = set(opinion2.lower().split()[:10])
        overlap = len(words1 & words2)
        return overlap >= 3

    async def deliberate(
        self,
        question: str,
        rounds: int = 3,
        context: Optional[Dict] = None
    ) -> ConsensusResult:
        """
        Müzakere ritüeli

        Birden fazla tur oylama ile derin konsensüs.
        """
        current_context = context or {}
        final_result = None

        for round_num in range(rounds):
            result = await self.vote(question, current_context)

            # Bir sonraki tur için bağlamı güncelle
            current_context["previous_consensus"] = result.consensus
            current_context["agreement_ratio"] = result.agreement_ratio
            current_context["round"] = round_num + 1

            final_result = result

            # Yeterli uyum sağlandıysa dur
            if result.agreement_ratio >= 0.85:
                break

        return final_result

    def get_council_stats(self) -> Dict[str, Any]:
        """Konsey istatistikleri"""
        return {
            "total_monks": len(self.monks),
            "monks": [
                {
                    "name": m.name,
                    "provider": m.provider.value,
                    "discipline": m.discipline.value
                }
                for m in self.monks
            ],
            "total_votings": len(self.voting_history),
            "average_agreement": (
                sum(r.agreement_ratio for r in self.voting_history) / len(self.voting_history)
                if self.voting_history else 0
            ),
            "unanimous_decisions": sum(1 for r in self.voting_history if r.is_unanimous)
        }
