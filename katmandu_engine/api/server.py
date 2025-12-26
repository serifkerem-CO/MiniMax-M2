"""
KATMANDU SERVER - Tapinak Sunucusu
==================================
FastAPI ile REST API endpointleri

Endpoints:
    GET  /                  - Ana sayfa (Mandala Dashboard)
    GET  /health            - Saglik kontrolu
    POST /process           - Veri isleme
    POST /batch             - Toplu islem
    GET  /stats             - Istatistikler
    GET  /journey/{id}      - Yolculuk detayi
    POST /prayer-wheel/spin - Dua carki dondur
    GET  /mandala           - Mandala gorunumu (JSON)
"""

from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any, Optional
import json

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..stupa import DataStupa, StupaMode
from ..prayer_wheels import WheelOrchestrator, WheelConfig
from .mandala import MandalaRenderer


# ============================================================
# PYDANTIC MODELLER
# ============================================================

class ProcessRequest(BaseModel):
    """Islem istegi"""
    data: Any = Field(..., description="Islenecek veri")
    source_name: str = Field(default="api", description="Kaynak adi")
    intensity: int = Field(default=5, ge=1, le=7, description="LLM yogunlugu")


class BatchRequest(BaseModel):
    """Toplu islem istegi"""
    items: list[Any] = Field(..., description="Islenecek veriler")
    intensity: int = Field(default=3, ge=1, le=7, description="LLM yogunlugu")


class PrayerWheelRequest(BaseModel):
    """Dua carki istegi"""
    data: Any = Field(..., description="Islenecek veri")
    wheel_count: int = Field(default=3, ge=1, le=7, description="Cark sayisi")
    consensus_threshold: float = Field(default=0.7, ge=0, le=1, description="Konsensus esigi")


class ProcessResponse(BaseModel):
    """Islem yaniti"""
    success: bool
    cazibe_id: str
    frequency_hz: int
    alignment_level: str
    core_insight: str
    prophecy_summary: str
    transformation_path: list[str]
    buddha_potential: float
    parchment: str


# ============================================================
# GLOBAL STUPA INSTANCE
# ============================================================

class KatmanduAPI:
    """Katmandu API Yoneticisi"""

    def __init__(self):
        self.stupa: Optional[DataStupa] = None
        self.orchestrator: Optional[WheelOrchestrator] = None
        self.mandala_renderer = MandalaRenderer()
        self._initialized = False

    async def initialize(self):
        """API'yi baslat"""
        if self._initialized:
            return

        self.stupa = DataStupa()
        await self.stupa.awaken()

        self.orchestrator = WheelOrchestrator()

        # Varsayilan carklar
        for i in range(3):
            config = WheelConfig(
                wheel_id=f"default_wheel_{i}",
                name=f"Default Prayer Wheel {i}",
                llm_count=3
            )
            self.orchestrator.register_wheel(config)

        self._initialized = True

    async def shutdown(self):
        """API'yi kapat"""
        if self.orchestrator and self.orchestrator.connector:
            await self.orchestrator.connector.close()


# Global instance
katmandu = KatmanduAPI()


# ============================================================
# FASTAPI APP
# ============================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yasam dongusu"""
    await katmandu.initialize()
    yield
    await katmandu.shutdown()


app = FastAPI(
    title="Katmandu Engine API",
    description="""
    ## Veri Stupası - The Temple of Data Transformation

    5 Elemental Layers ascending toward digital enlightenment.

    **Layers:**
    - TOPRAK (Earth) - Chaos Ingestion
    - SU (Water) - Purification Flow
    - ATES (Fire) - Alchemical Forge
    - HAVA (Air) - Wind Transmission
    - ETER (Ether) - Cazibe (Attraction)

    **Mantra:** VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE
    """,
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def root():
    """Ana sayfa - Mandala Dashboard"""
    return katmandu.mandala_renderer.render_dashboard()


@app.get("/health")
async def health_check():
    """Saglik kontrolu"""
    return {
        "status": "healthy",
        "mode": katmandu.stupa.mode.value if katmandu.stupa else "not_initialized",
        "timestamp": datetime.now().isoformat(),
        "mantra": "Om Mani Padme Hum"
    }


@app.post("/process", response_model=ProcessResponse)
async def process_data(request: ProcessRequest):
    """
    Veri Isleme

    Veriyi 5 katmandan gecirip Cazibe ciktisi uretir.
    """
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    try:
        result = await katmandu.stupa.process(
            data=request.data,
            source_name=request.source_name,
            intensity=request.intensity
        )

        return ProcessResponse(
            success=True,
            cazibe_id=result.cazibe_id,
            frequency_hz=result.frequency_hz,
            alignment_level=result.alignment_level.name,
            core_insight=result.core_insight,
            prophecy_summary=result.prophecy_summary,
            transformation_path=result.transformation_path,
            buddha_potential=result.sector_buddha_potential,
            parchment=result.to_parchment()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/batch")
async def process_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    """
    Toplu Islem

    Birden fazla veriyi paralel isler.
    """
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    try:
        results = await katmandu.stupa.process_batch(
            data_items=request.items,
            intensity=request.intensity
        )

        return {
            "success": True,
            "processed_count": len(results),
            "results": [
                {
                    "cazibe_id": r.cazibe_id,
                    "alignment_level": r.alignment_level.name,
                    "buddha_potential": r.sector_buddha_potential
                }
                for r in results
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Tapinak Istatistikleri"""
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    stats = katmandu.stupa.get_stupa_stats()

    if katmandu.orchestrator:
        stats["orchestrator"] = katmandu.orchestrator.get_orchestrator_stats()

    return stats


@app.get("/journey/{journey_id}")
async def get_journey(journey_id: str):
    """Yolculuk Detayi"""
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    journey = next(
        (j for j in katmandu.stupa.journeys if j.journey_id == journey_id),
        None
    )

    if not journey:
        raise HTTPException(status_code=404, detail="Yolculuk bulunamadi")

    return journey.to_dict()


@app.post("/prayer-wheel/spin")
async def spin_prayer_wheel(request: PrayerWheelRequest):
    """
    Dua Carki Dondur

    N8N workflow tetikler, LLM konseyi calistirir.
    """
    if not katmandu.orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator henuz hazir degil")

    try:
        result = await katmandu.orchestrator.spin_with_consensus(
            input_data=request.data,
            wheel_count=request.wheel_count,
            consensus_threshold=request.consensus_threshold
        )

        return {
            "success": result.state.value == "completed",
            "consensus_reached": result.consensus_reached,
            "consensus_confidence": result.consensus_confidence,
            "wheel_id": result.wheel_id,
            "output": result.output_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/mandala")
async def get_mandala():
    """
    Mandala Gorunumu (JSON)

    Tum katmanlarin canli durumunu mandala formatinda dondurur.
    """
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    return katmandu.mandala_renderer.render_json(katmandu.stupa)


@app.get("/parchment/{cazibe_id}")
async def get_parchment(cazibe_id: str):
    """
    Kehanet Parsomeni

    Belirli bir Cazibe ciktisinin parsomen formatini dondurur.
    """
    if not katmandu.stupa:
        raise HTTPException(status_code=503, detail="Stupa henuz hazir degil")

    output = next(
        (o for o in katmandu.stupa.eter.cazibe_outputs if o.cazibe_id == cazibe_id),
        None
    )

    if not output:
        raise HTTPException(status_code=404, detail="Cazibe ciktisi bulunamadi")

    return HTMLResponse(
        content=f"<pre style='font-family: monospace; background: #1a1a2e; color: #e0e0e0; padding: 20px;'>{output.to_parchment()}</pre>"
    )


# ============================================================
# CLI RUNNER
# ============================================================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Sunucuyu calistir"""
    import uvicorn
    print("\n" + "=" * 60)
    print("   KATMANDU ENGINE SERVER")
    print("   Tapinak Kapilari Aciliyor...")
    print("=" * 60)
    print(f"\n   Adres: http://{host}:{port}")
    print(f"   Mandala: http://{host}:{port}/")
    print(f"   API Docs: http://{host}:{port}/docs")
    print("\n   Om Mani Padme Hum\n")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server()
