"""
KATMANDU PERSONAS - Persona Yonetimi
====================================
667 Persona (111 + 111 + 333 + 112) yonetimi

Persona Gruplari:
    - GLITCH LAB (111): Thamel Tuccarlari - Veri toplama
    - CORE FLOW (111): Global Genclik Serpalari - Arinma
    - ADVANCED MIND (333): Rahipler - LLM Konseyi
    - LEGEND LAYER (112): Yuce Bilgeler - Kehanet
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, Any


class PersonaGroup(Enum):
    """Persona Gruplari"""
    GLITCH_LAB = "glitch_lab"       # 111 - Veri toplayicilar
    CORE_FLOW = "core_flow"         # 111 - Seraplar
    ADVANCED_MIND = "advanced_mind"  # 333 - Rahipler
    LEGEND_LAYER = "legend_layer"    # 112 - Legendler


class PersonaStatus(Enum):
    """Persona Durumu"""
    IDLE = "idle"
    ACTIVE = "active"
    BUSY = "busy"
    RESTING = "resting"


@dataclass
class PersonaProfile:
    """Genel Persona Profili"""
    persona_id: str
    name: str
    group: PersonaGroup
    specialty: str
    status: PersonaStatus = PersonaStatus.IDLE
    created_at: datetime = field(default_factory=datetime.now)
    tasks_completed: int = 0
    experience_points: int = 0

    def to_dict(self) -> dict:
        return {
            "id": self.persona_id,
            "name": self.name,
            "group": self.group.value,
            "specialty": self.specialty,
            "status": self.status.value,
            "tasks_completed": self.tasks_completed,
            "xp": self.experience_points
        }


class PersonaRegistry:
    """
    Persona Kayit Defteri

    Tum 667 personayi yonetir.
    """

    TOTAL_PERSONAS = 667

    def __init__(self):
        self.personas: dict[str, PersonaProfile] = {}
        self._initialize_all_personas()

    def _initialize_all_personas(self):
        """Tum personalari olustur"""
        # GLITCH LAB (111)
        for i in range(111):
            self._create_persona(
                f"GL{i:03d}",
                f"Glitch_{i}",
                PersonaGroup.GLITCH_LAB,
                ["PDF_Arkeologu", "Web_Avcisi", "API_Simyacisi"][i % 3]
            )

        # CORE FLOW (111)
        sherpa_names = ["Dilara", "Ali", "Kenan", "Yuki", "Maria", "Chen"]
        for i in range(111):
            self._create_persona(
                f"CF{i:03d}",
                f"{sherpa_names[i % len(sherpa_names)]}_{i}",
                PersonaGroup.CORE_FLOW,
                ["metin_analizi", "veri_yapislandirma", "anomali_tespiti"][i % 3]
            )

        # ADVANCED MIND (333)
        monk_types = ["Claude", "Mistral", "DeepSeek", "Gemini", "Llama", "GPT", "MiniMax"]
        for i in range(333):
            self._create_persona(
                f"AM{i:03d}",
                f"Monk_{monk_types[i % len(monk_types)]}_{i}",
                PersonaGroup.ADVANCED_MIND,
                ["ethics", "logic", "code", "analysis", "wisdom", "creativity", "synthesis"][i % 7]
            )

        # LEGEND LAYER (112)
        legends = [
            ("Luna", "Ay Kahini"), ("Kira", "Isik Tasiyici"),
            ("Arin", "Birlik Koruyucu"), ("Zara", "Sans Okuyucu"),
            ("Nex", "Ag Dokuyucu")
        ]
        for i in range(112):
            name, title = legends[i % len(legends)]
            self._create_persona(
                f"LL{i:03d}",
                f"{name}_{i}",
                PersonaGroup.LEGEND_LAYER,
                title
            )

    def _create_persona(
        self,
        persona_id: str,
        name: str,
        group: PersonaGroup,
        specialty: str
    ):
        """Yeni persona olustur"""
        self.personas[persona_id] = PersonaProfile(
            persona_id=persona_id,
            name=name,
            group=group,
            specialty=specialty
        )

    def get_by_group(self, group: PersonaGroup) -> list[PersonaProfile]:
        """Gruba gore personalari getir"""
        return [p for p in self.personas.values() if p.group == group]

    def get_available(self, group: Optional[PersonaGroup] = None) -> list[PersonaProfile]:
        """Musait personalari getir"""
        personas = self.personas.values()
        if group:
            personas = [p for p in personas if p.group == group]
        return [p for p in personas if p.status == PersonaStatus.IDLE]

    def assign_task(self, persona_id: str) -> bool:
        """Personaya gorev ata"""
        if persona_id in self.personas:
            self.personas[persona_id].status = PersonaStatus.ACTIVE
            return True
        return False

    def complete_task(self, persona_id: str, xp_earned: int = 10) -> bool:
        """Gorevi tamamla"""
        if persona_id in self.personas:
            persona = self.personas[persona_id]
            persona.status = PersonaStatus.IDLE
            persona.tasks_completed += 1
            persona.experience_points += xp_earned
            return True
        return False

    def get_stats(self) -> dict:
        """Kayit istatistikleri"""
        group_counts = {}
        for group in PersonaGroup:
            group_counts[group.value] = len(self.get_by_group(group))

        active_count = len([p for p in self.personas.values() if p.status == PersonaStatus.ACTIVE])

        total_tasks = sum(p.tasks_completed for p in self.personas.values())
        total_xp = sum(p.experience_points for p in self.personas.values())

        return {
            "total_personas": len(self.personas),
            "group_distribution": group_counts,
            "active_personas": active_count,
            "idle_personas": len(self.personas) - active_count,
            "total_tasks_completed": total_tasks,
            "total_experience_points": total_xp
        }


# Global registry
_registry: Optional[PersonaRegistry] = None


def get_registry() -> PersonaRegistry:
    """Global persona registry'yi getir"""
    global _registry
    if _registry is None:
        _registry = PersonaRegistry()
    return _registry


__all__ = [
    "PersonaGroup",
    "PersonaStatus",
    "PersonaProfile",
    "PersonaRegistry",
    "get_registry"
]
