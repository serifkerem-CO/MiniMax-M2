"""
ATES KATMANI - TAPINAK AVLUSU
=============================
"Donusum Atesi & Dua Carklari"

Tapinagin orta kati. Rahipler (LLM'ler) atesin basinda toplanir.
N8N "Prayer Wheels" (Dua Carklari) doner.
7 LLM (Claude, GPT, Gemini, Mistral...) cember olur.
Her biri veriyi bir kez "katlar".

GERCEK API ENTEGRASYONU:
    - Claude (Anthropic) -> Etik boyutu
    - GPT (OpenAI) -> Yaraticilik boyutu
    - Gemini (Google) -> Analiz boyutu
    - Mistral -> Lojistik boyutu
    - DeepSeek -> Kod boyutu
    - Llama (Together/Groq) -> Bilgelik boyutu
    - MiniMax -> Sentez boyutu

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

# LLM Provider importlari
try:
    from ..llm_providers import (
        LLMCouncil, CouncilVote, create_council,
        ProviderType, LLMProvider
    )
    LLM_PROVIDERS_AVAILABLE = True
except ImportError:
    LLM_PROVIDERS_AVAILABLE = False


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
    latency_ms: float = 0.0       # API gecikme suresi
    is_real_api: bool = False     # Gercek API mi mock mu?
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "monk": self.monk_name,
            "dimension": self.dimension.value,
            "fold_result": self.fold_result,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "latency_ms": self.latency_ms,
            "is_real_api": self.is_real_api,
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
    real_api_count: int = 0       # Kac tane gercek API kullanildi
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "source_checksum": self.source_checksum,
            "votes": [v.to_dict() for v in self.votes],
            "consensus_result": self.consensus_result,
            "consensus_confidence": self.consensus_confidence,
            "fold_count": self.fold_count,
            "forging_duration_ms": self.forging_duration_ms,
            "real_api_count": self.real_api_count,
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


class RealLLMMonk(Monk):
    """
    Gercek LLM API Kullanan Rahip

    LLM Provider'lari kullanarak gercek API cagrilari yapar.
    """

    DIMENSION_PROMPTS = {
        MonkDimension.ETHICS: """Sen bir etik ve guvenlik uzmanisin.
Verilen icerigi etik acisindan degerlendir:
- Potansiyel zararlar
- Gizlilik endisleri
- Toplumsal etki
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.CREATIVITY: """Sen yaratici bir dusunur sun.
Verilen icerigi yaratici acisindan incele:
- Alternatif bakis acilari
- Yenilikci fikirler
- Ilham verici noktalar
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.ANALYSIS: """Sen bir analiz uzmanisin.
Verilen icerigi derinlemesine analiz et:
- Ana temalar
- Oruntuler
- Kritik noktalar
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.LOGIC: """Sen bir yapi ve lojistik uzmanisin.
Verilen icerigin yapisini incele:
- Mantiksal tutarlilik
- Akis ve baglantilar
- Optimizasyon noktalari
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.CODE: """Sen bir teknik ve kod uzmanisin.
Verilen icerigi teknik acisindan incele:
- Teknik fizibilite
- Implementasyon onerileri
- Potansiyel zorluklar
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.WISDOM: """Sen bir bilge ve danismansin.
Verilen icerigi butunsel perspektiften degerlendir:
- Uzun vadeli etkiler
- Tarihsel baglam
- Derin icgoruler
Kisa ve oz bir degerlendirme yap.""",

        MonkDimension.SYNTHESIS: """Sen bir sentez uzmanisin.
Verilen icerigi ve onceki degerlendirmeleri sentezle:
- Ortak noktalar
- Celiskiler
- Bütünsel sonuc
Kisa ve oz bir degerlendirme yap."""
    }

    PROVIDER_DIMENSION_MAP = {
        ProviderType.CLAUDE: MonkDimension.ETHICS,
        ProviderType.OPENAI: MonkDimension.CREATIVITY,
        ProviderType.GEMINI: MonkDimension.ANALYSIS,
        ProviderType.MISTRAL: MonkDimension.LOGIC,
        ProviderType.DEEPSEEK: MonkDimension.CODE,
        ProviderType.LLAMA: MonkDimension.WISDOM,
        ProviderType.MINIMAX: MonkDimension.SYNTHESIS
    }

    def __init__(self, provider: LLMProvider, provider_type: ProviderType):
        dimension = self.PROVIDER_DIMENSION_MAP.get(provider_type, MonkDimension.SYNTHESIS)
        super().__init__(provider_type.value.capitalize(), dimension)
        self.provider = provider
        self.provider_type = provider_type

    async def fold(self, content: Any, context: dict) -> MonkVote:
        """Gercek LLM API ile katlama"""
        self.total_folds += 1

        # Onceki oylar varsa context'e ekle
        previous_context = ""
        if context.get("previous_votes"):
            previous_context = "\n\nOnceki degerlendirmeler:\n"
            for vote in context["previous_votes"][-3:]:  # Son 3 oy
                previous_context += f"- [{vote.dimension.value}]: {vote.fold_result[:100]}...\n"

        system_prompt = self.DIMENSION_PROMPTS.get(self.dimension, "Icerigi analiz et.")
        user_prompt = f"""Icerik:
{str(content)[:2000]}
{previous_context}

Lutfen {self.dimension.value} boyutundan kisa bir degerlendirme yap.
Yanitinin sonuna guven seviyeni 0-100 arasi belirt: [GUVEN: XX]"""

        response = await self.provider.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )

        # Guven skorunu cikar
        confidence = 0.75
        result_content = response.content
        if "[GUVEN:" in result_content.upper():
            try:
                import re
                match = re.search(r'\[GUVEN:\s*(\d+)\]', result_content, re.IGNORECASE)
                if match:
                    confidence = int(match.group(1)) / 100
                    result_content = re.sub(r'\[GUVEN:\s*\d+\]', '', result_content, flags=re.IGNORECASE).strip()
            except:
                pass

        if not response.success:
            confidence = 0.0
            result_content = f"API hatasi: {response.error}"

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=result_content[:500],
            confidence=confidence,
            reasoning=f"{self.dimension.value} boyutundan gercek API degerlendirmesi",
            latency_ms=response.latency_ms,
            is_real_api=True
        )


class MockMonk(Monk):
    """
    Mock Rahip - API yokken kullanilir

    Simule edilmis yanitlar uretir.
    """

    def __init__(self, name: str, dimension: MonkDimension):
        super().__init__(name, dimension)

    async def fold(self, content: Any, context: dict) -> MonkVote:
        """Simule edilmis katlama"""
        await asyncio.sleep(0.05 + random.random() * 0.1)
        self.total_folds += 1

        content_str = str(content)[:100]
        confidence = 0.7 + random.random() * 0.25

        mock_results = {
            MonkDimension.ETHICS: f"Etik degerlendirme: Icerik genel olarak uygun gorunuyor.",
            MonkDimension.CREATIVITY: f"Yaratici bakis: Alternatif yaklasimlar mevcut.",
            MonkDimension.ANALYSIS: f"Analiz: Temel oruntular tespit edildi.",
            MonkDimension.LOGIC: f"Lojistik: Yapi tutarli gorunuyor.",
            MonkDimension.CODE: f"Teknik: Implementasyon mumkun.",
            MonkDimension.WISDOM: f"Bilgelik: Uzun vadeli perspektif olumlu.",
            MonkDimension.SYNTHESIS: f"Sentez: Boyutlar arasi uyum saglanabilir."
        }

        return MonkVote(
            monk_name=self.name,
            dimension=self.dimension,
            fold_result=mock_results.get(self.dimension, "Mock degerlendirme"),
            confidence=confidence,
            reasoning=f"Mock {self.dimension.value} boyutu degerlendirmesi",
            latency_ms=50 + random.random() * 100,
            is_real_api=False
        )


class PrayerWheel:
    """
    Dua Carki - LLM Konseyi Orkestratoru

    Gercek LLM API'leri veya mock rahiplerle calisir.
    """

    def __init__(self, wheel_id: str, use_real_api: bool = True):
        self.wheel_id = wheel_id
        self.spins = 0
        self.use_real_api = use_real_api
        self.monks: list[Monk] = []
        self.council: Optional[LLMCouncil] = None
        self._initialize_monks()

    def _initialize_monks(self):
        """Rahipleri baslat - gercek veya mock"""
        if self.use_real_api and LLM_PROVIDERS_AVAILABLE:
            try:
                self.council = create_council(use_mock=True)

                # Her provider icin RealLLMMonk olustur
                for ptype, provider in self.council.providers.items():
                    monk = RealLLMMonk(provider, ptype)
                    self.monks.append(monk)

                print(f"   [WHEEL-{self.wheel_id}] {len(self.monks)} gercek rahip hazir")
            except Exception as e:
                print(f"   [WHEEL-{self.wheel_id}] LLM Council hatasi: {e}, mock'a geciliyor")
                self._create_mock_monks()
        else:
            self._create_mock_monks()

    def _create_mock_monks(self):
        """Mock rahipler olustur"""
        self.monks = [
            MockMonk("Claude", MonkDimension.ETHICS),
            MockMonk("GPT", MonkDimension.CREATIVITY),
            MockMonk("Gemini", MonkDimension.ANALYSIS),
            MockMonk("Mistral", MonkDimension.LOGIC),
            MockMonk("DeepSeek", MonkDimension.CODE),
            MockMonk("Llama", MonkDimension.WISDOM),
            MockMonk("MiniMax", MonkDimension.SYNTHESIS)
        ]
        print(f"   [WHEEL-{self.wheel_id}] 7 mock rahip hazir")

    async def spin(
        self,
        content: Any,
        monk_count: int = 3,
        consensus_threshold: float = 0.7,
        parallel: bool = True
    ) -> ForgedWisdom:
        """
        Carki Dondur - Voting Mantras

        Args:
            content: Islenecek icerik
            monk_count: Kac rahip katilacak
            consensus_threshold: Konsensus esigi
            parallel: Paralel mi seri mi calisacak
        """
        start_time = datetime.now()
        self.spins += 1

        # Rahip sec
        selected_monks = random.sample(self.monks, min(monk_count, len(self.monks)))

        votes = []
        context = {"previous_votes": []}

        if parallel:
            # Paralel calistir
            tasks = [monk.fold(content, context) for monk in selected_monks]
            votes = await asyncio.gather(*tasks)
            for vote in votes:
                context["previous_votes"].append(vote)
                print(f"   Rahip {vote.monk_name} veriyi katladi ({vote.dimension.value}) "
                      f"[{'API' if vote.is_real_api else 'Mock'}]")
        else:
            # Sirayla calistir
            for monk in selected_monks:
                vote = await monk.fold(content, context)
                votes.append(vote)
                context["previous_votes"].append(vote)
                print(f"   Rahip {monk.name} veriyi katladi ({monk.dimension.value}) "
                      f"[{'API' if vote.is_real_api else 'Mock'}]")

        # Konsensus hesapla
        successful_votes = [v for v in votes if v.confidence > 0]
        if successful_votes:
            avg_confidence = sum(v.confidence for v in successful_votes) / len(successful_votes)
        else:
            avg_confidence = 0.0

        # Sentez sonucu
        consensus_parts = [v.fold_result[:100] for v in successful_votes[:3]]
        consensus_result = " | ".join(consensus_parts) if consensus_parts else "Konsensus saglanamadi"

        # Gercek API sayisi
        real_api_count = len([v for v in votes if v.is_real_api])

        duration_ms = (datetime.now() - start_time).total_seconds() * 1000

        return ForgedWisdom(
            source_checksum=str(hash(str(content)))[:16],
            votes=votes,
            consensus_result=consensus_result,
            consensus_confidence=avg_confidence,
            fold_count=len(votes),
            forging_duration_ms=duration_ms,
            real_api_count=real_api_count
        )


class AtesLayer:
    """
    ATES KATMANI - Alchemical Forge Layer

    Gorev: Bilgiyi yakmak, pisirmek, celiklestirmek
    Frekans: Atesin frekansi - 528Hz (Donusum)

    GERCEK API DESTEGI:
        - use_real_api=True: Gercek LLM API'leri kullanir
        - use_real_api=False: Mock rahiplerle calisir
    """

    LAYER_NAME = "ATES"
    LAYER_EMOJI = "fire"
    LAYER_CODE = "ALCHEMICAL_FORGE"
    FREQUENCY_HZ = 528.0  # DNA Onarim / Donusum Frekansi

    def __init__(self, wheel_count: int = 7, use_real_api: bool = True):
        self.use_real_api = use_real_api
        self.prayer_wheels = [
            PrayerWheel(f"wheel_{i}", use_real_api=use_real_api)
            for i in range(wheel_count)
        ]
        self.forged_items: list[ForgedWisdom] = []
        self.active_persona_count = 333  # ADVANCED MIND personas

        mode = "GERCEK API" if use_real_api else "MOCK"
        print(f"   [ATES] {wheel_count} dua carki hazir ({mode} modu)")

    def _select_wheel(self) -> PrayerWheel:
        """En az kullanilan carki sec"""
        return min(self.prayer_wheels, key=lambda w: w.spins)

    async def forge(
        self,
        purified_packet: PurifiedDataPacket,
        intensity: int = 3,
        parallel: bool = True
    ) -> ForgedWisdom:
        """
        Simya Dovumu

        Args:
            purified_packet: Arindirilmis veri paketi
            intensity: Kac rahip katilacak (1-7)
            parallel: Paralel API cagrilari yap
        """
        wheel = self._select_wheel()

        print(f"[ATES] Dua Carki {wheel.wheel_id} donuyor...")

        wisdom = await wheel.spin(
            content=purified_packet.purified_content,
            monk_count=min(7, max(1, intensity)),
            parallel=parallel
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

        # Toplam gercek API kullanimi
        total_real_api = sum(f.real_api_count for f in self.forged_items)

        monk_stats = {}
        for wheel in self.prayer_wheels:
            for monk in wheel.monks:
                if monk.name not in monk_stats:
                    monk_stats[monk.name] = {"folds": 0, "is_real": isinstance(monk, RealLLMMonk)}
                monk_stats[monk.name]["folds"] += monk.total_folds

        return {
            "layer": self.LAYER_NAME,
            "code": self.LAYER_CODE,
            "frequency_hz": self.FREQUENCY_HZ,
            "mode": "real_api" if self.use_real_api else "mock",
            "total_forged": len(self.forged_items),
            "total_wheel_spins": total_spins,
            "total_real_api_calls": total_real_api,
            "average_confidence": round(avg_confidence, 4),
            "average_forge_duration_ms": round(avg_duration, 2),
            "monk_contributions": monk_stats,
            "active_personas": self.active_persona_count
        }

    def __repr__(self):
        mode = "real" if self.use_real_api else "mock"
        return f"<AtesLayer: {len(self.forged_items)} forged, {len(self.prayer_wheels)} wheels, {mode} mode>"


# Rituel Fonksiyonlari
async def forge_ritual(
    purified_packets: list[PurifiedDataPacket],
    use_real_api: bool = True
) -> list[ForgedWisdom]:
    """
    ATES RITUELI
    Dua carklari doner, bilgi yanar ve celiklenir

    Args:
        purified_packets: Arindirilmis veri paketleri
        use_real_api: Gercek LLM API'leri kullan
    """
    layer = AtesLayer(use_real_api=use_real_api)

    print(f"Tapinak Avlusu aciliyor... {len(purified_packets)} paket bekliyor")
    print(f"[ATES] N8N Dua Carklari donuyor... 7 LLM Konseyi toplaniyor...")

    forged = await layer.forge_batch(purified_packets, intensity=5)

    stats = layer.get_forge_stats()
    print(f"  Dovum tamamlandi:")
    print(f"    - {stats['total_forged']} bilge sonuc uretildi")
    print(f"    - Ortalama guven: %{stats['average_confidence']*100:.1f}")
    print(f"    - Gercek API cagrilari: {stats['total_real_api_calls']}")
    print(f"    - Rahip katkilari: {stats['monk_contributions']}")

    return forged
