"""
📊 API Data Models
==================
Mandala Dashboard için veri modelleri
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import math


class SectorType(Enum):
    """Mandala sektör türleri"""
    TOPRAK = "toprak"
    SU = "su"
    ATES = "ates"
    HAVA = "hava"
    ETER = "eter"


class RotationDirection(Enum):
    """Dönüş yönü"""
    CLOCKWISE = "clockwise"
    COUNTER_CLOCKWISE = "counter_clockwise"
    STILL = "still"


@dataclass
class SectorData:
    """Mandala sektör verisi"""

    sector_type: SectorType
    angle_start: float          # Derece (0-360)
    angle_end: float
    radius_inner: float         # 0-1 arası
    radius_outer: float
    color: str                  # Hex renk
    intensity: float = 1.0      # 0-1 parlaklık
    is_active: bool = False
    data_count: int = 0
    label: str = ""

    @property
    def angle_span(self) -> float:
        return self.angle_end - self.angle_start

    @property
    def center_angle(self) -> float:
        return (self.angle_start + self.angle_end) / 2

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.sector_type.value,
            "angle": {
                "start": self.angle_start,
                "end": self.angle_end,
                "center": self.center_angle,
                "span": self.angle_span
            },
            "radius": {
                "inner": self.radius_inner,
                "outer": self.radius_outer
            },
            "color": self.color,
            "intensity": self.intensity,
            "is_active": self.is_active,
            "data_count": self.data_count,
            "label": self.label
        }


@dataclass
class MandalaState:
    """Mandala genel durumu"""

    sectors: List[SectorData]
    rotation_angle: float = 0.0
    rotation_speed: float = 1.0
    rotation_direction: RotationDirection = RotationDirection.CLOCKWISE
    center_logo: str = "CAZIBE"
    center_frequency: int = 963
    is_spinning: bool = False
    pulse_rate: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def create_default(cls) -> "MandalaState":
        """Varsayılan 5 elementli Mandala oluştur"""
        colors = {
            SectorType.TOPRAK: "#8B4513",  # Kahverengi
            SectorType.SU: "#1E90FF",       # Mavi
            SectorType.ATES: "#FF4500",     # Turuncu-kırmızı
            SectorType.HAVA: "#E0E0E0",     # Açık gri
            SectorType.ETER: "#9400D3",     # Mor
        }

        labels = {
            SectorType.TOPRAK: "🪨 TOPRAK",
            SectorType.SU: "🌊 SU",
            SectorType.ATES: "🔥 ATEŞ",
            SectorType.HAVA: "🌬️ HAVA",
            SectorType.ETER: "🌌 ETER",
        }

        sectors = []
        angle_per_sector = 360 / 5

        for i, sector_type in enumerate(SectorType):
            sectors.append(SectorData(
                sector_type=sector_type,
                angle_start=i * angle_per_sector,
                angle_end=(i + 1) * angle_per_sector,
                radius_inner=0.3,
                radius_outer=0.9,
                color=colors[sector_type],
                label=labels[sector_type]
            ))

        return cls(sectors=sectors)

    def update_sector(self, sector_type: SectorType, **kwargs) -> None:
        """Sektör güncelle"""
        for sector in self.sectors:
            if sector.sector_type == sector_type:
                for key, value in kwargs.items():
                    if hasattr(sector, key):
                        setattr(sector, key, value)
                break

    def activate_sector(self, sector_type: SectorType) -> None:
        """Sektörü aktifleştir"""
        for sector in self.sectors:
            sector.is_active = sector.sector_type == sector_type

    def spin(self, degrees: float = 1.0) -> None:
        """Mandala'yı döndür"""
        if self.rotation_direction == RotationDirection.CLOCKWISE:
            self.rotation_angle = (self.rotation_angle + degrees) % 360
        elif self.rotation_direction == RotationDirection.COUNTER_CLOCKWISE:
            self.rotation_angle = (self.rotation_angle - degrees) % 360

    def to_dict(self) -> Dict[str, Any]:
        return {
            "sectors": [s.to_dict() for s in self.sectors],
            "rotation": {
                "angle": self.rotation_angle,
                "speed": self.rotation_speed,
                "direction": self.rotation_direction.value
            },
            "center": {
                "logo": self.center_logo,
                "frequency": self.center_frequency
            },
            "is_spinning": self.is_spinning,
            "pulse_rate": self.pulse_rate,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class LayerStatus:
    """Katman durum bilgisi"""

    name: str
    element: str
    state: str
    fold_count: int = 0
    last_activity: Optional[datetime] = None
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "element": self.element,
            "state": self.state,
            "fold_count": self.fold_count,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "metrics": self.metrics
        }


@dataclass
class ProcessRequest:
    """İşleme isteği"""

    data: Any
    sources: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    start_layer: str = "TOPRAK"
    end_layer: str = "ETER"
    async_mode: bool = False


@dataclass
class ProcessResponse:
    """İşleme yanıtı"""

    journey_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    layers_traversed: List[str] = field(default_factory=list)
    final_output: Optional[Dict] = None
    parchment: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "journey_id": self.journey_id,
            "status": self.status,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "layers_traversed": self.layers_traversed,
            "final_output": self.final_output,
            "parchment": self.parchment,
            "error": self.error
        }


@dataclass
class ProphecyParchment:
    """Kehanet Parşömeni - Müşteriye sunulan format"""

    title: str
    summary: str
    insights: List[str]
    recommendations: List[str]
    crystal_id: str
    frequency: int
    enlightenment_level: str
    created_at: datetime = field(default_factory=datetime.now)

    def render(self) -> str:
        """Parşömeni render et"""
        border = "═" * 60
        insights_text = "\n".join(f"  ✦ {i}" for i in self.insights)
        recommendations_text = "\n".join(f"  → {r}" for r in self.recommendations)

        return f"""
╔{border}╗
║
║  🛕 CAZIBE.IO - KEHANET PARŞÖMENİ
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
║
║  📅 {self.created_at.strftime('%Y-%m-%d %H:%M')}
║  🔮 Kristal: {self.crystal_id}
║  📡 Frekans: {self.frequency}Hz
║  🧘 Aydınlanma: {self.enlightenment_level.upper()}
║
║  ┌─────────────────────────────────┐
║  │  {self.title}
║  └─────────────────────────────────┘
║
║  {self.summary}
║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
║  ✨ İÇGÖRÜLER
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{insights_text}
║
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
║  🎯 ÖNERİLER
║  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{recommendations_text}
║
║  "Sizin veriniz var, bizim ise Görümüz var."
║                                  - CAZIBE.IO
║
╚{border}╝
"""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "summary": self.summary,
            "insights": self.insights,
            "recommendations": self.recommendations,
            "crystal_id": self.crystal_id,
            "frequency": self.frequency,
            "enlightenment_level": self.enlightenment_level,
            "created_at": self.created_at.isoformat(),
            "rendered": self.render()
        }
