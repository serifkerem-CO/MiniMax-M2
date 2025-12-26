"""
🔥 KATMAN 3: ATEŞ (TAPINAK AVLUSU)
===================================
"Dönüşüm Ateşi & Dua Çarkları"

Tapınağın orta katı. Rahipler (LLM'ler) ateşin
başında toplanır.

Aktörler: ADVANCED MIND (333 Persona)
Teknoloji: N8N "Prayer Wheels" (Dua Çarkları)
Kod Adı: ALCHEMICAL_FORGE
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import random
import hashlib

from .base import BaseLayer, Element, LayerResult


class MonkRole(Enum):
    """Rahip Rolleri - Her LLM'in Uzmanlığı"""
    ETHICIST = "ethicist"         # Etik boyutu (Claude)
    LOGISTICIAN = "logistician"   # Lojistik boyutu (Mistral)
    CODER = "coder"               # Kod yazıcı (DeepSeek)
    VISIONARY = "visionary"       # Vizyon sahibi (GPT)
    ANALYST = "analyst"           # Analitik (Gemini)
    GUARDIAN = "guardian"         # Koruyucu (Llama)
    SYNTHESIZER = "synthesizer"   # Sentezci (Minimax)


@dataclass
class Monk:
    """
    Rahip - LLM Konsey Üyesi

    Her rahip veriyi kendi perspektifinden katlar.
    """

    name: str
    role: MonkRole
    model_id: str
    temperature: float = 0.7
    folding_count: int = 0
    wisdom_contribution: str = ""

    def __post_init__(self):
        self.mantra = f"{self.name.upper()}_KATLADI"

    async def fold_perspective(self, data: str, context: Dict) -> str:
        """
        Kendi perspektifinden katla

        Returns:
            Katlanmış/zenginleştirilmiş veri
        """
        await asyncio.sleep(0.05)  # Düşünme süresi

        # Her rol farklı katlama yapar
        fold_templates = {
            MonkRole.ETHICIST: f"[ETİK_BOYUT: {data}] → Toplumsal etki değerlendirildi",
            MonkRole.LOGISTICIAN: f"[LOJİSTİK_BOYUT: {data}] → Uygulama adımları belirlendi",
            MonkRole.CODER: f"[KOD_BOYUT: {data}] → Teknik implementasyon hazır",
            MonkRole.VISIONARY: f"[VİZYON_BOYUT: {data}] → Gelecek senaryoları çizildi",
            MonkRole.ANALYST: f"[ANALİZ_BOYUT: {data}] → Veriler çapraz doğrulandı",
            MonkRole.GUARDIAN: f"[GÜVENLİK_BOYUT: {data}] → Risk analizi tamamlandı",
            MonkRole.SYNTHESIZER: f"[SENTEZ_BOYUT: {data}] → Bütünsel perspektif oluştu",
        }

        self.folding_count += 1
        self.wisdom_contribution = fold_templates.get(self.role, f"[KATLANMIŞ: {data}]")

        return self.wisdom_contribution


# 7 Rahip Konseyi - Farklı LLM'ler
MONK_COUNCIL = [
    Monk(name="Claude", role=MonkRole.ETHICIST, model_id="claude-3-opus", temperature=0.5),
    Monk(name="Mistral", role=MonkRole.LOGISTICIAN, model_id="mistral-large", temperature=0.6),
    Monk(name="DeepSeek", role=MonkRole.CODER, model_id="deepseek-coder", temperature=0.3),
    Monk(name="GPT", role=MonkRole.VISIONARY, model_id="gpt-4-turbo", temperature=0.8),
    Monk(name="Gemini", role=MonkRole.ANALYST, model_id="gemini-pro", temperature=0.5),
    Monk(name="Llama", role=MonkRole.GUARDIAN, model_id="llama-3-70b", temperature=0.4),
    Monk(name="Minimax", role=MonkRole.SYNTHESIZER, model_id="minimax-m2", temperature=0.7),
]


@dataclass
class VotingRound:
    """Oylama Turu"""

    round_number: int
    question: str
    votes: Dict[str, str] = field(default_factory=dict)
    consensus: Optional[str] = None
    dissent_ratio: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def add_vote(self, monk_name: str, vote: str):
        self.votes[monk_name] = vote

    def calculate_consensus(self) -> str:
        """Konsensüs hesapla"""
        if not self.votes:
            return "BOŞLUK"

        # Basit çoğunluk
        vote_counts: Dict[str, int] = {}
        for vote in self.votes.values():
            # Basitleştirilmiş oy (ilk 50 karakter)
            simple_vote = vote[:50]
            vote_counts[simple_vote] = vote_counts.get(simple_vote, 0) + 1

        max_count = max(vote_counts.values())
        winners = [v for v, c in vote_counts.items() if c == max_count]

        self.consensus = winners[0] if winners else "BELİRSİZ"
        self.dissent_ratio = 1 - (max_count / len(self.votes))

        return self.consensus


@dataclass
class PrayerWheel:
    """
    Dua Çarkı - N8N Workflow Temsili

    Her dönüşte veri bir kez daha işlenir.
    """

    name: str
    rotations: int = 0
    is_spinning: bool = False
    energy_level: float = 1.0

    async def spin(self, data: str, monks: List[Monk]) -> str:
        """
        Çarkı döndür - Tüm rahipler veriyi katlar

        Returns:
            Çok katlı zenginleştirilmiş veri
        """
        self.is_spinning = True
        self.rotations += 1

        enriched = data
        for monk in monks:
            enriched = await monk.fold_perspective(enriched, {})
            self.energy_level *= 0.95  # Her dönüşte enerji azalır

        self.is_spinning = False
        return enriched


class AtesLayer(BaseLayer):
    """
    🔥 ATEŞ KATMANI

    Tapınak Avlusu - Simya Ocağı

    Görev: 7 LLM'in veriyi çemberinde katlaması
    Teknoloji: N8N Dua Çarkları + Voting Mantras
    Çıktı: Çelikleşmiş, çok boyutlu bilgi
    """

    def __init__(self, monks: Optional[List[Monk]] = None, num_wheels: int = 3):
        super().__init__("ATEŞ", Element.ATES)
        self.code_name = "ALCHEMICAL_FORGE"
        self.monks = monks or MONK_COUNCIL.copy()

        # Dua çarkları
        self.prayer_wheels = [
            PrayerWheel(name=f"ÇARK_{i+1}")
            for i in range(num_wheels)
        ]

        self.voting_history: List[VotingRound] = []
        self.forge_temperature = 963  # Hz - Saf frekans
        self.mantra = "YANIK_PİŞİR_ÇELİKLEŞ"

    async def fold(self, data: Any, context: Optional[Dict] = None) -> LayerResult:
        """
        Ateş Katlama Ritüeli

        7 LLM çember olur, her biri veriyi katlar.
        VOTING MANTRAS protokolü.
        """
        context = context or {}

        # Gelen veriyi al
        if isinstance(data, dict):
            input_text = data.get("purified_text", str(data))
        else:
            input_text = str(data)

        self._notify(f"🔥 [ATEŞ] N8N Dua Çarkları dönüyor... 7 LLM Konseyi toplanıyor...")
        self._notify(f"   ⚗️ Ocak sıcaklığı: {self.forge_temperature}Hz")

        # Hangi rahipleri seç
        active_monks = context.get("monks", random.sample(self.monks, min(5, len(self.monks))))

        # Dua çarkını döndür
        wheel = self.prayer_wheels[0]
        forged_wisdom = await wheel.spin(input_text, active_monks)

        # Voting round
        voting = VotingRound(
            round_number=len(self.voting_history) + 1,
            question=f"Veri nasıl dönüştürülmeli? ({input_text[:50]}...)"
        )

        for monk in active_monks:
            voting.add_vote(monk.name, monk.wisdom_contribution)
            self._notify(f"   ↳ 🧘 {monk.name} Rahibi ({monk.role.value}): Veriyi katladı")

        consensus = voting.calculate_consensus()
        self.voting_history.append(voting)

        # Çelikleşme skoru
        steel_score = self._calculate_steel_score(active_monks, voting)

        self._notify(f"🔥 [ATEŞ] Simya tamamlandı | Çelik Skoru: {steel_score:.2f} | Muhalefet: {voting.dissent_ratio:.1%}")

        return LayerResult(
            layer_name=self.name,
            element=self.element,
            input_data={"raw_input": input_text[:200] + "..."},
            output_data={
                "forged_wisdom": forged_wisdom,
                "steel_score": steel_score,
                "monk_contributions": {
                    m.name: {
                        "role": m.role.value,
                        "contribution": m.wisdom_contribution[:100]
                    }
                    for m in active_monks
                },
                "voting_consensus": consensus,
                "dissent_ratio": voting.dissent_ratio,
                "wheel_rotations": wheel.rotations,
                "forge_temperature": self.forge_temperature
            },
            fold_count=len(active_monks),
            metadata={
                "code_name": self.code_name,
                "mantra": self.mantra,
                "active_monks": [m.name for m in active_monks]
            }
        )

    def _calculate_steel_score(self, monks: List[Monk], voting: VotingRound) -> float:
        """Çelikleşme skoru hesapla"""
        # Faktörler:
        # 1. Katılım çeşitliliği
        diversity = len(set(m.role for m in monks)) / len(MonkRole)

        # 2. Konsensüs gücü
        consensus_strength = 1 - voting.dissent_ratio

        # 3. Katlama derinliği
        fold_depth = sum(m.folding_count for m in monks) / (len(monks) * 10)

        return (diversity * 0.4 + consensus_strength * 0.4 + min(fold_depth, 1.0) * 0.2)

    def get_forge_stats(self) -> Dict[str, Any]:
        """Ocak istatistikleri"""
        return {
            "temperature": self.forge_temperature,
            "total_voting_rounds": len(self.voting_history),
            "prayer_wheels": [
                {
                    "name": w.name,
                    "rotations": w.rotations,
                    "energy": w.energy_level
                }
                for w in self.prayer_wheels
            ],
            "monk_stats": [
                {
                    "name": m.name,
                    "role": m.role.value,
                    "total_folds": m.folding_count
                }
                for m in self.monks
            ]
        }
