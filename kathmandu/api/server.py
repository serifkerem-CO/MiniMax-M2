"""
🌐 MANDALA SERVER
==================
FastAPI tabanlı Mandala Dashboard sunucusu

Tapınak Modu - N8N çarkları döner!
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager
import json

# FastAPI imports (optional - graceful fallback)
try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import HTMLResponse
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    FastAPI = None

from ..stupa import DataStupa
from .models import (
    MandalaState,
    SectorType,
    LayerStatus,
    ProcessRequest,
    ProcessResponse,
    ProphecyParchment
)


class MandalaServer:
    """
    🛕 Mandala Sunucusu

    WebSocket üzerinden gerçek zamanlı Mandala güncellemeleri.
    REST API ile veri işleme.
    """

    def __init__(self, stupa: Optional[DataStupa] = None):
        self.stupa = stupa or DataStupa()
        self.mandala = MandalaState.create_default()
        self.active_connections: List[Any] = []  # WebSocket bağlantıları
        self._spin_task: Optional[asyncio.Task] = None
        self._is_temple_mode = False

    async def start_temple_mode(self) -> None:
        """Tapınak modunu başlat - Çarklar dönsün!"""
        self._is_temple_mode = True
        self.mandala.is_spinning = True

        async def spin_loop():
            while self._is_temple_mode:
                self.mandala.spin(degrees=1.0)
                await self._broadcast_mandala_update()
                await asyncio.sleep(0.05)  # 20 FPS

        self._spin_task = asyncio.create_task(spin_loop())

    async def stop_temple_mode(self) -> None:
        """Tapınak modunu durdur"""
        self._is_temple_mode = False
        self.mandala.is_spinning = False
        if self._spin_task:
            self._spin_task.cancel()
            try:
                await self._spin_task
            except asyncio.CancelledError:
                pass

    async def _broadcast_mandala_update(self) -> None:
        """Tüm bağlantılara Mandala güncellemesi gönder"""
        if not self.active_connections:
            return

        message = json.dumps({
            "type": "mandala_update",
            "data": self.mandala.to_dict()
        })

        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)

        for conn in disconnected:
            self.active_connections.remove(conn)

    async def process_data(self, request: ProcessRequest) -> ProcessResponse:
        """Veri işle ve yanıt döndür"""

        # Aktif katmanı güncelle
        for layer_name in self.stupa.layer_order:
            sector_type = SectorType[layer_name.replace("Ş", "S")]
            self.mandala.update_sector(sector_type, is_active=False)

        try:
            # İşleme başlat
            journey = await self.stupa.process(
                data=request.data,
                context=request.context,
                start_layer=request.start_layer,
                end_layer=request.end_layer
            )

            # Sonuç oluştur
            parchment = ""
            if journey.final_output and isinstance(journey.final_output, dict):
                parchment = journey.final_output.get("parchment", "")

            return ProcessResponse(
                journey_id=journey.journey_id,
                status=journey.state.value,
                started_at=journey.started_at,
                completed_at=journey.completed_at,
                layers_traversed=journey.layers_traversed,
                final_output=journey.final_output,
                parchment=parchment
            )

        except Exception as e:
            return ProcessResponse(
                journey_id="ERROR",
                status="failed",
                started_at=datetime.now(),
                error=str(e)
            )

    def get_layer_statuses(self) -> List[LayerStatus]:
        """Tüm katmanların durumunu getir"""
        statuses = []
        for name, layer in self.stupa.layers.items():
            karma = layer.get_karma()
            statuses.append(LayerStatus(
                name=name,
                element=karma.get("element", ""),
                state=karma.get("state", "unknown"),
                fold_count=karma.get("total_folds", 0),
                metrics=karma
            ))
        return statuses

    def get_mandala_state(self) -> Dict[str, Any]:
        """Mevcut Mandala durumunu getir"""
        return self.mandala.to_dict()


def create_app(stupa: Optional[DataStupa] = None) -> Any:
    """FastAPI uygulaması oluştur"""

    if not FASTAPI_AVAILABLE:
        raise ImportError(
            "FastAPI yüklü değil. Kurmak için: pip install fastapi uvicorn"
        )

    server = MandalaServer(stupa)

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Başlangıç
        print("🛕 Kathmandu Engine başlatılıyor...")
        print("📿 Mantra: VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE")
        yield
        # Kapanış
        await server.stop_temple_mode()
        print("🧘 Tapınak kapanıyor...")

    app = FastAPI(
        title="🛕 Kathmandu Engine - Mandala Dashboard",
        description="XDATUM & CAZIBE.IO Veri Dönüşüm Motoru",
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

    # ============ REST Endpoints ============

    @app.get("/")
    async def root():
        """Ana sayfa"""
        return {
            "message": "🛕 Kathmandu Engine - Tapınak Aktif",
            "mantra": "Om Mani Padme Hum",
            "frequency": 963,
            "endpoints": {
                "mandala": "/mandala",
                "process": "/process",
                "layers": "/layers",
                "temple_mode": "/temple/start",
                "ws": "/ws/mandala"
            }
        }

    @app.get("/mandala")
    async def get_mandala():
        """Mevcut Mandala durumu"""
        return server.get_mandala_state()

    @app.get("/layers")
    async def get_layers():
        """Katman durumları"""
        return {
            "layers": [s.to_dict() for s in server.get_layer_statuses()]
        }

    @app.get("/stats")
    async def get_stats():
        """Stupa istatistikleri"""
        return server.stupa.get_stupa_stats()

    @app.post("/process")
    async def process_data(data: str, sources: Optional[List[str]] = None):
        """Veri işle"""
        request = ProcessRequest(
            data=data,
            sources=sources or []
        )
        response = await server.process_data(request)
        return response.to_dict()

    @app.post("/temple/start")
    async def start_temple():
        """Tapınak modunu başlat"""
        await server.start_temple_mode()
        return {"status": "Temple mode started", "spinning": True}

    @app.post("/temple/stop")
    async def stop_temple():
        """Tapınak modunu durdur"""
        await server.stop_temple_mode()
        return {"status": "Temple mode stopped", "spinning": False}

    @app.get("/parchment/{journey_id}")
    async def get_parchment(journey_id: str):
        """Kehanet parşömeni getir"""
        journey = server.stupa.get_journey(journey_id)
        if not journey:
            raise HTTPException(status_code=404, detail="Journey not found")

        if journey.final_output:
            return {
                "journey_id": journey_id,
                "parchment": journey.final_output.get("parchment", ""),
                "crystal": journey.final_output.get("crystal", {})
            }
        return {"journey_id": journey_id, "parchment": "İşlem devam ediyor..."}

    # ============ WebSocket ============

    @app.websocket("/ws/mandala")
    async def websocket_mandala(websocket: WebSocket):
        """Gerçek zamanlı Mandala güncellemeleri"""
        await websocket.accept()
        server.active_connections.append(websocket)

        try:
            # İlk durum gönder
            await websocket.send_json({
                "type": "initial_state",
                "data": server.get_mandala_state()
            })

            # Mesaj dinle
            while True:
                data = await websocket.receive_text()
                message = json.loads(data)

                if message.get("type") == "spin":
                    server.mandala.spin(message.get("degrees", 5))
                elif message.get("type") == "activate_sector":
                    sector = SectorType[message.get("sector", "TOPRAK").upper()]
                    server.mandala.activate_sector(sector)

                await websocket.send_json({
                    "type": "mandala_update",
                    "data": server.get_mandala_state()
                })

        except WebSocketDisconnect:
            server.active_connections.remove(websocket)

    # ============ Demo HTML ============

    @app.get("/demo", response_class=HTMLResponse)
    async def demo_page():
        """Demo Mandala sayfası"""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>🛕 Kathmandu Mandala</title>
            <style>
                body {
                    background: #1a1a2e;
                    color: #eee;
                    font-family: 'Segoe UI', sans-serif;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    padding: 20px;
                }
                h1 { color: #9400D3; }
                #mandala {
                    width: 400px;
                    height: 400px;
                    border-radius: 50%;
                    border: 3px solid #9400D3;
                    position: relative;
                    animation: spin 10s linear infinite;
                }
                @keyframes spin {
                    from { transform: rotate(0deg); }
                    to { transform: rotate(360deg); }
                }
                .sector {
                    position: absolute;
                    width: 50%;
                    height: 50%;
                    clip-path: polygon(100% 0, 100% 100%, 0 100%);
                }
                .center {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 80px;
                    height: 80px;
                    background: #9400D3;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: bold;
                    animation: pulse 2s ease-in-out infinite;
                }
                @keyframes pulse {
                    0%, 100% { box-shadow: 0 0 20px #9400D3; }
                    50% { box-shadow: 0 0 40px #9400D3, 0 0 60px #9400D3; }
                }
                .stats {
                    margin-top: 20px;
                    padding: 20px;
                    background: #16213e;
                    border-radius: 10px;
                    max-width: 600px;
                }
                pre { color: #0ff; }
            </style>
        </head>
        <body>
            <h1>🛕 Kathmandu Engine</h1>
            <p>Om Mani Padme Hum - 963Hz</p>
            <div id="mandala">
                <div class="center">CAZİBE</div>
            </div>
            <div class="stats">
                <h3>📊 Canlı Durum</h3>
                <pre id="stats">Yükleniyor...</pre>
            </div>
            <script>
                async function fetchStats() {
                    const res = await fetch('/mandala');
                    const data = await res.json();
                    document.getElementById('stats').textContent =
                        JSON.stringify(data, null, 2);
                }
                fetchStats();
                setInterval(fetchStats, 2000);
            </script>
        </body>
        </html>
        """

    return app


# Sunucu başlatma yardımcısı
def run_server(host: str = "0.0.0.0", port: int = 8963):
    """Sunucuyu başlat"""
    try:
        import uvicorn
        app = create_app()
        print(f"🛕 Tapınak açılıyor: http://{host}:{port}")
        print(f"📿 Mandala Demo: http://{host}:{port}/demo")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        print("❌ Uvicorn yüklü değil. Kurmak için: pip install uvicorn")
