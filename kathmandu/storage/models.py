"""
📦 Storage Data Models
======================
Kalıcı veri modelleri
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import json
import hashlib


@dataclass
class StoredJourney:
    """Saklanan yolculuk kaydı"""

    journey_id: str
    input_data: str
    final_output: Optional[Dict[str, Any]]
    layers_traversed: List[str]
    duration_seconds: float
    state: str
    created_at: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "journey_id": self.journey_id,
            "input_data": self.input_data[:500],  # Özet
            "final_output": self.final_output,
            "layers_traversed": self.layers_traversed,
            "duration_seconds": self.duration_seconds,
            "state": self.state,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoredJourney":
        return cls(
            journey_id=data["journey_id"],
            input_data=data["input_data"],
            final_output=data.get("final_output"),
            layers_traversed=data.get("layers_traversed", []),
            duration_seconds=data.get("duration_seconds", 0),
            state=data.get("state", "unknown"),
            created_at=datetime.fromisoformat(data["created_at"]),
            metadata=data.get("metadata", {})
        )


@dataclass
class StoredCrystal:
    """Saklanan bilgelik kristali"""

    crystal_id: str
    essence: str
    frequency: int
    enlightenment_level: str
    purity_percentage: float
    source_journey_id: str
    created_at: datetime
    tags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "crystal_id": self.crystal_id,
            "essence": self.essence,
            "frequency": self.frequency,
            "enlightenment_level": self.enlightenment_level,
            "purity_percentage": self.purity_percentage,
            "source_journey_id": self.source_journey_id,
            "created_at": self.created_at.isoformat(),
            "tags": self.tags
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StoredCrystal":
        return cls(
            crystal_id=data["crystal_id"],
            essence=data["essence"],
            frequency=data.get("frequency", 963),
            enlightenment_level=data.get("enlightenment_level", "seeker"),
            purity_percentage=data.get("purity_percentage", 0),
            source_journey_id=data.get("source_journey_id", ""),
            created_at=datetime.fromisoformat(data["created_at"]),
            tags=data.get("tags", [])
        )


@dataclass
class StorageStats:
    """Depolama istatistikleri"""

    total_journeys: int
    total_crystals: int
    successful_journeys: int
    average_duration: float
    average_purity: float
    most_common_enlightenment: str
    storage_type: str
    last_activity: Optional[datetime]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "total_journeys": self.total_journeys,
            "total_crystals": self.total_crystals,
            "successful_journeys": self.successful_journeys,
            "average_duration": self.average_duration,
            "average_purity": self.average_purity,
            "most_common_enlightenment": self.most_common_enlightenment,
            "storage_type": self.storage_type,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None
        }
