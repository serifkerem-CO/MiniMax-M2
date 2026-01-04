"""
MANDALA RENDERER - Mandala Goruntuleyici
========================================
Donen mandala arayuzu - Klasik grafikler yerine mistik dashboard
"""

from datetime import datetime
from typing import Any, Optional
import json
import math


class MandalaRenderer:
    """
    Mandala Dashboard Renderer

    Merkezde CAZIBE logosu, etrafinda donen sektorler.
    Veri akarken renk degisir.
    """

    # Katman renkleri (5 element)
    LAYER_COLORS = {
        "TOPRAK": "#8B4513",  # Kahverengi - Toprak
        "SU": "#4169E1",       # Mavi - Su
        "ATES": "#FF4500",     # Turuncu/Kirmizi - Ates
        "HAVA": "#87CEEB",     # Acik Mavi - Hava
        "ETER": "#9370DB",     # Mor - Eter
    }

    # Frekans renkleri
    FREQUENCY_COLORS = {
        7.83: "#654321",    # Schumann - Toprak tonu
        432: "#1E90FF",     # Harmonik - Su tonu
        528: "#FF6347",     # DNA - Ates tonu
        639: "#00CED1",     # Baglanti - Hava tonu
        963: "#8A2BE2",     # Birlik - Eter tonu
    }

    def render_dashboard(self) -> str:
        """
        HTML Dashboard Render

        Donen mandala ile canli istatistikler.
        """
        html = """
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>KATMANDU ENGINE - Mandala Dashboard</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            color: #e0e0e0;
            overflow-x: hidden;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            text-align: center;
            padding: 40px 0;
        }

        h1 {
            font-size: 3em;
            background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3, #54a0ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradient 3s ease infinite;
            background-size: 300% 300%;
        }

        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .mantra {
            font-size: 1.2em;
            color: #888;
            margin-top: 10px;
            letter-spacing: 3px;
        }

        .mandala-container {
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 40px 0;
        }

        .mandala {
            width: 500px;
            height: 500px;
            position: relative;
            animation: spin 60s linear infinite;
        }

        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }

        .mandala-ring {
            position: absolute;
            border-radius: 50%;
            border: 3px solid;
            opacity: 0.8;
        }

        .ring-eter {
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            border-color: #9370DB;
            animation: pulse 2s ease-in-out infinite;
        }

        .ring-hava {
            width: 80%;
            height: 80%;
            top: 10%;
            left: 10%;
            border-color: #87CEEB;
            animation: pulse 2.5s ease-in-out infinite;
        }

        .ring-ates {
            width: 60%;
            height: 60%;
            top: 20%;
            left: 20%;
            border-color: #FF4500;
            animation: pulse 3s ease-in-out infinite;
        }

        .ring-su {
            width: 40%;
            height: 40%;
            top: 30%;
            left: 30%;
            border-color: #4169E1;
            animation: pulse 3.5s ease-in-out infinite;
        }

        .ring-toprak {
            width: 20%;
            height: 20%;
            top: 40%;
            left: 40%;
            border-color: #8B4513;
            animation: pulse 4s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 0.5; transform: scale(1); }
            50% { opacity: 1; transform: scale(1.02); }
        }

        .center-logo {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 80px;
            height: 80px;
            background: linear-gradient(45deg, #ff6b6b, #feca57);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 2em;
            animation: glow 2s ease-in-out infinite;
            z-index: 10;
        }

        @keyframes glow {
            0%, 100% { box-shadow: 0 0 20px rgba(255,107,107,0.5); }
            50% { box-shadow: 0 0 40px rgba(254,202,87,0.8); }
        }

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 40px;
        }

        .stat-card {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 25px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }

        .stat-card h3 {
            font-size: 0.9em;
            color: #888;
            text-transform: uppercase;
            letter-spacing: 2px;
            margin-bottom: 10px;
        }

        .stat-card .value {
            font-size: 2.5em;
            font-weight: bold;
            background: linear-gradient(45deg, #48dbfb, #ff9ff3);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stat-card .unit {
            font-size: 0.8em;
            color: #666;
        }

        .layer-card {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .layer-icon {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
        }

        .layer-toprak { background: linear-gradient(45deg, #8B4513, #A0522D); }
        .layer-su { background: linear-gradient(45deg, #4169E1, #1E90FF); }
        .layer-ates { background: linear-gradient(45deg, #FF4500, #FF6347); }
        .layer-hava { background: linear-gradient(45deg, #87CEEB, #00CED1); }
        .layer-eter { background: linear-gradient(45deg, #9370DB, #8A2BE2); }

        .frequency-bar {
            width: 100%;
            height: 8px;
            background: rgba(255,255,255,0.1);
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }

        .frequency-fill {
            height: 100%;
            border-radius: 4px;
            animation: flow 2s ease-in-out infinite;
        }

        @keyframes flow {
            0% { width: 0%; }
            50% { width: 100%; }
            100% { width: 0%; }
        }

        .api-section {
            margin-top: 40px;
            background: rgba(0,0,0,0.3);
            border-radius: 15px;
            padding: 30px;
        }

        .api-section h2 {
            margin-bottom: 20px;
            color: #feca57;
        }

        .endpoint {
            background: rgba(255,255,255,0.05);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 10px;
            font-family: monospace;
        }

        .method {
            display: inline-block;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: bold;
            margin-right: 10px;
        }

        .method-get { background: #28a745; }
        .method-post { background: #007bff; }

        footer {
            text-align: center;
            padding: 40px;
            color: #666;
        }

        .om {
            font-size: 3em;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>KATMANDU ENGINE</h1>
            <p class="mantra">VERI_DONUSSUN_BILGIYE_BILGI_DONUSSUN_BILGELEGE</p>
        </header>

        <div class="mandala-container">
            <div class="mandala">
                <div class="mandala-ring ring-eter"></div>
                <div class="mandala-ring ring-hava"></div>
                <div class="mandala-ring ring-ates"></div>
                <div class="mandala-ring ring-su"></div>
                <div class="mandala-ring ring-toprak"></div>
                <div class="center-logo">CAZ</div>
            </div>
        </div>

        <div class="stats-grid">
            <div class="stat-card layer-card">
                <div class="layer-icon layer-toprak">1</div>
                <div>
                    <h3>TOPRAK - Kaos</h3>
                    <div class="value" id="toprak-count">0</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="background: #8B4513;"></div>
                    </div>
                    <div class="unit">7.83 Hz - Schumann</div>
                </div>
            </div>

            <div class="stat-card layer-card">
                <div class="layer-icon layer-su">2</div>
                <div>
                    <h3>SU - Arinma</h3>
                    <div class="value" id="su-count">0</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="background: #4169E1;"></div>
                    </div>
                    <div class="unit">432 Hz - Harmonik</div>
                </div>
            </div>

            <div class="stat-card layer-card">
                <div class="layer-icon layer-ates">3</div>
                <div>
                    <h3>ATES - Donusum</h3>
                    <div class="value" id="ates-count">0</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="background: #FF4500;"></div>
                    </div>
                    <div class="unit">528 Hz - DNA Onarim</div>
                </div>
            </div>

            <div class="stat-card layer-card">
                <div class="layer-icon layer-hava">4</div>
                <div>
                    <h3>HAVA - Vizyon</h3>
                    <div class="value" id="hava-count">0</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="background: #87CEEB;"></div>
                    </div>
                    <div class="unit">639 Hz - Baglanti</div>
                </div>
            </div>

            <div class="stat-card layer-card">
                <div class="layer-icon layer-eter">5</div>
                <div>
                    <h3>ETER - Cazibe</h3>
                    <div class="value" id="eter-count">0</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="background: #9370DB;"></div>
                    </div>
                    <div class="unit">963 Hz - Birlik</div>
                </div>
            </div>

            <div class="stat-card">
                <h3>Toplam Yolculuk</h3>
                <div class="value" id="journey-count">0</div>
                <div class="unit">islem tamamlandi</div>
            </div>

            <div class="stat-card">
                <h3>Ortalama Buda Potansiyeli</h3>
                <div class="value" id="buddha-potential">0%</div>
                <div class="unit">sektor liderlik skoru</div>
            </div>

            <div class="stat-card">
                <h3>Tapinak Modu</h3>
                <div class="value" id="stupa-mode">TEMPLE</div>
                <div class="unit">aktif durum</div>
            </div>
        </div>

        <div class="api-section">
            <h2>API Endpointleri</h2>

            <div class="endpoint">
                <span class="method method-post">POST</span>
                <code>/process</code> - Veri isleme (5 katman)
            </div>

            <div class="endpoint">
                <span class="method method-post">POST</span>
                <code>/batch</code> - Toplu islem
            </div>

            <div class="endpoint">
                <span class="method method-post">POST</span>
                <code>/prayer-wheel/spin</code> - Dua carki dondur
            </div>

            <div class="endpoint">
                <span class="method method-get">GET</span>
                <code>/stats</code> - Istatistikler
            </div>

            <div class="endpoint">
                <span class="method method-get">GET</span>
                <code>/mandala</code> - Mandala JSON
            </div>

            <div class="endpoint">
                <span class="method method-get">GET</span>
                <code>/docs</code> - Swagger UI
            </div>
        </div>

        <footer>
            <div class="om">OM</div>
            <p>Om Mani Padme Hum</p>
            <p style="margin-top: 10px;">CAZIBE.IO - "Sizin veriniz var, bizim ise Gorumuz var."</p>
        </footer>
    </div>

    <script>
        // Canli istatistik guncelleme
        async function updateStats() {
            try {
                const response = await fetch('/stats');
                const data = await response.json();

                if (data.layers) {
                    document.getElementById('toprak-count').textContent =
                        data.layers.toprak?.total_collected || 0;
                    document.getElementById('su-count').textContent =
                        data.layers.su?.total_purified || 0;
                    document.getElementById('ates-count').textContent =
                        data.layers.ates?.total_forged || 0;
                    document.getElementById('hava-count').textContent =
                        data.layers.hava?.total_transmissions || 0;
                    document.getElementById('eter-count').textContent =
                        data.layers.eter?.total_crystallized || 0;

                    const buddhaAvg = data.layers.eter?.average_buddha_potential || 0;
                    document.getElementById('buddha-potential').textContent =
                        (buddhaAvg * 100).toFixed(1) + '%';
                }

                document.getElementById('journey-count').textContent =
                    data.total_journeys || 0;
                document.getElementById('stupa-mode').textContent =
                    (data.mode || 'dormant').toUpperCase();

            } catch (e) {
                console.log('Stats update failed:', e);
            }
        }

        // Her 3 saniyede guncelle
        setInterval(updateStats, 3000);
        updateStats();
    </script>
</body>
</html>
        """
        return html

    def render_json(self, stupa: Any) -> dict:
        """
        Mandala JSON Render

        Tum katmanlarin durumunu JSON olarak dondurur.
        """
        stats = stupa.get_stupa_stats() if stupa else {}

        mandala = {
            "title": "KATMANDU MANDALA",
            "timestamp": datetime.now().isoformat(),
            "center": {
                "name": "CAZIBE",
                "frequency_hz": 963,
                "color": self.LAYER_COLORS["ETER"]
            },
            "rings": []
        }

        # Katmanlari halka olarak ekle (disaridan iceriye)
        layer_order = ["ETER", "HAVA", "ATES", "SU", "TOPRAK"]
        frequencies = [963, 639, 528, 432, 7.83]

        for i, (layer_name, freq) in enumerate(zip(layer_order, frequencies)):
            layer_stats = stats.get("layers", {}).get(layer_name.lower(), {})

            ring = {
                "level": i + 1,
                "name": layer_name,
                "frequency_hz": freq,
                "color": self.LAYER_COLORS.get(layer_name, "#FFFFFF"),
                "radius_percent": 100 - (i * 20),
                "stats": layer_stats,
                "active": layer_stats.get("total_collected", 0) > 0 or
                          layer_stats.get("total_purified", 0) > 0 or
                          layer_stats.get("total_forged", 0) > 0 or
                          layer_stats.get("total_transmissions", 0) > 0 or
                          layer_stats.get("total_crystallized", 0) > 0
            }

            mandala["rings"].append(ring)

        # Genel istatistikler
        mandala["meta"] = {
            "mode": stats.get("mode", "dormant"),
            "mantra": stats.get("mantra", "VERI_DONUSSUN_BILGIYE"),
            "total_journeys": stats.get("total_journeys", 0),
            "philosophy": "Sizin veriniz var, bizim ise Gorumuz var."
        }

        return mandala

    def render_parchment_html(self, content: str) -> str:
        """Parsomen HTML formati"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Kehanet Parsomeni</title>
    <style>
        body {{
            background: #1a1a2e;
            color: #e0e0e0;
            font-family: 'Courier New', monospace;
            padding: 40px;
            display: flex;
            justify-content: center;
        }}
        .parchment {{
            background: linear-gradient(135deg, #2d2d44 0%, #1a1a2e 100%);
            border: 2px solid #4a4a6a;
            border-radius: 10px;
            padding: 30px;
            max-width: 800px;
            box-shadow: 0 0 30px rgba(147, 112, 219, 0.3);
            white-space: pre-wrap;
        }}
    </style>
</head>
<body>
    <div class="parchment">{content}</div>
</body>
</html>
        """
