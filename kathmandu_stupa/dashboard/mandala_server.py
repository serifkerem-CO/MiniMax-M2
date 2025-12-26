"""
🎨 MANDALA SERVER - Tapınak Dashboard'u
=======================================

Dönen mandala arayüzü ile real-time veri görselleştirme.
"""

import asyncio
import json
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional
from pathlib import Path

try:
    from aiohttp import web
except ImportError:
    web = None  # aiohttp yoksa basit mod


@dataclass
class MandalaState:
    """Mandala durumu"""
    rotation_angle: float = 0.0
    active_layer: str = "dormant"
    frequency_hz: int = 963
    packets_flowing: int = 0
    last_update: str = ""


class MandalaServer:
    """
    🎨 Mandala Dashboard Server

    Real-time dönen mandala ile veri akışı görselleştirme.
    """

    def __init__(self, host: str = "0.0.0.0", port: int = 8888):
        self.host = host
        self.port = port
        self.state = MandalaState()
        self.connections: List = []

    def get_html(self) -> str:
        """Ana HTML sayfası"""
        return '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🛕 KATHMANDU STUPA - Mandala Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: radial-gradient(ellipse at center, #1a0a2e 0%, #0d0015 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', system-ui, sans-serif;
            color: #e0d4f7;
            overflow-x: hidden;
        }

        .header {
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, rgba(139,69,19,0.3) 0%, rgba(75,0,130,0.3) 100%);
            border-bottom: 2px solid #8b4513;
        }

        .header h1 {
            font-size: 2em;
            background: linear-gradient(90deg, #ffd700, #ff8c00, #ffd700);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header .mantra {
            font-size: 0.9em;
            color: #9370db;
            margin-top: 5px;
            font-style: italic;
        }

        .main-container {
            display: flex;
            justify-content: center;
            align-items: flex-start;
            padding: 20px;
            gap: 30px;
            flex-wrap: wrap;
        }

        /* MANDALA */
        .mandala-container {
            position: relative;
            width: 500px;
            height: 500px;
        }

        .mandala {
            position: absolute;
            width: 100%;
            height: 100%;
            animation: rotate 60s linear infinite;
        }

        @keyframes rotate {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .mandala-ring {
            position: absolute;
            border-radius: 50%;
            border: 3px solid;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        /* 5 Element Halkaları */
        .ring-eter {
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            border-color: rgba(255, 255, 255, 0.8);
            box-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
            animation: pulse-eter 4s ease-in-out infinite;
        }

        .ring-hava {
            width: 80%;
            height: 80%;
            top: 10%;
            left: 10%;
            border-color: rgba(135, 206, 250, 0.8);
            box-shadow: 0 0 25px rgba(135, 206, 250, 0.5);
            animation: pulse-hava 3.5s ease-in-out infinite;
        }

        .ring-ates {
            width: 60%;
            height: 60%;
            top: 20%;
            left: 20%;
            border-color: rgba(255, 69, 0, 0.8);
            box-shadow: 0 0 20px rgba(255, 69, 0, 0.5);
            animation: pulse-ates 3s ease-in-out infinite;
        }

        .ring-su {
            width: 40%;
            height: 40%;
            top: 30%;
            left: 30%;
            border-color: rgba(0, 191, 255, 0.8);
            box-shadow: 0 0 15px rgba(0, 191, 255, 0.5);
            animation: pulse-su 2.5s ease-in-out infinite;
        }

        .ring-toprak {
            width: 20%;
            height: 20%;
            top: 40%;
            left: 40%;
            border-color: rgba(139, 69, 19, 0.8);
            box-shadow: 0 0 10px rgba(139, 69, 19, 0.5);
            animation: pulse-toprak 2s ease-in-out infinite;
        }

        @keyframes pulse-eter { 0%, 100% { opacity: 0.6; } 50% { opacity: 1; } }
        @keyframes pulse-hava { 0%, 100% { opacity: 0.65; } 50% { opacity: 1; } }
        @keyframes pulse-ates { 0%, 100% { opacity: 0.7; } 50% { opacity: 1; } }
        @keyframes pulse-su { 0%, 100% { opacity: 0.75; } 50% { opacity: 1; } }
        @keyframes pulse-toprak { 0%, 100% { opacity: 0.8; } 50% { opacity: 1; } }

        /* Merkez Logo */
        .center-logo {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: radial-gradient(circle, #ffd700 0%, #ff8c00 100%);
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 2em;
            box-shadow: 0 0 40px rgba(255, 215, 0, 0.8);
            z-index: 10;
        }

        /* Katman İsimleri */
        .layer-labels {
            position: absolute;
            width: 100%;
            height: 100%;
        }

        .layer-label {
            position: absolute;
            font-size: 0.8em;
            padding: 5px 10px;
            border-radius: 15px;
            background: rgba(0,0,0,0.6);
        }

        .label-eter { top: -10px; left: 50%; transform: translateX(-50%); color: #fff; }
        .label-hava { top: 15%; right: 5%; color: #87ceeb; }
        .label-ates { bottom: 15%; right: 10%; color: #ff4500; }
        .label-su { bottom: 15%; left: 10%; color: #00bfff; }
        .label-toprak { top: 15%; left: 5%; color: #8b4513; }

        /* Sağ Panel - İstatistikler */
        .stats-panel {
            background: rgba(30, 20, 50, 0.9);
            border: 2px solid #8b4513;
            border-radius: 15px;
            padding: 20px;
            min-width: 300px;
        }

        .stats-title {
            font-size: 1.3em;
            color: #ffd700;
            border-bottom: 1px solid #8b4513;
            padding-bottom: 10px;
            margin-bottom: 15px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid rgba(139,69,19,0.3);
        }

        .stat-label {
            color: #9370db;
        }

        .stat-value {
            color: #ffd700;
            font-weight: bold;
        }

        .stat-value.active {
            color: #00ff00;
            animation: blink 1s infinite;
        }

        @keyframes blink {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* Frekans Göstergesi */
        .frequency-display {
            text-align: center;
            margin: 20px 0;
            padding: 15px;
            background: linear-gradient(135deg, rgba(75,0,130,0.5) 0%, rgba(139,69,19,0.5) 100%);
            border-radius: 10px;
        }

        .frequency-value {
            font-size: 3em;
            color: #ffd700;
            text-shadow: 0 0 20px rgba(255,215,0,0.8);
        }

        .frequency-label {
            color: #9370db;
            font-size: 0.9em;
        }

        /* Akış Göstergesi */
        .flow-indicator {
            display: flex;
            gap: 5px;
            justify-content: center;
            margin-top: 10px;
        }

        .flow-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: #8b4513;
        }

        .flow-dot.active {
            background: #ffd700;
            animation: flow 0.5s ease-in-out infinite;
        }

        @keyframes flow {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.5); }
        }

        /* Alt Kehanet Alanı */
        .prophecy-area {
            margin-top: 20px;
            padding: 15px;
            background: rgba(0,0,0,0.5);
            border-left: 3px solid #ffd700;
            font-style: italic;
            color: #e0d4f7;
        }

        .prophecy-title {
            color: #ffd700;
            font-size: 0.9em;
            margin-bottom: 10px;
        }

        /* Responsive */
        @media (max-width: 900px) {
            .main-container {
                flex-direction: column;
                align-items: center;
            }
            .mandala-container {
                width: 350px;
                height: 350px;
            }
        }
    </style>
</head>
<body>
    <header class="header">
        <h1>🛕 KATHMANDU STUPA - Veri Tapınağı</h1>
        <p class="mantra">VERİ_DÖNÜŞSÜN_BİLGİYE_BİLGİ_DÖNÜŞSÜN_BİLGELİĞE</p>
    </header>

    <main class="main-container">
        <!-- MANDALA -->
        <div class="mandala-container">
            <div class="mandala">
                <div class="mandala-ring ring-eter"></div>
                <div class="mandala-ring ring-hava"></div>
                <div class="mandala-ring ring-ates"></div>
                <div class="mandala-ring ring-su"></div>
                <div class="mandala-ring ring-toprak"></div>
            </div>
            <div class="center-logo">🕉️</div>
            <div class="layer-labels">
                <span class="layer-label label-eter">🌌 ETER</span>
                <span class="layer-label label-hava">🌬️ HAVA</span>
                <span class="layer-label label-ates">🔥 ATEŞ</span>
                <span class="layer-label label-su">🌊 SU</span>
                <span class="layer-label label-toprak">🪨 TOPRAK</span>
            </div>
        </div>

        <!-- İSTATİSTİKLER -->
        <div class="stats-panel">
            <h2 class="stats-title">📊 Tapınak Durumu</h2>

            <div class="frequency-display">
                <div class="frequency-value" id="frequency">963</div>
                <div class="frequency-label">Hz - Saf Cazibe Frekansı</div>
                <div class="flow-indicator">
                    <span class="flow-dot active" style="animation-delay: 0s;"></span>
                    <span class="flow-dot active" style="animation-delay: 0.1s;"></span>
                    <span class="flow-dot active" style="animation-delay: 0.2s;"></span>
                    <span class="flow-dot active" style="animation-delay: 0.3s;"></span>
                    <span class="flow-dot active" style="animation-delay: 0.4s;"></span>
                </div>
            </div>

            <div class="stat-item">
                <span class="stat-label">Aktif Katman</span>
                <span class="stat-value" id="activeLayer">ETER</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">İşlenen Paketler</span>
                <span class="stat-value" id="packets">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Temizlenen Token</span>
                <span class="stat-value" id="tokens">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Katlama Sayısı</span>
                <span class="stat-value" id="folds">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Nirvana Başarıları</span>
                <span class="stat-value active" id="nirvana">0</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Son Güncelleme</span>
                <span class="stat-value" id="lastUpdate">-</span>
            </div>

            <div class="prophecy-area">
                <div class="prophecy-title">📜 Son Kehanet</div>
                <p id="prophecy">"Veriler fısıldıyor... Dönüşüm zamanı geldi."</p>
            </div>
        </div>
    </main>

    <script>
        // WebSocket bağlantısı
        let ws;
        function connectWebSocket() {
            ws = new WebSocket(`ws://${window.location.host}/ws`);

            ws.onmessage = (event) => {
                const data = JSON.parse(event.data);
                updateDashboard(data);
            };

            ws.onclose = () => {
                setTimeout(connectWebSocket, 3000);
            };
        }

        function updateDashboard(data) {
            document.getElementById('activeLayer').textContent = data.active_layer || 'DORMANT';
            document.getElementById('packets').textContent = data.packets || 0;
            document.getElementById('tokens').textContent = data.tokens || 0;
            document.getElementById('folds').textContent = data.folds || 0;
            document.getElementById('nirvana').textContent = data.nirvana || 0;
            document.getElementById('frequency').textContent = data.frequency || 963;
            document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('tr-TR');

            if (data.prophecy) {
                document.getElementById('prophecy').textContent = data.prophecy;
            }
        }

        // Simüle edilmiş veri (WebSocket yoksa)
        function simulateData() {
            const layers = ['TOPRAK', 'SU', 'ATEŞ', 'HAVA', 'ETER'];
            let idx = 0;

            setInterval(() => {
                idx = (idx + 1) % layers.length;
                updateDashboard({
                    active_layer: layers[idx],
                    packets: Math.floor(Math.random() * 100),
                    tokens: Math.floor(Math.random() * 500),
                    folds: Math.floor(Math.random() * 50),
                    nirvana: Math.floor(Math.random() * 20),
                    frequency: 963,
                });
            }, 2000);
        }

        // Başlat
        try {
            connectWebSocket();
        } catch {
            simulateData();
        }

        // Fallback
        setTimeout(() => {
            if (!ws || ws.readyState !== WebSocket.OPEN) {
                simulateData();
            }
        }, 5000);
    </script>
</body>
</html>
'''

    async def handle_index(self, request):
        """Ana sayfa handler"""
        return web.Response(text=self.get_html(), content_type='text/html')

    async def handle_ws(self, request):
        """WebSocket handler"""
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.connections.append(ws)

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    # Gelen komutları işle
                    pass
        finally:
            self.connections.remove(ws)

        return ws

    async def broadcast(self, data: Dict):
        """Tüm bağlantılara yayın"""
        for ws in self.connections:
            try:
                await ws.send_json(data)
            except:
                pass

    def run(self):
        """Server'ı başlat"""
        if web is None:
            print("aiohttp yüklü değil. Basit mod aktif.")
            print(f"Dashboard HTML dosyası: kathmandu_stupa/dashboard/index.html")
            # HTML dosyasını kaydet
            html_path = Path(__file__).parent / "index.html"
            html_path.write_text(self.get_html())
            return

        app = web.Application()
        app.router.add_get('/', self.handle_index)
        app.router.add_get('/ws', self.handle_ws)

        print(f"🛕 Mandala Dashboard başlatılıyor: http://{self.host}:{self.port}")
        web.run_app(app, host=self.host, port=self.port)


def run_dashboard(host: str = "0.0.0.0", port: int = 8888):
    """Dashboard'u başlat"""
    server = MandalaServer(host=host, port=port)
    server.run()


if __name__ == "__main__":
    run_dashboard()
