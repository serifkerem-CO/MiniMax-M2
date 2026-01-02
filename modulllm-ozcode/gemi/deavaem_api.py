"""
DEAVAEM Gemisi - Su Soğutmalı GPU Cluster API

MODULllm.com'un fiziksel gücü - gemideki sunucular!
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
import httpx


class GemiKaynak(str, Enum):
    """Gemi kaynakları"""
    GPU_CLUSTER = "gpu_cluster"          # GPU cluster (inference)
    CPU_CLUSTER = "cpu_cluster"          # CPU cluster (genel işlem)
    STORAGE = "storage"                  # Depolama
    NETWORK = "network"                  # Ağ kaynağı
    COOLING_SYSTEM = "cooling_system"    # Su soğutma sistemi


@dataclass
class GemiDurum:
    """Gemi sistem durumu"""
    online: bool
    sicaklik: float              # Su sıcaklığı (°C)
    gpu_kullanim: float          # GPU kullanım oranı (%)
    cpu_kullanim: float          # CPU kullanım oranı (%)
    bellek_kullanim: float       # RAM kullanım oranı (%)
    aktif_islemler: int          # Şu an kaç işlem çalışıyor
    kuyruk: int                  # Kuyrukta bekleyen işlem
    su_sogutma_akis: float       # Su akış hızı (L/dk)
    enerji_tuketim: float        # Enerji tüketimi (W)


@dataclass
class GemiIsTask:
    """Gemiye gönderilen iş"""
    task_id: str
    task_type: str               # "llm_inference", "data_processing", etc.
    priority: int                # 1-11 (11 en yüksek)
    kaynak: GemiKaynak
    payload: Dict[str, Any]
    modulllm_exclusive: bool = True  # Sadece MODULllm için mi?


class DeavaemGemiAPI:
    """
    DEAVAEM Gemisi API Client

    Gemideki su soğutmalı sunuculara erişim
    """

    def __init__(
        self,
        gemi_endpoint: str = "http://gemi.modulllm.com:8000",
        api_key: Optional[str] = None
    ):
        self.endpoint = gemi_endpoint
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=60)

    async def durum_sorgula(self) -> GemiDurum:
        """Gemi sistem durumunu sorgula"""
        try:
            response = await self.client.get(
                f"{self.endpoint}/api/durum",
                headers={"X-API-Key": self.api_key} if self.api_key else {}
            )

            data = response.json()

            return GemiDurum(
                online=data.get("online", True),
                sicaklik=data.get("sicaklik", 25.0),
                gpu_kullanim=data.get("gpu_kullanim", 0.0),
                cpu_kullanim=data.get("cpu_kullanim", 0.0),
                bellek_kullanim=data.get("bellek_kullanim", 0.0),
                aktif_islemler=data.get("aktif_islemler", 0),
                kuyruk=data.get("kuyruk", 0),
                su_sogutma_akis=data.get("su_sogutma_akis", 100.0),
                enerji_tuketim=data.get("enerji_tuketim", 1000.0)
            )

        except Exception as e:
            print(f"⚠️ Gemi durum sorgulama hatası: {e}")
            # Offline durumu dön
            return GemiDurum(
                online=False,
                sicaklik=0.0,
                gpu_kullanim=0.0,
                cpu_kullanim=0.0,
                bellek_kullanim=0.0,
                aktif_islemler=0,
                kuyruk=0,
                su_sogutma_akis=0.0,
                enerji_tuketim=0.0
            )

    async def llm_inference_gonder(
        self,
        model: str,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2000,
        priority: int = 5
    ) -> Dict[str, Any]:
        """
        Gemideki LLM'e inference isteği gönder

        Self-hosted LLM'ler gemide çalışıyor!
        """
        try:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt} if system_prompt else None,
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": False
            }

            # None'ları filtrele
            payload["messages"] = [m for m in payload["messages"] if m is not None]

            response = await self.client.post(
                f"{self.endpoint}/api/llm/inference",
                json=payload,
                headers={
                    "X-API-Key": self.api_key,
                    "X-Priority": str(priority),
                    "X-MODULllm-Exclusive": "true"
                } if self.api_key else {}
            )

            result = response.json()

            return {
                "success": True,
                "response": result.get("choices", [{}])[0].get("message", {}).get("content", ""),
                "model": model,
                "tokens_used": result.get("usage", {}).get("total_tokens", 0),
                "gemi_task_id": result.get("task_id", "unknown")
            }

        except Exception as e:
            print(f"⚠️ Gemi LLM inference hatası: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "",
                "model": model
            }

    async def gpu_cluster_kullan(
        self,
        script_path: str,
        args: Dict[str, Any],
        gpu_count: int = 1
    ) -> Dict[str, Any]:
        """
        Gemideki GPU cluster'da script çalıştır

        Örnekler:
        - Model training
        - Büyük veri analizi
        - Rendering
        """
        try:
            task = GemiIsTask(
                task_id=f"gpu_{asyncio.current_task().get_name()}",
                task_type="gpu_compute",
                priority=8,
                kaynak=GemiKaynak.GPU_CLUSTER,
                payload={
                    "script": script_path,
                    "args": args,
                    "gpu_count": gpu_count
                },
                modulllm_exclusive=True
            )

            response = await self.client.post(
                f"{self.endpoint}/api/gpu/execute",
                json={
                    "task_id": task.task_id,
                    "gpu_count": gpu_count,
                    "script": script_path,
                    "args": args
                },
                headers={"X-API-Key": self.api_key} if self.api_key else {}
            )

            result = response.json()

            return {
                "success": True,
                "task_id": result.get("task_id"),
                "status": result.get("status"),
                "estimated_time": result.get("estimated_time", "unknown")
            }

        except Exception as e:
            print(f"⚠️ GPU cluster hatası: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    async def task_durumu_sorgula(self, task_id: str) -> Dict[str, Any]:
        """Gönderilen task'ın durumunu sorgula"""
        try:
            response = await self.client.get(
                f"{self.endpoint}/api/task/{task_id}",
                headers={"X-API-Key": self.api_key} if self.api_key else {}
            )

            result = response.json()

            return {
                "task_id": task_id,
                "status": result.get("status"),  # pending, running, completed, failed
                "progress": result.get("progress", 0),  # 0-100
                "result": result.get("result"),
                "error": result.get("error")
            }

        except Exception as e:
            return {
                "task_id": task_id,
                "status": "error",
                "error": str(e)
            }

    async def su_sogutma_optimizasyon(self) -> Dict[str, Any]:
        """
        Su soğutma sistemini optimize et

        Geminin özel özelliği - su soğutma!
        Sıcaklık yüksekse akışı artır
        """
        durum = await self.durum_sorgula()

        oneriler = []

        if durum.sicaklik > 30:
            oneriler.append("⚠️ Sıcaklık yüksek! Su akışını artır.")
        elif durum.sicaklik < 20:
            oneriler.append("✅ Sıcaklık optimal. Su akışı normal.")

        if durum.gpu_kullanim > 80:
            oneriler.append("🔥 GPU yoğun kullanımda. Soğutma prioritize edilmeli.")

        return {
            "sicaklik": durum.sicaklik,
            "su_akis": durum.su_sogutma_akis,
            "oneriler": oneriler,
            "optimal": durum.sicaklik < 25 and durum.su_sogutma_akis > 80
        }

    async def istatistikler(self) -> Dict[str, Any]:
        """Gemi kullanım istatistikleri"""
        durum = await self.durum_sorgula()

        return {
            "gemi_online": durum.online,
            "sistem_durumu": {
                "sicaklik": f"{durum.sicaklik}°C",
                "gpu_kullanim": f"{durum.gpu_kullanim}%",
                "cpu_kullanim": f"{durum.cpu_kullanim}%",
                "bellek_kullanim": f"{durum.bellek_kullanim}%",
            },
            "is_yuku": {
                "aktif": durum.aktif_islemler,
                "kuyruk": durum.kuyruk
            },
            "su_sogutma": {
                "akis": f"{durum.su_sogutma_akis} L/dk",
                "enerji": f"{durum.enerji_tuketim} W"
            },
            "modulllm_exclusive": True,
            "mesaj": "🚢 DEAVAEM Gemisi - Su Soğutmalı Güç!"
        }

    async def close(self):
        """Cleanup"""
        await self.client.aclose()


# Test fonksiyonu
async def test_gemi_api():
    """Gemi API test"""
    gemi = DeavaemGemiAPI()

    print("\n🚢 DEAVAEM Gemisi Test Başlıyor...\n")

    # 1. Durum sorgula
    durum = await gemi.durum_sorgula()
    print(f"Gemi Online: {durum.online}")
    print(f"Sıcaklık: {durum.sicaklik}°C")
    print(f"GPU Kullanım: {durum.gpu_kullanim}%")
    print(f"Su Akış: {durum.su_sogutma_akis} L/dk")

    # 2. İstatistikler
    stats = await gemi.istatistikler()
    print(f"\n📊 İstatistikler:")
    print(f"{stats}")

    # 3. Su soğutma optimizasyonu
    sogutma = await gemi.su_sogutma_optimizasyon()
    print(f"\n❄️ Su Soğutma:")
    print(f"Optimal: {sogutma['optimal']}")
    print(f"Öneriler: {sogutma['oneriler']}")

    await gemi.close()


if __name__ == "__main__":
    asyncio.run(test_gemi_api())
