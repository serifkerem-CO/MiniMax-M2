"""
SU KATMANI - SHERPA ROTASI
==========================
"Nehirler Birlesiyor & Arinma"

Topraktan cikan veri, akisa kapilir. Verinin yikandigi nehir.
Minimax M2 burada nehir suyu gibi hizli akar.
Verinin uzerindeki "camuru" (gereksiz kelimeleri/tokenlari) yikar.

Aktorler: CORE FLOW (111 Persona) - Global Genclik (Serpalar)
          Japonya'dan Dilara, Avustralya'dan Ali, Moskova'dan Kenan
Rituel: Yuku hafifletmek. Sadece "saf metni" birak.
Kod Adi: PURIFICATION_FLOW
"""

import asyncio
import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json

from .toprak import RawDataPacket


class PurificationLevel(Enum):
    """Arinma Seviyeleri"""
    SURFACE = 1      # Yuzey temizligi
    DEEP = 2         # Derin temizlik
    CRYSTALLINE = 3  # Kristal berrakligi


@dataclass
class SherpaProfile:
    """Serpa Profili - Global Genclik"""
    sherpa_id: str
    name: str
    origin: str
    specialty: str
    experience_level: int = 1
    packets_purified: int = 0


@dataclass
class PurifiedDataPacket:
    """Arindirilmis veri paketi - Nehirden cikan saf su"""
    original_checksum: str
    purified_content: Any
    purification_level: PurificationLevel
    sherpa_id: str
    tokens_removed: int = 0
    noise_ratio: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    hallucination_flags: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "original_checksum": self.original_checksum,
            "purified_content": self.purified_content,
            "purification_level": self.purification_level.name,
            "sherpa_id": self.sherpa_id,
            "tokens_removed": self.tokens_removed,
            "noise_ratio": self.noise_ratio,
            "timestamp": self.timestamp.isoformat(),
            "hallucination_flags": self.hallucination_flags
        }


class HallucinationDetector:
    """
    Halusinasyon Dedektoru
    Makinenin halusnasyonunu Serpa (Insan Gozu) burada eler
    """

    SUSPICIOUS_PATTERNS = [
        r'\b(kesinlikle|mutlaka|her zaman|asla)\b',  # Asiri kesin ifadeler
        r'\d{10,}',  # Cok uzun sayilar (olasi hata)
        r'(.)\1{5,}',  # Tekrar eden karakterler
        r'Lorem ipsum',  # Placeholder metin
        r'TODO|FIXME|XXX',  # Kod kalintilari
    ]

    def __init__(self):
        self.compiled_patterns = [
            re.compile(p, re.IGNORECASE) for p in self.SUSPICIOUS_PATTERNS
        ]

    def detect(self, text: str) -> list[dict]:
        """Supheli kaliplari tespit et"""
        flags = []
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.findall(text)
            if matches:
                flags.append({
                    "pattern_id": i,
                    "matches": matches[:5],  # Ilk 5 eslesme
                    "severity": "warning" if i < 2 else "info"
                })
        return flags


class TokenCleaner:
    """
    Token Temizleyici
    Gereksiz tokenlari/kelimeleri yikar
    """

    NOISE_TOKENS = {
        # Turkce dolgu kelimeleri
        'iste', 'yani', 'simdi', 'ee', 'hani', 'falan', 'filan',
        'sanirim', 'galiba', 'mesela', 'aslinda',
        # Ingilizce dolgu
        'um', 'uh', 'like', 'basically', 'actually', 'literally',
        # Ozel karakterler ve bosluklar
        '\t', '\r', '\xa0'
    }

    PUNCTUATION_CLEANUP = [
        (r'\s+', ' '),           # Coklu bosluk -> tek bosluk
        (r'\n{3,}', '\n\n'),     # 3+ yeni satir -> 2
        (r'\.{4,}', '...'),      # 4+ nokta -> 3
        (r'\s+([.,;:!?])', r'\1'),  # Noktalama oncesi bosluk
    ]

    def clean(self, text: str) -> tuple[str, int]:
        """
        Metni temizle
        Returns: (temiz_metin, kaldirilan_token_sayisi)
        """
        original_len = len(text.split())
        cleaned = text

        # Gurultu tokenlarini kaldir
        for noise in self.NOISE_TOKENS:
            cleaned = cleaned.replace(noise, ' ')

        # Noktalama temizligi
        for pattern, replacement in self.PUNCTUATION_CLEANUP:
            cleaned = re.sub(pattern, replacement, cleaned)

        # Unicode normalizasyonu
        cleaned = unicodedata.normalize('NFKC', cleaned)

        cleaned = cleaned.strip()
        new_len = len(cleaned.split())
        tokens_removed = max(0, original_len - new_len)

        return cleaned, tokens_removed


class SuLayer:
    """
    SU KATMANI - Purification Flow Layer

    Gorev: Ham veriyi arindirmak, camuru yikamak
    Frekans: Suyun frekansi - 432Hz (Harmonik)
    """

    LAYER_NAME = "SU"
    LAYER_EMOJI = "water"
    LAYER_CODE = "PURIFICATION_FLOW"
    FREQUENCY_HZ = 432.0  # Harmonik Frekans

    def __init__(self, sherpa_count: int = 111):
        self.token_cleaner = TokenCleaner()
        self.hallucination_detector = HallucinationDetector()
        self.sherpas = self._initialize_sherpas(sherpa_count)
        self.purified_packets: list[PurifiedDataPacket] = []

    def _initialize_sherpas(self, count: int) -> list[SherpaProfile]:
        """Global Genclik Serpalari"""
        sherpa_pool = [
            ("Dilara", "Japonya", "metin_analizi"),
            ("Ali", "Avustralya", "veri_yapislandirma"),
            ("Kenan", "Moskova", "anomali_tespiti"),
            ("Yuki", "Tokyo", "dil_isleme"),
            ("Maria", "Brezilya", "duygu_analizi"),
            ("Chen", "Singapur", "sayisal_dogrulama"),
        ]

        sherpas = []
        for i in range(count):
            base = sherpa_pool[i % len(sherpa_pool)]
            sherpas.append(SherpaProfile(
                sherpa_id=f"sherpa_{i:03d}",
                name=f"{base[0]}_{i}",
                origin=base[1],
                specialty=base[2],
                experience_level=(i % 5) + 1
            ))
        return sherpas

    def _assign_sherpa(self, packet_complexity: int = 1) -> SherpaProfile:
        """Ise uygun Serpa ata"""
        suitable = [s for s in self.sherpas if s.experience_level >= packet_complexity]
        if not suitable:
            suitable = self.sherpas

        # En az is yapana ver (yuk dengeleme)
        return min(suitable, key=lambda s: s.packets_purified)

    async def purify(
        self,
        raw_packet: RawDataPacket,
        level: PurificationLevel = PurificationLevel.DEEP
    ) -> PurifiedDataPacket:
        """
        Nehir Ritueli - Veriyi arindır
        """
        sherpa = self._assign_sherpa(level.value)

        content = raw_packet.content
        tokens_removed = 0
        hallucination_flags = []
        noise_ratio = 0.0

        # Icerik tipine gore arinma
        if isinstance(content, dict):
            if "raw_text" in content:
                text = content["raw_text"]
                original_len = len(text)

                # Token temizligi
                cleaned_text, tokens_removed = self.token_cleaner.clean(text)

                # Halusnasyon kontrolu
                hallucination_flags = self.hallucination_detector.detect(cleaned_text)

                # Gurultu orani hesapla
                noise_ratio = tokens_removed / max(1, len(text.split()))

                content = {
                    "purified_text": cleaned_text,
                    "original_char_count": original_len,
                    "purified_char_count": len(cleaned_text)
                }
            else:
                # JSON/dict temizligi
                content = self._clean_dict(content)

        elif isinstance(content, str):
            cleaned_text, tokens_removed = self.token_cleaner.clean(content)
            hallucination_flags = self.hallucination_detector.detect(cleaned_text)
            content = cleaned_text

        # Serpa'nin is sayacini guncelle
        sherpa.packets_purified += 1

        # Arınma simulasyonu (nehirde yikanma suresi)
        await asyncio.sleep(0.05 * level.value)

        purified = PurifiedDataPacket(
            original_checksum=raw_packet.checksum,
            purified_content=content,
            purification_level=level,
            sherpa_id=sherpa.sherpa_id,
            tokens_removed=tokens_removed,
            noise_ratio=noise_ratio,
            hallucination_flags=hallucination_flags
        )

        self.purified_packets.append(purified)
        return purified

    def _clean_dict(self, d: dict) -> dict:
        """Sozluk temizligi - None ve bos degerleri at"""
        cleaned = {}
        for k, v in d.items():
            if v is None or v == "" or v == []:
                continue
            if isinstance(v, dict):
                v = self._clean_dict(v)
            if isinstance(v, str):
                v, _ = self.token_cleaner.clean(v)
            cleaned[k] = v
        return cleaned

    async def purify_batch(
        self,
        packets: list[RawDataPacket],
        level: PurificationLevel = PurificationLevel.DEEP
    ) -> list[PurifiedDataPacket]:
        """Toplu arinma - Nehir yatagi"""
        tasks = [self.purify(p, level) for p in packets]
        return await asyncio.gather(*tasks)

    def get_flow_stats(self) -> dict:
        """Nehir istatistikleri"""
        total_tokens_removed = sum(p.tokens_removed for p in self.purified_packets)
        avg_noise = (
            sum(p.noise_ratio for p in self.purified_packets) /
            max(1, len(self.purified_packets))
        )

        hallucination_count = sum(
            len(p.hallucination_flags) for p in self.purified_packets
        )

        return {
            "layer": self.LAYER_NAME,
            "code": self.LAYER_CODE,
            "frequency_hz": self.FREQUENCY_HZ,
            "total_purified": len(self.purified_packets),
            "total_tokens_removed": total_tokens_removed,
            "average_noise_ratio": round(avg_noise, 4),
            "hallucinations_detected": hallucination_count,
            "active_sherpas": len([s for s in self.sherpas if s.packets_purified > 0])
        }

    def __repr__(self):
        return f"<SuLayer: {len(self.purified_packets)} purified, {len(self.sherpas)} sherpas>"


# Rituel Fonksiyonlari
async def sherpa_ritual(raw_packets: list[RawDataPacket]) -> list[PurifiedDataPacket]:
    """
    SHERPA RITUELI
    Nehirde arinma, yukun hafiflemesi
    """
    layer = SuLayer()

    print(f"Nehir akisi basliyor... {len(raw_packets)} paket bekliyor")

    purified = await layer.purify_batch(raw_packets, PurificationLevel.DEEP)

    stats = layer.get_flow_stats()
    print(f"  Arindirma tamamlandi:")
    print(f"    - {stats['total_tokens_removed']} token temizlendi")
    print(f"    - {stats['hallucinations_detected']} halusnasyon elendi")
    print(f"    - Ortalama gurultu orani: %{stats['average_noise_ratio']*100:.1f}")

    return purified
