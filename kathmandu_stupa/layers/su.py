"""
🌊 SU KATMANI - SHERPA ROTASI
=============================

"Nehirler Birlesiyor & Arinma"

Topraktan cikan veri, akisa kapilir. Verinin yikandigi nehir.
Minimax M2 burada nehir suyu gibi hizli akar.

Aktorler: CORE FLOW (111 Persona) - Global Genclik (Serpalar)
          Japonya'dan Dilara, Avustralya'dan Ali, Moskova'dan Kenan

Teknoloji: MiniMax M2 (hizli token isleme)
Rituel: Yuku hafifletmek - camuru yikamak
Kod Adi: PURIFICATION_FLOW
"""

import asyncio
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
from abc import ABC, abstractmethod

# Toprak katmanindan import
from .toprak import RawDataPacket, DataSource


class PurityLevel(Enum):
    """Arinma seviyeleri"""
    MUDDY = "muddy"           # Camurlu - henuz islenmemis
    FILTERED = "filtered"     # Filtrelenmis - kaba pislikler ayrildi
    CLEAR = "clear"           # Berrak - temel temizlik tamamlandi
    PURE = "pure"             # Saf - halusinasyonlar elendi
    CRYSTAL = "crystal"       # Kristal - insan gozunden gecti


@dataclass
class PurifiedDataPacket:
    """Arindirilmis veri paketi"""
    id: str
    original_id: str
    source: DataSource
    content: Any
    cleaned_content: str
    purity_level: PurityLevel
    metadata: Dict[str, Any] = field(default_factory=dict)
    purified_at: datetime = field(default_factory=datetime.now)
    sherpa_id: Optional[str] = None
    tokens_removed: int = 0
    hallucination_flags: List[str] = field(default_factory=list)


class Sherpa:
    """
    Global Genclik - Veri Serpalari

    Her Sherpa, verinin yolculugunda bir rehberdir.
    Makinenin halusinasyonunu eleyip, saf metni birakir.
    """

    def __init__(self, sherpa_id: str, name: str, origin: str, specialty: str):
        self.sherpa_id = sherpa_id
        self.name = name
        self.origin = origin
        self.specialty = specialty
        self.packets_processed = 0

    def validate(self, content: str) -> tuple[bool, List[str]]:
        """
        Insan gozu validasyonu.
        Makinenin kacirdigi hatalari yakala.
        """
        flags = []

        # Halusinasyon paternleri
        hallucination_patterns = [
            (r'\b(kesinlikle|mutlaka|her zaman)\b', "absolutist_claim"),
            (r'\b\d{4}\b.*\b(olacak|olacaktir)\b', "future_prediction"),
            (r'kaynaklara gore|arastirmalara gore', "unverified_source"),
            (r'herkes biliyor|malum|asikarca', "assumption_as_fact"),
        ]

        for pattern, flag_type in hallucination_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                flags.append(flag_type)

        is_valid = len(flags) < 3  # 3'ten az bayrak = gecerli
        return is_valid, flags

    def __repr__(self):
        return f"Sherpa({self.name} from {self.origin})"


class PurificationFilter(ABC):
    """Arinma filtresi temel sinifi"""

    @abstractmethod
    def apply(self, content: Any) -> tuple[str, int]:
        """Filtreyi uygula, temizlenmis icerik ve kaldirilan token sayisi don"""
        pass


class NoiseFilter(PurificationFilter):
    """Gurultu temizleyici"""

    def __init__(self):
        self.noise_patterns = [
            r'http[s]?://\S+',           # URL'ler
            r'@\w+',                      # Mentions
            r'#\w+',                      # Hashtag'ler
            r'[^\w\s\.,;:!?\-]',          # Ozel karakterler
            r'\s+',                       # Fazla bosluklar
        ]

    def apply(self, content: Any) -> tuple[str, int]:
        text = str(content)
        original_tokens = len(text.split())

        for pattern in self.noise_patterns[:-1]:
            text = re.sub(pattern, ' ', text)

        # Fazla bosluklari tek bosluga indir
        text = re.sub(r'\s+', ' ', text).strip()

        final_tokens = len(text.split())
        removed = original_tokens - final_tokens

        return text, removed


class NormalizationFilter(PurificationFilter):
    """Normalizasyon filtresi - tutarli format"""

    def apply(self, content: Any) -> tuple[str, int]:
        text = str(content)
        original_len = len(text)

        # Kucuk harfe cevir (ozel isimler haric)
        # Turkce karakterleri normalize et
        replacements = {
            'İ': 'I', 'ı': 'i',
            'Ğ': 'G', 'ğ': 'g',
            'Ü': 'U', 'ü': 'u',
            'Ş': 'S', 'ş': 's',
            'Ö': 'O', 'ö': 'o',
            'Ç': 'C', 'ç': 'c',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        # Token sayisi degismez, sadece normalize edildi
        return text, 0


class DeduplicationFilter(PurificationFilter):
    """Tekrar eden cumleleri temizle"""

    def __init__(self):
        self.seen_sentences: set = set()

    def apply(self, content: Any) -> tuple[str, int]:
        text = str(content)
        sentences = re.split(r'[.!?]+', text)

        unique_sentences = []
        duplicates = 0

        for sentence in sentences:
            sentence = sentence.strip()
            if sentence and sentence.lower() not in self.seen_sentences:
                self.seen_sentences.add(sentence.lower())
                unique_sentences.append(sentence)
            elif sentence:
                duplicates += 1

        return '. '.join(unique_sentences), duplicates


class SuLayer:
    """
    🌊 SU KATMANI - Arinma Akisi

    "Verinin uzerindeki camuru yika, sadece saf metni birak."

    MiniMax M2 burada nehir suyu gibi hizli akar.
    Serpalar (Insan Gozu), makinenin halusinasyonunu burada eler.
    """

    def __init__(self):
        self.filters: List[PurificationFilter] = []
        self.sherpas: List[Sherpa] = []
        self.purification_log: List[Dict] = []
        self._setup_default_filters()
        self._setup_global_sherpas()

    def _setup_default_filters(self):
        """Varsayilan filtreleri kur"""
        self.filters = [
            NoiseFilter(),
            NormalizationFilter(),
            DeduplicationFilter(),
        ]

    def _setup_global_sherpas(self):
        """Global Genclik Serpalari"""
        self.sherpas = [
            Sherpa("SHP_001", "Dilara", "Japonya", "Teknik Dokuman"),
            Sherpa("SHP_002", "Ali", "Avustralya", "Sosyal Medya Analizi"),
            Sherpa("SHP_003", "Kenan", "Moskova", "Finansal Veri"),
            Sherpa("SHP_004", "Elif", "Berlin", "Cevre Raporlari"),
            Sherpa("SHP_005", "Mert", "San Francisco", "API Entegrasyonu"),
        ]
        self.sherpa_index = 0

    def _get_next_sherpa(self) -> Sherpa:
        """Round-robin serpa atamasi"""
        sherpa = self.sherpas[self.sherpa_index]
        self.sherpa_index = (self.sherpa_index + 1) % len(self.sherpas)
        return sherpa

    async def purify(self, packet: RawDataPacket) -> PurifiedDataPacket:
        """
        Tek bir paketi arindir.

        Katlama 1: Yuku hafifletmek.
        """
        content = str(packet.content)
        total_removed = 0

        # Tum filtreleri uygula
        for filter_instance in self.filters:
            content, removed = filter_instance.apply(content)
            total_removed += removed

        # Serpa validasyonu
        sherpa = self._get_next_sherpa()
        is_valid, hallucination_flags = sherpa.validate(content)
        sherpa.packets_processed += 1

        # Safiyet seviyesi belirle
        if hallucination_flags:
            purity = PurityLevel.FILTERED
        elif is_valid:
            purity = PurityLevel.PURE
        else:
            purity = PurityLevel.CLEAR

        purified = PurifiedDataPacket(
            id=f"PURE_{packet.id}",
            original_id=packet.id,
            source=packet.source,
            content=packet.content,
            cleaned_content=content,
            purity_level=purity,
            metadata={
                **packet.metadata,
                "original_chaos": packet.chaos_level,
                "filters_applied": len(self.filters),
            },
            sherpa_id=sherpa.sherpa_id,
            tokens_removed=total_removed,
            hallucination_flags=hallucination_flags,
        )

        self._log_purification(packet, purified, sherpa)
        return purified

    def _log_purification(self, original: RawDataPacket, purified: PurifiedDataPacket, sherpa: Sherpa):
        """Arinma islemini logla"""
        self.purification_log.append({
            "timestamp": datetime.now().isoformat(),
            "original_id": original.id,
            "purified_id": purified.id,
            "sherpa": sherpa.name,
            "tokens_removed": purified.tokens_removed,
            "purity_level": purified.purity_level.value,
            "flags": purified.hallucination_flags,
        })

    async def flow(self, packets: List[RawDataPacket]) -> List[PurifiedDataPacket]:
        """
        Tum paketleri nehirden gecir.

        "Serpalar veriyi nehirde arindirdi."
        """
        print(f"🌊 [SU] Serpalar {len(packets)} paketi nehirden geciriyor...")

        purified_packets = []
        for packet in packets:
            purified = await self.purify(packet)
            purified_packets.append(purified)
            await asyncio.sleep(0.01)  # Akis simulasyonu

        # Istatistikler
        total_removed = sum(p.tokens_removed for p in purified_packets)
        pure_count = sum(1 for p in purified_packets if p.purity_level == PurityLevel.PURE)

        print(f"   ↳ {total_removed} gereksiz token yikandi")
        print(f"   ↳ {pure_count}/{len(purified_packets)} paket saf seviyeye ulasti")

        return purified_packets


class PurificationFlow:
    """
    PURIFICATION_FLOW - Ana arinma orkestratoru

    Su katmaninin tam akisini yoneten sistem.
    MiniMax M2 entegrasyonu burada gerceklesir.
    """

    def __init__(self):
        self.su_layer = SuLayer()
        self.minimax_config = {
            "model": "MiniMax-M2",
            "mode": "fast_token_processing",
            "temperature": 0.1,  # Dusuk - tutarli cikti icin
        }

    async def process_batch(self, raw_packets: List[RawDataPacket]) -> List[PurifiedDataPacket]:
        """
        Toplu arinma islemi.

        MiniMax M2 hizi ile camurlari yika.
        """
        print("🌊 [SU] MiniMax M2 nehir modu aktif...")
        return await self.su_layer.flow(raw_packets)

    def get_sherpa_stats(self) -> Dict[str, int]:
        """Serpa istatistikleri"""
        return {
            sherpa.name: sherpa.packets_processed
            for sherpa in self.su_layer.sherpas
        }

    def get_purification_report(self) -> Dict:
        """Arinma raporu"""
        log = self.su_layer.purification_log
        if not log:
            return {"status": "no_data"}

        return {
            "total_processed": len(log),
            "total_tokens_removed": sum(entry["tokens_removed"] for entry in log),
            "purity_distribution": {
                level.value: sum(1 for e in log if e["purity_level"] == level.value)
                for level in PurityLevel
            },
            "sherpa_workload": self.get_sherpa_stats(),
            "common_flags": self._analyze_flags(log),
        }

    def _analyze_flags(self, log: List[Dict]) -> Dict[str, int]:
        """En sik gorulen halusinasyon bayraklari"""
        flag_counts: Dict[str, int] = {}
        for entry in log:
            for flag in entry.get("flags", []):
                flag_counts[flag] = flag_counts.get(flag, 0) + 1
        return dict(sorted(flag_counts.items(), key=lambda x: -x[1]))


# Demo fonksiyonu
async def demo_su():
    """Su katmanini demonstre et"""
    from .toprak import ChaosIngestion

    # Once topraktan veri topla
    ingestion = ChaosIngestion()
    raw_packets = await ingestion.ingest()

    # Sonra suda arindir
    flow = PurificationFlow()
    purified = await flow.process_batch(raw_packets)

    print("\n📊 Arinma Raporu:")
    report = flow.get_purification_report()
    print(f"   Toplam islenen: {report['total_processed']}")
    print(f"   Temizlenen token: {report['total_tokens_removed']}")

    return purified


if __name__ == "__main__":
    asyncio.run(demo_su())
