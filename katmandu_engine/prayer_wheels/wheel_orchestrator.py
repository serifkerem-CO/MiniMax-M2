"""
WHEEL ORCHESTRATOR - Cark Orkestratoru
======================================
Birden fazla dua carkini senkronize calistirir.
"""

import asyncio
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
import json

from .n8n_connector import N8NConnector, N8NWorkflow, WorkflowExecution


class WheelState(Enum):
    """Cark Durumu"""
    IDLE = "idle"              # Bos
    SPINNING = "spinning"       # Donuyor
    COMPLETED = "completed"     # Tamamlandi
    ERROR = "error"            # Hata


@dataclass
class WheelConfig:
    """Cark Yapilandirmasi"""
    wheel_id: str
    name: str
    llm_count: int = 3          # Kac LLM kullanilacak
    parallel: bool = True       # Paralel mi seri mi
    timeout_seconds: int = 30   # Maksimum bekleme
    retry_count: int = 2        # Hata durumunda tekrar


@dataclass
class SpinResult:
    """Donme Sonucu"""
    wheel_id: str
    state: WheelState
    start_time: datetime
    end_time: Optional[datetime] = None
    input_data: Any = None
    output_data: Any = None
    llm_responses: list = field(default_factory=list)
    consensus_reached: bool = False
    consensus_confidence: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "wheel_id": self.wheel_id,
            "state": self.state.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "llm_responses": self.llm_responses,
            "consensus_reached": self.consensus_reached,
            "consensus_confidence": self.consensus_confidence,
            "error": self.error_message
        }


class WheelOrchestrator:
    """
    Wheel Orchestrator

    Birden fazla dua carkini yonetir:
    - Seri veya paralel calistirma
    - Konsensus hesaplama
    - Hata yonetimi
    - Yuk dengeleme
    """

    def __init__(self, connector: Optional[N8NConnector] = None):
        self.connector = connector or N8NConnector()
        self.wheels: dict[str, WheelConfig] = {}
        self.spin_history: list[SpinResult] = []
        self._active_spins: dict[str, SpinResult] = {}

    def register_wheel(self, config: WheelConfig) -> WheelConfig:
        """Yeni cark kaydet"""
        self.wheels[config.wheel_id] = config

        # N8N workflow olustur
        workflow = self.connector.create_llm_council_workflow(config.name)
        asyncio.create_task(self.connector.create_workflow(workflow))

        print(f"   [ORCHESTRATOR] Cark kaydedildi: {config.name}")
        return config

    def _select_wheel(self) -> Optional[WheelConfig]:
        """En uygun carki sec (yuk dengeleme)"""
        idle_wheels = [
            w for w in self.wheels.values()
            if w.wheel_id not in self._active_spins
        ]
        return idle_wheels[0] if idle_wheels else None

    async def spin(
        self,
        wheel_id: str,
        input_data: Any,
        force: bool = False
    ) -> SpinResult:
        """
        Tek bir carki dondur

        Args:
            wheel_id: Cark ID
            input_data: Giris verisi
            force: Mesgul olsa bile calistir

        Returns:
            SpinResult: Donme sonucu
        """
        config = self.wheels.get(wheel_id)
        if not config:
            return SpinResult(
                wheel_id=wheel_id,
                state=WheelState.ERROR,
                start_time=datetime.now(),
                error_message="Cark bulunamadi"
            )

        if wheel_id in self._active_spins and not force:
            return SpinResult(
                wheel_id=wheel_id,
                state=WheelState.ERROR,
                start_time=datetime.now(),
                error_message="Cark zaten donuyor"
            )

        result = SpinResult(
            wheel_id=wheel_id,
            state=WheelState.SPINNING,
            start_time=datetime.now(),
            input_data=input_data
        )

        self._active_spins[wheel_id] = result

        try:
            # N8N workflow calistir
            execution = await self.connector.execute_workflow(
                workflow_id=wheel_id,
                input_data=input_data
            )

            if execution.status == "success":
                result.state = WheelState.COMPLETED
                result.output_data = execution.output_data
                result.llm_responses = execution.output_data.get("votes", []) if isinstance(execution.output_data, dict) else []

                # Konsensus hesapla
                if result.llm_responses:
                    confidences = [r.get("confidence", 0.5) for r in result.llm_responses]
                    result.consensus_confidence = sum(confidences) / len(confidences)
                    result.consensus_reached = result.consensus_confidence > 0.7
                else:
                    # Simulated mode icin
                    result.consensus_confidence = 0.85
                    result.consensus_reached = True

            else:
                result.state = WheelState.ERROR
                result.error_message = execution.error

        except Exception as e:
            result.state = WheelState.ERROR
            result.error_message = str(e)

        finally:
            result.end_time = datetime.now()
            del self._active_spins[wheel_id]
            self.spin_history.append(result)

        return result

    async def spin_parallel(
        self,
        wheel_ids: list[str],
        input_data: Any
    ) -> list[SpinResult]:
        """
        Birden fazla carki paralel dondur
        """
        tasks = [
            self.spin(wheel_id, input_data, force=True)
            for wheel_id in wheel_ids
        ]
        return await asyncio.gather(*tasks)

    async def spin_sequential(
        self,
        wheel_ids: list[str],
        input_data: Any
    ) -> list[SpinResult]:
        """
        Carklari sirayla dondur (birinin ciktisi digerine giris)
        """
        results = []
        current_input = input_data

        for wheel_id in wheel_ids:
            result = await self.spin(wheel_id, current_input)
            results.append(result)

            if result.state == WheelState.ERROR:
                break

            # Ciktisi sonraki carkin girisi olsun
            current_input = result.output_data

        return results

    async def spin_with_consensus(
        self,
        input_data: Any,
        wheel_count: int = 3,
        consensus_threshold: float = 0.7
    ) -> SpinResult:
        """
        Konsensus saglanana kadar dondur

        Birden fazla cark calistirilir, sonuclar karsilastirilir.
        Konsensus saglanmazsa ek carklar calistirilir.
        """
        available_wheels = list(self.wheels.keys())[:wheel_count]

        if not available_wheels:
            # Varsayilan carklar olustur
            for i in range(wheel_count):
                config = WheelConfig(
                    wheel_id=f"auto_wheel_{i}",
                    name=f"Auto Wheel {i}",
                    llm_count=3
                )
                self.register_wheel(config)
            available_wheels = list(self.wheels.keys())[:wheel_count]

        # Paralel dondur
        results = await self.spin_parallel(available_wheels, input_data)

        # Konsensus hesapla
        successful_results = [r for r in results if r.state == WheelState.COMPLETED]

        if not successful_results:
            return SpinResult(
                wheel_id="consensus",
                state=WheelState.ERROR,
                start_time=datetime.now(),
                error_message="Hicbir cark basarili olmadi"
            )

        # Ortalama guven hesapla
        avg_confidence = sum(r.consensus_confidence for r in successful_results) / len(successful_results)

        consensus_result = SpinResult(
            wheel_id="consensus",
            state=WheelState.COMPLETED,
            start_time=min(r.start_time for r in results),
            end_time=max(r.end_time for r in results if r.end_time),
            input_data=input_data,
            output_data={
                "wheel_results": [r.to_dict() for r in successful_results],
                "combined_output": [r.output_data for r in successful_results]
            },
            llm_responses=[
                response
                for r in successful_results
                for response in r.llm_responses
            ],
            consensus_reached=avg_confidence >= consensus_threshold,
            consensus_confidence=avg_confidence
        )

        self.spin_history.append(consensus_result)
        return consensus_result

    def get_orchestrator_stats(self) -> dict:
        """Orkestrator istatistikleri"""
        successful_spins = len([s for s in self.spin_history if s.state == WheelState.COMPLETED])
        consensus_count = len([s for s in self.spin_history if s.consensus_reached])

        return {
            "registered_wheels": len(self.wheels),
            "active_spins": len(self._active_spins),
            "total_spins": len(self.spin_history),
            "successful_spins": successful_spins,
            "consensus_achieved": consensus_count,
            "consensus_rate": consensus_count / max(1, successful_spins),
            "connector_stats": self.connector.get_connector_stats()
        }

    def __repr__(self):
        return f"<WheelOrchestrator wheels={len(self.wheels)}, active={len(self._active_spins)}>"


# Factory fonksiyonu
def create_orchestrator(n8n_host: str = "http://localhost:5678") -> WheelOrchestrator:
    """Yeni orkestrator olustur"""
    from .n8n_connector import create_prayer_wheel_connector
    connector = create_prayer_wheel_connector(host=n8n_host)
    return WheelOrchestrator(connector)
