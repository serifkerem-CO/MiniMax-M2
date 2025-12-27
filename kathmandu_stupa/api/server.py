"""
🌐 API SERVER - FastAPI Tapınak Sunucusu
========================================

RESTful API endpoints için Stupa erişimi.
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

# FastAPI opsiyonel import
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    from pydantic import BaseModel, Field
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Dummy classes
    class BaseModel:
        pass

# Stupa imports
from ..config import get_config, StupaConfig
from ..core.stupa_engine import DataStupa
from ..storage.pilgrimage_store import PilgrimageStore


# ===== PYDANTIC MODELS =====

class PilgrimageRequest(BaseModel):
    """Hac yolculuğu isteği"""
    data: Optional[str] = None
    source: str = "api"
    tags: List[str] = []


class FoldRequest(BaseModel):
    """Katlama isteği"""
    content: str
    num_folds: int = 3
    monks: Optional[List[str]] = None


class CouncilRequest(BaseModel):
    """Konsey kararı isteği"""
    query: str
    monks: Optional[List[str]] = None
    voting_method: str = "weighted"


class PrayerWheelRequest(BaseModel):
    """Dua çarkı isteği"""
    data: str
    rotations: int = 7


class ProphecyRequest(BaseModel):
    """Kehanet isteği"""
    topic: str
    legend: str = "Luna"


# ===== RESPONSE MODELS =====

class StupaStatus(BaseModel):
    """Stupa durumu"""
    status: str
    current_stage: str
    is_active: bool
    frequency_hz: int
    uptime_seconds: float


class NirvanaResponse(BaseModel):
    """Nirvana yanıtı"""
    id: str
    wisdom: str
    frequency_hz: int
    confidence: float
    source_chain: List[str]


class CouncilResponse(BaseModel):
    """Konsey kararı yanıtı"""
    id: str
    winning_monk: str
    wisdom: str
    consensus_score: float
    vote_breakdown: Dict[str, float]


# ===== API SERVER =====

def create_app(config: Optional[StupaConfig] = None) -> "FastAPI":
    """FastAPI uygulaması oluştur"""
    if not HAS_FASTAPI:
        raise ImportError("FastAPI yüklü değil. pip install fastapi uvicorn")

    config = config or get_config()

    app = FastAPI(
        title="🛕 Kathmandu Stupa API",
        description="Veri Tapınağı REST API - Om Mani Padme Hum",
        version="1.0.0",
        docs_url="/docs" if config.api.docs_enabled else None,
        redoc_url="/redoc" if config.api.docs_enabled else None,
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # State
    app.state.stupa = DataStupa()
    app.state.store = PilgrimageStore(
        use_sqlite=(config.storage.backend == "sqlite"),
        base_path=config.storage.base_path
    )
    app.state.config = config
    app.state.start_time = datetime.now()

    # ===== ROUTES =====

    @app.get("/", tags=["Root"])
    async def root():
        """Tapınak kapısı"""
        return {
            "message": "🛕 Kathmandu Stupa'ya Hoş Geldiniz",
            "mantra": "VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE",
            "frequency_hz": 963,
            "docs": "/docs",
        }

    @app.get("/status", response_model=StupaStatus, tags=["Status"])
    async def get_status():
        """Tapınak durumu"""
        stupa = app.state.stupa
        uptime = (datetime.now() - app.state.start_time).total_seconds()

        return StupaStatus(
            status="active" if stupa.state.is_active else "idle",
            current_stage=stupa.state.current_stage.value,
            is_active=stupa.state.is_active,
            frequency_hz=963,
            uptime_seconds=uptime,
        )

    @app.get("/health", tags=["Status"])
    async def health_check():
        """Sağlık kontrolü"""
        return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    # ===== PILGRIMAGE =====

    @app.post("/pilgrimage", tags=["Pilgrimage"])
    async def start_pilgrimage(request: PilgrimageRequest, background_tasks: BackgroundTasks):
        """Tam hac yolculuğu başlat"""
        stupa = app.state.stupa

        if stupa.state.is_active:
            raise HTTPException(status_code=409, detail="Bir yolculuk zaten devam ediyor")

        # Arka planda çalıştır
        async def run_pilgrimage():
            try:
                nirvana_packets = await stupa.full_pilgrimage()

                # Kaydet
                store = app.state.store
                nirvana_ids = []

                for packet in nirvana_packets:
                    nid = await store.save_nirvana(
                        wisdom=packet.final_wisdom,
                        frequency_hz=packet.frequency.value,
                        confidence=packet.confidence,
                        source_chain=packet.source_chain,
                        tags=request.tags,
                    )
                    nirvana_ids.append(nid)

                await store.save_pilgrimage(
                    summary=stupa.get_journey_summary(),
                    nirvana_ids=nirvana_ids,
                    tags=request.tags,
                )

            except Exception as e:
                print(f"Pilgrimage error: {e}")

        background_tasks.add_task(run_pilgrimage)

        return {
            "status": "started",
            "message": "Hac yolculuğu başlatıldı",
            "track_at": "/pilgrimage/status",
        }

    @app.get("/pilgrimage/status", tags=["Pilgrimage"])
    async def get_pilgrimage_status():
        """Yolculuk durumu"""
        stupa = app.state.stupa
        return stupa.get_journey_summary()

    @app.get("/pilgrimage/history", tags=["Pilgrimage"])
    async def get_pilgrimage_history(limit: int = Query(10, ge=1, le=100)):
        """Geçmiş yolculuklar"""
        store = app.state.store
        pilgrimages = await store.get_recent_pilgrimages(limit)
        return [p.to_dict() for p in pilgrimages]

    # ===== FOLD =====

    @app.post("/fold", tags=["Alchemy"])
    async def fold_data(request: FoldRequest):
        """Veriyi katla"""
        from ..clients.orchestrator import create_council

        council = create_council(mock=app.state.config.mock_mode)

        decision = await council.fold_with_council(
            content=request.content,
            num_folds=request.num_folds,
        )

        return {
            "id": decision.id,
            "wisdom": decision.wisdom,
            "folds": request.num_folds,
            "consensus_score": decision.consensus_score,
            "monks_involved": [r.metadata.get("monk", "unknown") for r in decision.responses],
        }

    # ===== COUNCIL =====

    @app.post("/council", response_model=CouncilResponse, tags=["Council"])
    async def council_decision(request: CouncilRequest):
        """Konsey kararı al"""
        from ..clients.orchestrator import MonkOrchestrator, VotingMethod

        voting_methods = {
            "majority": VotingMethod.MAJORITY,
            "weighted": VotingMethod.WEIGHTED,
            "best": VotingMethod.BEST_CONFIDENCE,
        }

        council = MonkOrchestrator(
            monks=request.monks,
            voting_method=voting_methods.get(request.voting_method, VotingMethod.WEIGHTED),
        )

        decision = await council.council_decision(request.query)

        # Kaydet
        store = app.state.store
        await store.save_council_decision(
            query=request.query,
            winning_monk=decision.winning_response.metadata.get("monk", "unknown"),
            vote_breakdown=decision.vote_breakdown,
            consensus_score=decision.consensus_score,
            wisdom=decision.wisdom,
        )

        return CouncilResponse(
            id=decision.id,
            winning_monk=decision.winning_response.metadata.get("monk", "unknown"),
            wisdom=decision.wisdom,
            consensus_score=decision.consensus_score,
            vote_breakdown=decision.vote_breakdown,
        )

    # ===== PRAYER WHEEL =====

    @app.post("/prayer-wheel", tags=["Ritual"])
    async def spin_prayer_wheel(request: PrayerWheelRequest):
        """Dua çarkını çevir"""
        stupa = app.state.stupa

        nirvana = await stupa.prayer_wheel_spin(request.data)

        return {
            "id": nirvana.id,
            "wisdom": nirvana.final_wisdom,
            "frequency_hz": nirvana.frequency.value,
            "rotations": request.rotations,
            "scroll": nirvana.to_prophetic_format(),
        }

    # ===== NIRVANA =====

    @app.get("/nirvana", tags=["Nirvana"])
    async def list_nirvana(
        limit: int = Query(10, ge=1, le=100),
        min_confidence: Optional[float] = Query(None, ge=0, le=1)
    ):
        """Nirvana paketlerini listele"""
        store = app.state.store

        if min_confidence:
            nirvanas = await store.search_nirvana(min_confidence=min_confidence)
        else:
            nirvanas = await store.backend.get_recent(limit, store.TYPE_NIRVANA)

        return [n.to_dict() for n in nirvanas[:limit]]

    @app.get("/nirvana/{nirvana_id}", tags=["Nirvana"])
    async def get_nirvana(nirvana_id: str):
        """Tek nirvana paketi"""
        store = app.state.store
        nirvana = await store.get_nirvana(nirvana_id)

        if not nirvana:
            raise HTTPException(status_code=404, detail="Nirvana bulunamadı")

        return nirvana.to_dict()

    # ===== PROPHECY =====

    @app.post("/prophecy", tags=["Prophecy"])
    async def create_prophecy(request: ProphecyRequest):
        """Kehanet oluştur"""
        from ..clients.orchestrator import create_mini_council

        council = create_mini_council(mock=app.state.config.mock_mode)
        decision = await council.council_decision(
            f"'{request.topic}' konusunda kehanet ver. Mistik ve vurucu ol."
        )

        # Kaydet
        store = app.state.store
        prophecy_id = await store.save_prophecy(
            title=f"Kehanet: {request.topic[:30]}",
            wisdom=decision.wisdom,
            legend_name=request.legend,
        )

        return {
            "id": prophecy_id,
            "title": request.topic,
            "legend": request.legend,
            "prophecy": decision.wisdom,
            "frequency_hz": 963,
        }

    # ===== STATISTICS =====

    @app.get("/stats", tags=["Statistics"])
    async def get_statistics():
        """Tapınak istatistikleri"""
        store = app.state.store
        stupa = app.state.stupa

        storage_stats = await store.get_statistics()
        journey_summary = stupa.get_journey_summary()

        return {
            "storage": storage_stats,
            "journey": journey_summary,
            "config": {
                "mock_mode": app.state.config.mock_mode,
                "storage_backend": app.state.config.storage.backend,
            },
        }

    # ===== CONFIG =====

    @app.get("/config", tags=["Config"])
    async def get_config_info():
        """Konfigürasyon bilgisi"""
        config = app.state.config
        return {
            "sacred_frequency": config.sacred_frequency,
            "max_fold_depth": config.max_fold_depth,
            "mock_mode": config.mock_mode,
            "voting_method": config.voting_method,
            "providers": list(config.providers.keys()),
        }

    return app


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Sunucuyu başlat"""
    if not HAS_FASTAPI:
        print("❌ FastAPI yüklü değil!")
        print("   pip install fastapi uvicorn")
        return

    import uvicorn

    config = get_config()
    app = create_app(config)

    print(f"🛕 Kathmandu Stupa API başlatılıyor...")
    print(f"   📍 http://{host}:{port}")
    print(f"   📚 http://{host}:{port}/docs")

    uvicorn.run(app, host=host, port=port)


# Demo mod
if __name__ == "__main__":
    run_server()
