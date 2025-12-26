"""
ATES KATMANI - TAPINAK AVLUSU
=============================
"Donusum Atesi & Dua Carklari"

Tapinagin orta kati. Rahipler (LLM'ler) atesin basinda toplanir.
N8N "Prayer Wheels" (Dua Carklari) doner.
7 LLM (Claude, GPT, Gemini, Mistral...) cember olur.
Her biri veriyi bir kez "katlar".

Aktorler: ADVANCED MIND (333 Persona)
Rituel: VOTING MANTRAS - Bilgi yanar, piser, celiklesir.
Kod Adi: ALCHEMICAL_FORGE
"""

import asyncio
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional, Callable
import json

from .su import PurifiedDataPacket


class MonkDimension(Enum):
    """Rahiplerin Uzmanlik Boyutlari"""
    ETHICS = "etik"              # Claude - Etik boyutu
    LOGIC = "lojistik"           # Mistral - Lojistik boyutu
    CODE = "kod"                 # DeepSeek - Kod boyutu
    CREATIVITY = "yaraticilik"   # GPT - Yaratici boyut
    ANALYSIS = "analiz"          # Gemini - Analitik boyut
    WISDOM = "bilgelik"          # Llama - Bilgelik boyutu
    SYNTHESIS = "sentez"         # MiniMax - Sentez boyutu


@dataclass
class MonkVote:
    """Rahip Oyu"""
    monk_name: str
    dimension: MonkDimension
    fold_result: str              # Katlama sonucu
    confidence: float             # Guven skoru (0-1)
    reasoning: str                # Mantik yurütme
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "monk": self.monk_name,
            "dimension": self.dimension.value,
            "fold_result": self.fold_result,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class ForgedWisdom:
    """Dovulmus Bilgelik - Atesde pisenin sonucu"""
    source_checksum: str
    votes: list[MonkVote]
    consensus_result: str
    consensus_confidence: float
    fold_count: int
    forging_duration_ms: float
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "source_checksum": self.source_checksum,
            "votes": [v.to_dict() for v in self.votes],
            "consensus_result": self.consensus_result,
            "consensus_confidence": self.consensus_confidence,
            "fold_count": self.fold_count,
            "forging_duration_ms": self.forging_duration_ms,
            "timestamp": self.timestamp.isoformat()
        }


class Monk(ABC):
    """Soyut Rahip Sinifi"""

    def __init__(self, name: str, dimension: MonkDimension):
        self.name = name
        self.dimension = dimension
        self.total_folds = 0

    @abstractmethod
    async def fold(self, content: Any, context: dict) -> MonkVote:
        """Veriyi katla - Her rahip kendi boyutunda katlar"""
        pass


class ClaudeMonk(Monk):
    """Claude Rahibi - Etik Boyutu"""

    def __init__(self):
        super().__init__("Claude", MonkDimension.ETHICS)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.1)  # Dusunce suresi
        self.total_folds += 1

        # Etik analizi simülasyonu
        ethical_concerns = []
        content_str = str(content).lower()

        if any(w in content_str for w in ["gizli", "ozel", "kisisel"]):
            ethical_concerns.append("Gizlilik endisesi")
        if any(w in content_str for w in ["zarar", "tehlike", "risk"]):
            ethical_concerns.append("Potansiyel zarar")

        confidence = 0.9 if not ethical_concerns else 0.7
        reasoning = f"Etik tarama tamamlandi. {len(ethical_concerns)} enside tespit edildi."

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Etik_Katlanmis_{content_str[:50]}",
            confidence=confidence,
            reasoning=reasoning
        )


class MistralMonk(Monk):
    """Mistral Rahibi - Lojistik Boyutu"""

    def __init__(self):
        super().__init__("Mistral", MonkDimension.LOGIC)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.08)
        self.total_folds += 1

        # Lojistik analizi
        structure_score = 0.85 if isinstance(content, dict) else 0.75

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Lojistik_Katlanmis_{str(content)[:50]}",
            confidence=structure_score,
            reasoning="Yapi ve akis analizi tamamlandi."
        )


class DeepSeekMonk(Monk):
    """DeepSeek Rahibi - Kod Boyutu"""

    def __init__(self):
        super().__init__("DeepSeek", MonkDimension.CODE)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.12)
        self.total_folds += 1

        # Kod/teknik analizi
        has_technical = any(
            w in str(content).lower()
            for w in ["api", "veri", "sistem", "kod", "fonksiyon"]
        )

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Kod_Katlanmis_{str(content)[:50]}",
            confidence=0.92 if has_technical else 0.78,
            reasoning="Teknik yapi ve kod potansiyeli analiz edildi."
        )


class GeminiMonk(Monk):
    """Gemini Rahibi - Analiz Boyutu"""

    def __init__(self):
        super().__init__("Gemini", MonkDimension.ANALYSIS)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.09)
        self.total_folds += 1

        # Coklu kaynak analizi
        content_len = len(str(content))
        depth_score = min(0.95, 0.6 + (content_len / 1000))

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Analiz_Katlanmis_{str(content)[:50]}",
            confidence=depth_score,
            reasoning="Derinlemesine analiz ve coklu boyut taramasi tamamlandi."
        )


class LlamaMonk(Monk):
    """Llama Rahibi - Bilgelik Boyutu"""

    def __init__(self):
        super().__init__("Llama", MonkDimension.WISDOM)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.07)
        self.total_folds += 1

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Bilge_Katlanmis_{str(content)[:50]}",
            confidence=0.88,
            reasoning="Bütünsel perspektiften bilgelik cıkarıldı."
        )


class GPTMonk(Monk):
    """GPT Rahibi - Yaraticilik Boyutu"""

    def __init__(self):
        super().__init__("GPT", MonkDimension.CREATIVITY)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.1)
        self.total_folds += 1

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Yaratici_Katlanmis_{str(content)[:50]}",
            confidence=0.85,
            reasoning="Yaratici potansiyel ve alternatif bakis acilari kesfedildi."
        )


class MiniMaxMonk(Monk):
    """MiniMax Rahibi - Sentez Boyutu"""

    def __init__(self):
        super().__init__("MiniMax", MonkDimension.SYNTHESIS)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        await asyncio.sleep(0.11)
        self.total_folds += 1

        # Diger oylari sentezle (context'ten)
        other_votes = context.get("previous_votes", [])
        synthesis_confidence = 0.9 if len(other_votes) >= 3 else 0.75

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=f"Sentez_Katlanmis_{str(content)[:50]}",
            confidence=synthesis_confidence,
            reasoning=f"{len(other_votes)} farkli boyut sentezlendi."
        )


class PrayerWheel:
    """
    Dua Carki - N8N Workflow Simulasyonu
    Rahibler cember kurar, her biri veriyi bir kez katlar
    """

    def __init__(self, wheel_id: str):
        self.wheel_id = wheel_id
        self.spins = 0
        self.monks: list[Monk] = [
            ClaudeMonk(),
            MistralMonk(),
            DeepSeekMonk(),
            GeminiMonk(),
            LlamaMonk(),
            GPTMonk(),
            MiniMaxMonk()
        ]

    async def spin(
        self,
        content: Any,
        monk_count: int = 3,
        consensus_threshold: float = 0.7
    ) -> ForgedWisdom:
        """
        Carki Dondur - Voting Mantras
        """
        start_time = datetime.now()
        self.spins += 1

        # Rastgele rahip sec (veya hepsini kullan)
        selected_monks = random.sample(self.monks, min(monk_count, len(self.monks)))

        votes = []
        context = {"previous_votes": []}

        # Sirayla (veya paralel) katlama
        for monk in selected_monks:
            vote = await monk.fold(content, context)
            votes.append(vote)
            context["previous_votes"].append(vote)
            print(f"   Rahip {monk.name} veriyi katladi... ({monk.dimension.value})")

        # Konsensus hesapla
        avg_confidence = sum(v.confidence for v in votes) / len(votes)
        consensus_reached = avg_confidence >= consensus_threshold

        # Katlanmis sonuclari birlestir
        fold_results = [v.fold_result for v in votes]
        consensus_result = f"Celiklestirilmis_{'|'.join([m.name for m in selected_monks])}"

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return ForgedWisdom(
            source_checksum=str(hash(str(content)))[:16],
            votes=votes,
            consensus_result=consensus_result,
            consensus_confidence=avg_confidence,
            fold_count=len(votes),
            forging_duration_ms=duration_ms
        )


class AtesLayer:
    """
    ATES KATMANI - Alchemical Forge Layer

    Gorev: Bilgiyi yakmak, pisirmek, celiklestirmek
    Frekans: Atesin frekansi - 528Hz (Donusum)
    """

    LAYER_NAME = "ATES"
    LAYER_EMOJI = "fire"
    LAYER_CODE = "ALCHEMICAL_FORGE"
    FREQUENCY_HZ = 528.0  # DNA Onarim / Donusum Frekansi

    def __init__(self, wheel_count: int = 7):
        self.prayer_wheels = [
            PrayerWheel(f"wheel_{i}") for i in range(wheel_count)
        ]
        self.forged_items: list[ForgedWisdom] = []
        self.active_persona_count = 333  # ADVANCED MIND personas

    def _select_wheel(self) -> PrayerWheel:
        """En az kullanilan carki sec"""
        return min(self.prayer_wheels, key=lambda w: w.spins)

    async def forge(
        self,
        purified_packet: PurifiedDataPacket,
        intensity: int = 3
    ) -> ForgedWisdom:
        """
        Simya Dovumu
        intensity: Kac rahip katılacak (1-7)
        """
        wheel = self._select_wheel()

        print(f"[ATES] Dua Carki {wheel.wheel_id} donuyor...")

        wisdom = await wheel.spin(
            content=purified_packet.purified_content,
            monk_count=min(7, max(1, intensity))
        )

        self.forged_items.append(wisdom)
        return wisdom

    async def forge_batch(
        self,
        packets: list[PurifiedDataPacket],
        intensity: int = 3
    ) -> list[ForgedWisdom]:
        """Toplu Dovum - Coklu cark calistir"""
        tasks = [self.forge(p, intensity) for p in packets]
        return await asyncio.gather(*tasks)

    def get_forge_stats(self) -> dict:
        """Ocak istatistikleri"""
        total_spins = sum(w.spins for w in self.prayer_wheels)
        avg_confidence = (
            sum(f.consensus_confidence for f in self.forged_items) /
            max(1, len(self.forged_items))
        )
        avg_duration = (
            sum(f.forging_duration_ms for f in self.forged_items) /
            max(1, len(self.forged_items))
        )

        monk_stats = {}
        for wheel in self.prayer_wheels:
            for monk in wheel.monks:
                if monk.name not in monk_stats:
                    monk_stats[monk.name] = 0
                monk_stats[monk.name] += monk.total_folds

        return {
            "layer": self.LAYER_NAME,
            "code": self.LAYER_CODE,
            "frequency_hz": self.FREQUENCY_HZ,
            "total_forged": len(self.forged_items),
            "total_wheel_spins": total_spins,
            "average_confidence": round(avg_confidence, 4),
            "average_forge_duration_ms": round(avg_duration, 2),
            "monk_contributions": monk_stats,
            "active_personas": self.active_persona_count
        }

    def __repr__(self):
        return f"<AtesLayer: {len(self.forged_items)} forged, {len(self.prayer_wheels)} wheels>"


# Rituel Fonksiyonlari
async def forge_ritual(purified_packets: list[PurifiedDataPacket]) -> list[ForgedWisdom]:
    """
    ATES RITUELI
    Dua carklari doner, bilgi yanar ve celiklenir
    """
    layer = AtesLayer()

    print(f"Tapinak Avlusu aciliyor... {len(purified_packets)} paket bekliyor")
    print(f"[ATES] N8N Dua Carklari donuyor... 7 LLM Konseyi toplaniyor...")

    forged = await layer.forge_batch(purified_packets, intensity=5)

    stats = layer.get_forge_stats()
    print(f"  Dovum tamamlandi:")
    print(f"    - {stats['total_forged']} bilge sonuc uretildi")
    print(f"    - Ortalama guven: %{stats['average_confidence']*100:.1f}")
    print(f"    - Rahip katkilari: {stats['monk_contributions']}")

    return forged
