"""
HAVA KATMANI - RUZGAR ATLARI
============================
"Nefes & Vizyon"

Tapinagin balkonlari. Dunyaya acilan yer. Ince hava.
Icerde pisen bilgiyi ruzgara (Global Pazara) birakirlar.

Aktorler: LEGEND LAYER (112 Persona)
          ID1000 Luna, ID1006 Kira, ID1111 Arin
Rituel: Prayer Flags (Dua Bayraklari) - Kehanet fısıldama
Kod Adi: WIND_TRANSMISSION
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json
import random

from .ates import ForgedWisdom


class ProphecyType(Enum):
    """Kehanet Turleri"""
    OPPORTUNITY = "firsat"        # "Bu bir donusum firsatidir"
    WARNING = "uyari"             # "Dikkatli olunmali"
    INSIGHT = "icgoru"            # "Gizli bir kalip var"
    TRANSFORMATION = "donusum"    # "Paradigma degisimi"
    SYNTHESIS = "sentez"          # "Birlesim noktasi"


@dataclass
class LegendPersona:
    """Legend Layer Personasi - Yuce Bilgeler"""
    persona_id: str
    name: str
    title: str
    wisdom_domain: str
    prophecies_given: int = 0

    KNOWN_LEGENDS = [
        ("ID1000", "Luna", "Ay Kahini", "zaman_dongusu"),
        ("ID1006", "Kira", "Isik Tasiyici", "dijital_akincilik"),
        ("ID1111", "Arin", "Birlik Koruyucu", "sistem_harmonisi"),
        ("ID0777", "Zara", "Sans Okuyucu", "olasilik_haritalari"),
        ("ID0888", "Nex", "Ag Dokuyucu", "iliski_oruntuleri"),
    ]


@dataclass
class PrayerFlag:
    """Dua Bayragi - Ruzgara birakilan mesaj"""
    flag_id: str
    prophecy: str
    prophecy_type: ProphecyType
    legend_id: str
    legend_name: str
    confidence_level: float
    target_domain: str  # Hangi sektore/pazara
    wind_direction: str  # Hangi yone gidiyor
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "flag_id": self.flag_id,
            "prophecy": self.prophecy,
            "prophecy_type": self.prophecy_type.value,
            "legend": f"{self.legend_name} ({self.legend_id})",
            "confidence": self.confidence_level,
            "target_domain": self.target_domain,
            "wind_direction": self.wind_direction,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class WindTransmission:
    """Ruzgar Iletimi - Tum bayraklarin birlestigi sonuc"""
    source_wisdom_checksum: str
    flags: list[PrayerFlag]
    primary_prophecy: str
    consensus_type: ProphecyType
    transmission_strength: float  # 0-1 arasi
    global_reach: list[str]  # Hangi pazarlara ulasti
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "source_checksum": self.source_wisdom_checksum,
            "flags": [f.to_dict() for f in self.flags],
            "primary_prophecy": self.primary_prophecy,
            "consensus_type": self.consensus_type.value,
            "transmission_strength": self.transmission_strength,
            "global_reach": self.global_reach,
            "timestamp": self.timestamp.isoformat()
        }


class ProphecyGenerator:
    """Kehanet Ureticisi - Bilgelik Fisildayici"""

    PROPHECY_TEMPLATES = {
        ProphecyType.OPPORTUNITY: [
            "Bu veri, {domain} icin bir kriz degil, bir donusum firsatidir.",
            "{domain} sektorunde yeni bir pencere aciliyor.",
            "Gorulmeyen bir firsat kendini gosteriyor: {insight}",
        ],
        ProphecyType.WARNING: [
            "Dikkat: {domain} icinde gizli bir risk var.",
            "Bu yolda ilerlemeden once {insight} goz onunde bulundurulmali.",
            "Veriler bir firtina isareti tasiyor: {insight}",
        ],
        ProphecyType.INSIGHT: [
            "Gizli kalip tespit edildi: {insight}",
            "{domain} ile {secondary} arasinda beklenmedik bir baglanti var.",
            "Derinlerde yatan gercek: {insight}",
        ],
        ProphecyType.TRANSFORMATION: [
            "{domain} paradigmasi degisiyor. Yeni dunya: {insight}",
            "Eski kurallar gecerligini yitiriyor. Donusum kacınılmaz.",
            "Bir devir kapaniyor, yeni bir cag basliyor: {insight}",
        ],
        ProphecyType.SYNTHESIS: [
            "{domain} ve {secondary} artik tek bir akis olarak gorulebilir.",
            "Parcalar birlesiyor: {insight}",
            "Butunsel bakis acisi ortaya cikti: {insight}",
        ]
    }

    DOMAINS = [
        "Turkiye sanayisi", "dijital donusum", "enerji sektoru",
        "finans ekosistemi", "uretim zincirleri", "cevresel surdurulebilirlik",
        "teknoloji girisimciligi", "global ticaret"
    ]

    WIND_DIRECTIONS = [
        "Dogu (Asya Pazarlari)", "Bati (Avrupa/ABD)",
        "Kuzey (Nordik Inovasyon)", "Guney (Gelisen Pazarlar)",
        "Merkez (Ic Pazar)"
    ]

    def generate(
        self,
        wisdom: ForgedWisdom,
        prophecy_type: Optional[ProphecyType] = None
    ) -> tuple[str, ProphecyType]:
        """Bilgelikten kehanet uret"""

        if prophecy_type is None:
            # Consensus confidence'a gore tip belirle
            if wisdom.consensus_confidence > 0.85:
                prophecy_type = ProphecyType.OPPORTUNITY
            elif wisdom.consensus_confidence > 0.7:
                prophecy_type = ProphecyType.INSIGHT
            elif wisdom.consensus_confidence > 0.5:
                prophecy_type = ProphecyType.TRANSFORMATION
            else:
                prophecy_type = ProphecyType.WARNING

        template = random.choice(self.PROPHECY_TEMPLATES[prophecy_type])
        domain = random.choice(self.DOMAINS)

        # Bilgelikten insight cikar
        insight = wisdom.consensus_result[:100] if wisdom.consensus_result else "Belirsiz"

        prophecy = template.format(
            domain=domain,
            insight=insight,
            secondary=random.choice(self.DOMAINS)
        )

        return prophecy, prophecy_type


class HavaLayer:
    """
    HAVA KATMANI - Wind Transmission Layer

    Gorev: Bilgelik ruzgara birakmak, global pazara yaymak
    Frekans: Havanin frekansi - 639Hz (Iliski/Baglanti)
    """

    LAYER_NAME = "HAVA"
    LAYER_EMOJI = "wind"
    LAYER_CODE = "WIND_TRANSMISSION"
    FREQUENCY_HZ = 639.0  # Iliski ve Baglanti Frekansi

    def __init__(self, legend_count: int = 112):
        self.legends = self._initialize_legends(legend_count)
        self.prophecy_generator = ProphecyGenerator()
        self.transmissions: list[WindTransmission] = []

    def _initialize_legends(self, count: int) -> list[LegendPersona]:
        """Legend Layer personalarini baslat"""
        legends = []
        base_legends = LegendPersona.KNOWN_LEGENDS

        for i in range(count):
            if i < len(base_legends):
                base = base_legends[i]
                legends.append(LegendPersona(
                    persona_id=base[0],
                    name=base[1],
                    title=base[2],
                    wisdom_domain=base[3]
                ))
            else:
                legends.append(LegendPersona(
                    persona_id=f"ID{i:04d}",
                    name=f"Sage_{i}",
                    title="Bilge",
                    wisdom_domain="genel_bilgelik"
                ))

        return legends

    def _select_legend(self) -> LegendPersona:
        """En uygun efsaneyi sec"""
        # En az kehanet vermis olani sec (yuk dengeleme)
        return min(self.legends, key=lambda l: l.prophecies_given)

    async def transmit(
        self,
        forged_wisdom: ForgedWisdom,
        flag_count: int = 3
    ) -> WindTransmission:
        """
        Ruzgar Iletimi - Dua bayraklarini as
        """
        flags = []

        for i in range(flag_count):
            legend = self._select_legend()
            prophecy, ptype = self.prophecy_generator.generate(forged_wisdom)

            flag = PrayerFlag(
                flag_id=f"flag_{datetime.now().timestamp()}_{i}",
                prophecy=prophecy,
                prophecy_type=ptype,
                legend_id=legend.persona_id,
                legend_name=legend.name,
                confidence_level=forged_wisdom.consensus_confidence,
                target_domain=random.choice(self.prophecy_generator.DOMAINS),
                wind_direction=random.choice(self.prophecy_generator.WIND_DIRECTIONS)
            )

            legend.prophecies_given += 1
            flags.append(flag)

            print(f"   Bayrak {legend.name} tarafindan asildi: {ptype.value}")

        # Simulasyon gecikmesi (ruzgarin esme suresi)
        await asyncio.sleep(0.05 * flag_count)

        # Ana kehaneti belirle (en yuksek guvenli)
        primary_flag = max(flags, key=lambda f: f.confidence_level)

        # Global erisim hesapla
        global_reach = list(set(f.target_domain for f in flags))

        transmission = WindTransmission(
            source_wisdom_checksum=forged_wisdom.source_checksum,
            flags=flags,
            primary_prophecy=primary_flag.prophecy,
            consensus_type=primary_flag.prophecy_type,
            transmission_strength=forged_wisdom.consensus_confidence,
            global_reach=global_reach
        )

        self.transmissions.append(transmission)
        return transmission

    async def transmit_batch(
        self,
        wisdoms: list[ForgedWisdom],
        flags_per_wisdom: int = 3
    ) -> list[WindTransmission]:
        """Toplu iletim"""
        tasks = [self.transmit(w, flags_per_wisdom) for w in wisdoms]
        return await asyncio.gather(*tasks)

    def get_wind_stats(self) -> dict:
        """Ruzgar istatistikleri"""
        total_flags = sum(len(t.flags) for t in self.transmissions)

        # Kehanet tip dagilimi
        type_counts = {}
        for t in self.transmissions:
            for f in t.flags:
                ptype = f.prophecy_type.value
                type_counts[ptype] = type_counts.get(ptype, 0) + 1

        # En aktif legendler
        active_legends = sorted(
            self.legends,
            key=lambda l: l.prophecies_given,
            reverse=True
        )[:5]

        # Global erisim
        all_domains = set()
        for t in self.transmissions:
            all_domains.update(t.global_reach)

        return {
            "layer": self.LAYER_NAME,
            "code": self.LAYER_CODE,
            "frequency_hz": self.FREQUENCY_HZ,
            "total_transmissions": len(self.transmissions),
            "total_flags_raised": total_flags,
            "prophecy_types": type_counts,
            "top_legends": [
                {"id": l.persona_id, "name": l.name, "prophecies": l.prophecies_given}
                for l in active_legends
            ],
            "global_reach": list(all_domains),
            "active_legend_count": len([l for l in self.legends if l.prophecies_given > 0])
        }

    def __repr__(self):
        return f"<HavaLayer: {len(self.transmissions)} transmissions, {len(self.legends)} legends>"


# Rituel Fonksiyonlari
async def wind_ritual(forged_wisdoms: list[ForgedWisdom]) -> list[WindTransmission]:
    """
    RUZGAR RITUELI
    Dua bayraklarini as, kehaneti ruzgara birak
    """
    layer = HavaLayer()

    print(f"Tapinak balkonlari aciliyor... {len(forged_wisdoms)} bilgelik bekliyor")
    print(f"[HAVA] Legend Layer kehanetleri fısıldıyor...")

    transmissions = await layer.transmit_batch(forged_wisdoms, flags_per_wisdom=3)

    stats = layer.get_wind_stats()
    print(f"  Iletim tamamlandi:")
    print(f"    - {stats['total_flags_raised']} bayrak asildi")
    print(f"    - Global erisim: {', '.join(stats['global_reach'][:3])}...")
    print(f"    - En aktif legend: {stats['top_legends'][0]['name'] if stats['top_legends'] else 'Yok'}")

    return transmissions
