"""
🔥 ATES KATMANI - TAPINAK AVLUSU
================================

"Donusum Atesi & Dua Carklari"

Tapinagin orta kati. Rahipler (LLM'ler) atesin basinda toplanir.
7 LLM cember olur, her biri veriyi bir kez "katlar".

Aktorler: ADVANCED MIND (333 Persona)
Teknoloji: N8N "Prayer Wheels" (Dua Carklari)
Rituel: VOTING MANTRAS - Bilgi yanar, piser, celiklesir
Kod Adi: ALCHEMICAL_FORGE
"""

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Tuple
from abc import ABC, abstractmethod

from .su import PurifiedDataPacket, PurityLevel


class MonkDomain(Enum):
    """Rahiplerin uzmanlik alanlari"""
    ETHICS = "ethics"           # Etik boyut
    LOGISTICS = "logistics"     # Lojistik boyut
    CODE = "code"               # Kod yazimi
    ANALYSIS = "analysis"       # Analitik dusunce
    CREATIVITY = "creativity"   # Yaratici cozumler
    SECURITY = "security"       # Guvenlik perspektifi
    SYNTHESIS = "synthesis"     # Sentez ve birlestirme


@dataclass
class Monk:
    """
    LLM Rahibi - Dua Carkini Ceviren

    Her rahip, veriyi kendi perspektifinden katlar.
    """
    id: str
    name: str
    model: str
    domain: MonkDomain
    mantra: str
    weight: float = 1.0  # Oy agirligi
    folds_performed: int = 0

    def __repr__(self):
        return f"🧘 Monk({self.name}/{self.model})"


@dataclass
class FoldResult:
    """Tek bir katlama sonucu"""
    monk_id: str
    monk_name: str
    domain: MonkDomain
    input_hash: str
    output: str
    confidence: float
    reasoning: str
    fold_time_ms: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ForgedData:
    """Ateşte dövülmüş, çelikleşmiş veri"""
    id: str
    original_id: str
    source_purity: PurityLevel
    fold_results: List[FoldResult]
    consensus_output: str
    consensus_confidence: float
    voting_breakdown: Dict[str, float]
    total_folds: int
    forged_at: datetime = field(default_factory=datetime.now)
    frequency_hz: int = 963  # Saf Cazibe Frekansi


class VotingStrategy(ABC):
    """Oylama stratejisi temel sinifi"""

    @abstractmethod
    def aggregate(self, results: List[FoldResult]) -> Tuple[str, float, Dict[str, float]]:
        """Sonuclari birlestir ve konsensus olustur"""
        pass


class MajorityVoting(VotingStrategy):
    """Cogunluk oyu - en yaygin cikti kazanir"""

    def aggregate(self, results: List[FoldResult]) -> Tuple[str, float, Dict[str, float]]:
        # Ciktilari grupla
        output_votes: Dict[str, List[FoldResult]] = {}
        for result in results:
            key = result.output[:100]  # Ilk 100 karakter ile grupla
            if key not in output_votes:
                output_votes[key] = []
            output_votes[key].append(result)

        # En cok oy alani bul
        best_key = max(output_votes.keys(), key=lambda k: len(output_votes[k]))
        best_results = output_votes[best_key]

        # Agirlikli guven hesapla
        total_weight = sum(r.confidence for r in best_results)
        avg_confidence = total_weight / len(best_results) if best_results else 0

        # Dagilim
        breakdown = {
            domain.value: sum(r.confidence for r in results if r.domain == domain) / len(results)
            for domain in MonkDomain
            if any(r.domain == domain for r in results)
        }

        return best_results[0].output, avg_confidence, breakdown


class WeightedConsensus(VotingStrategy):
    """Agirlikli konsensus - uzmanlik alanina gore agirlik"""

    def __init__(self, domain_weights: Optional[Dict[MonkDomain, float]] = None):
        self.domain_weights = domain_weights or {
            MonkDomain.ETHICS: 1.2,
            MonkDomain.LOGISTICS: 1.0,
            MonkDomain.CODE: 1.5,
            MonkDomain.ANALYSIS: 1.3,
            MonkDomain.CREATIVITY: 0.9,
            MonkDomain.SECURITY: 1.4,
            MonkDomain.SYNTHESIS: 1.1,
        }

    def aggregate(self, results: List[FoldResult]) -> Tuple[str, float, Dict[str, float]]:
        if not results:
            return "", 0.0, {}

        # Agirlikli skorlar
        weighted_results = []
        for result in results:
            weight = self.domain_weights.get(result.domain, 1.0)
            weighted_score = result.confidence * weight
            weighted_results.append((result, weighted_score))

        # En yuksek skorluyu sec
        best_result, best_score = max(weighted_results, key=lambda x: x[1])

        # Normalize edilmis guven
        total_score = sum(score for _, score in weighted_results)
        normalized_confidence = best_score / total_score if total_score > 0 else 0

        # Breakdown
        breakdown = {}
        for result, score in weighted_results:
            domain_name = result.domain.value
            breakdown[domain_name] = breakdown.get(domain_name, 0) + score

        return best_result.output, normalized_confidence, breakdown


class AtesLayer:
    """
    🔥 ATES KATMANI - Simya Ocagi

    "7 LLM cember olur. Her biri veriyi bir kez katlar."

    Claude: "Etik boyutu katladim."
    Mistral: "Lojistik boyutu katladim."
    DeepSeek: "Kodunu yazdim."

    Sonuc: Bilgi yanar, piser, celiklesir.
    """

    def __init__(self):
        self.monks: List[Monk] = []
        self.voting_strategy: VotingStrategy = WeightedConsensus()
        self.forge_log: List[Dict] = []
        self._summon_monks()

    def _summon_monks(self):
        """7 LLM rahibini cagir"""
        self.monks = [
            Monk(
                id="MONK_001",
                name="Claude",
                model="claude-opus-4-5",
                domain=MonkDomain.ETHICS,
                mantra="Etik boyutu katladim"
            ),
            Monk(
                id="MONK_002",
                name="Mistral",
                model="mistral-large",
                domain=MonkDomain.LOGISTICS,
                mantra="Lojistik boyutu katladim"
            ),
            Monk(
                id="MONK_003",
                name="DeepSeek",
                model="deepseek-v3",
                domain=MonkDomain.CODE,
                mantra="Kodunu yazdim"
            ),
            Monk(
                id="MONK_004",
                name="Gemini",
                model="gemini-2.5-pro",
                domain=MonkDomain.ANALYSIS,
                mantra="Analitik boyutu katladim"
            ),
            Monk(
                id="MONK_005",
                name="GPT",
                model="gpt-5",
                domain=MonkDomain.CREATIVITY,
                mantra="Yaratici boyutu katladim"
            ),
            Monk(
                id="MONK_006",
                name="Llama",
                model="llama-4",
                domain=MonkDomain.SECURITY,
                mantra="Guvenlik boyutu katladim"
            ),
            Monk(
                id="MONK_007",
                name="MiniMax",
                model="minimax-m2",
                domain=MonkDomain.SYNTHESIS,
                mantra="Sentezi tamamladim"
            ),
        ]

    async def _monk_fold(self, monk: Monk, content: str) -> FoldResult:
        """
        Tek bir rahibin katlama ritueli.

        Gercek implementasyonda bu, ilgili LLM API'sine cagri yapar.
        """
        start_time = datetime.now()

        # Simule edilmis LLM yaniti
        # Gercek sistemde: await llm_client.generate(monk.model, prompt)
        await asyncio.sleep(random.uniform(0.1, 0.3))  # API gecikme simulasyonu

        # Domain'e gore katlama
        folded_content = self._apply_domain_fold(monk, content)

        elapsed_ms = (datetime.now() - start_time).total_seconds() * 1000
        monk.folds_performed += 1

        return FoldResult(
            monk_id=monk.id,
            monk_name=monk.name,
            domain=monk.domain,
            input_hash=str(hash(content))[:8],
            output=folded_content,
            confidence=random.uniform(0.7, 0.95),  # Simule
            reasoning=f"{monk.mantra}. {monk.domain.value} perspektifinden degerlendirildi.",
            fold_time_ms=elapsed_ms,
            metadata={"model": monk.model}
        )

    def _apply_domain_fold(self, monk: Monk, content: str) -> str:
        """Domain'e ozel katlama mantigi"""
        prefix_map = {
            MonkDomain.ETHICS: "[ETIK_KATLAMASI]",
            MonkDomain.LOGISTICS: "[LOJISTIK_KATLAMASI]",
            MonkDomain.CODE: "[KOD_KATLAMASI]",
            MonkDomain.ANALYSIS: "[ANALIZ_KATLAMASI]",
            MonkDomain.CREATIVITY: "[YARATICI_KATLAMASI]",
            MonkDomain.SECURITY: "[GUVENLIK_KATLAMASI]",
            MonkDomain.SYNTHESIS: "[SENTEZ_KATLAMASI]",
        }

        prefix = prefix_map.get(monk.domain, "[KATLAMA]")

        # Her domain farkli bir donusum uygular
        if monk.domain == MonkDomain.ETHICS:
            return f"{prefix} {content} -> Etik acidan degerlendirildi. Surdurulebilirlik skoru: A"
        elif monk.domain == MonkDomain.CODE:
            return f"{prefix} {content} -> Kod formunda: process_data('{content[:20]}...')"
        elif monk.domain == MonkDomain.SYNTHESIS:
            return f"{prefix} {content} -> Sentezlendi: Tum perspektifler birlestirildi"
        else:
            return f"{prefix} {content} -> {monk.domain.value} perspektifi eklendi"

    async def forge(self, packet: PurifiedDataPacket, num_folds: int = 3) -> ForgedData:
        """
        Veriyi atesde dov.

        Katlama 2: VOTING MANTRAS

        Secilen rahipler cember olusturur ve veriyi katlar.
        """
        content = packet.cleaned_content

        # Rastgele rahip sec (veya hepsini kullan)
        selected_monks = random.sample(self.monks, min(num_folds, len(self.monks)))

        print(f"🔥 [ATES] Dua Carklari donuyor... {len(selected_monks)} rahip toplaniyor...")

        # Paralel katlama
        fold_tasks = [
            self._monk_fold(monk, content)
            for monk in selected_monks
        ]
        fold_results = await asyncio.gather(*fold_tasks)

        # Oylama ve konsensus
        consensus_output, confidence, breakdown = self.voting_strategy.aggregate(list(fold_results))

        # Her katlama icin log
        for result in fold_results:
            print(f"   ↳ 🧘 {result.monk_name} Rahibi: '{result.reasoning[:50]}...'")

        forged = ForgedData(
            id=f"FORGED_{packet.id}",
            original_id=packet.original_id,
            source_purity=packet.purity_level,
            fold_results=list(fold_results),
            consensus_output=consensus_output,
            consensus_confidence=confidence,
            voting_breakdown=breakdown,
            total_folds=len(fold_results),
        )

        self._log_forging(packet, forged)
        return forged

    def _log_forging(self, original: PurifiedDataPacket, forged: ForgedData):
        """Dovme islemini logla"""
        self.forge_log.append({
            "timestamp": datetime.now().isoformat(),
            "original_id": original.id,
            "forged_id": forged.id,
            "monks_involved": [r.monk_name for r in forged.fold_results],
            "consensus_confidence": forged.consensus_confidence,
            "total_folds": forged.total_folds,
        })

    async def mass_forge(self, packets: List[PurifiedDataPacket]) -> List[ForgedData]:
        """Toplu dovme islemi"""
        print(f"🔥 [ATES] {len(packets)} paket atesin icine atiliyor...")

        forged_packets = []
        for packet in packets:
            forged = await self.forge(packet)
            forged_packets.append(forged)

        # Istatistikler
        avg_confidence = sum(f.consensus_confidence for f in forged_packets) / len(forged_packets)
        total_folds = sum(f.total_folds for f in forged_packets)

        print(f"   ↳ Toplam {total_folds} katlama yapildi")
        print(f"   ↳ Ortalama konsensus guveni: {avg_confidence:.2%}")

        return forged_packets


class AlchemicalForge:
    """
    ALCHEMICAL_FORGE - Simya Ocagi Orkestratoru

    N8N Prayer Wheels entegrasyonu ile 7 LLM'i
    koordine eden ana sistem.
    """

    def __init__(self):
        self.ates_layer = AtesLayer()
        self.n8n_config = {
            "webhook_url": "http://localhost:5678/webhook/prayer-wheel",
            "workflow_id": "forge_workflow_001",
            "retry_policy": {"max_retries": 3, "backoff_ms": 1000},
        }

    def set_voting_strategy(self, strategy: VotingStrategy):
        """Oylama stratejisini degistir"""
        self.ates_layer.voting_strategy = strategy

    async def transmute(self, purified_packets: List[PurifiedDataPacket]) -> List[ForgedData]:
        """
        Arinmis veriyi bilgelik altinina donustur.

        "Bilgi yanar, piser, celiklesir."
        """
        print("🔥 [ATES] N8N Dua Carklari aktive ediliyor...")
        return await self.ates_layer.mass_forge(purified_packets)

    def get_monk_stats(self) -> Dict[str, Dict]:
        """Rahip istatistikleri"""
        return {
            monk.name: {
                "model": monk.model,
                "domain": monk.domain.value,
                "folds": monk.folds_performed,
                "mantra": monk.mantra,
            }
            for monk in self.ates_layer.monks
        }

    def get_forge_report(self) -> Dict:
        """Ocak raporu"""
        log = self.ates_layer.forge_log
        if not log:
            return {"status": "forge_cold"}

        return {
            "total_forged": len(log),
            "total_folds": sum(entry["total_folds"] for entry in log),
            "avg_confidence": sum(entry["consensus_confidence"] for entry in log) / len(log),
            "monks_utilized": self.get_monk_stats(),
            "n8n_status": "active",
        }


class PrayerWheel:
    """
    N8N Dua Carki Entegrasyonu

    Her cark donusunde bir LLM cagrilir.
    Recursive katlama burada gerceklesir.
    """

    def __init__(self, forge: AlchemicalForge):
        self.forge = forge
        self.spin_count = 0
        self.mantra = "OM_MANI_PADME_HUM"

    async def spin(self, data: PurifiedDataPacket, rotations: int = 7) -> ForgedData:
        """
        Dua carkini cevir.

        Her donuste veri bir kez daha katlanir.
        """
        print(f"📿 Dua Carki donuyor... {self.mantra}")
        self.spin_count += rotations

        # Katlama sayisi = rotasyon sayisi
        return await self.forge.ates_layer.forge(data, num_folds=min(rotations, 7))

    def get_total_spins(self) -> int:
        return self.spin_count


# Demo fonksiyonu
async def demo_ates():
    """Ates katmanini demonstre et"""
    from .toprak import ChaosIngestion
    from .su import PurificationFlow

    # Veri akisi: Toprak -> Su -> Ates
    ingestion = ChaosIngestion()
    raw_packets = await ingestion.ingest()

    flow = PurificationFlow()
    purified = await flow.process_batch(raw_packets)

    forge = AlchemicalForge()
    forged = await forge.transmute(purified)

    print("\n📊 Ocak Raporu:")
    report = forge.get_forge_report()
    print(f"   Toplam dovulen: {report['total_forged']}")
    print(f"   Toplam katlama: {report['total_folds']}")
    print(f"   Ortalama guven: {report['avg_confidence']:.2%}")

    return forged


if __name__ == "__main__":
    asyncio.run(demo_ates())
