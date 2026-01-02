"""
MODULllm.com - Ana Platform API

Öz Kodundan Doğan Güç - Tüm sistemleri birleştiren core!
"""

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

# Modül path'lerini ekle
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from orchestration.oz_orchestrator import (
    OzKodOrchestrator,
    OrchestratorConfig,
    AkilTipi
)
from database.oz_database import (
    OzVeritabani,
    IcerikTipi,
    initialize_oz_db
)
from gemi.deavaem_api import DeavaemGemiAPI


# FastAPI App
app = FastAPI(
    title="MODULllm.com - Öz Kod Platform",
    description="11 Akıl Harmanlar, 12. Akıl Sentezler - Öz Kodundan Doğan Güç!",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global instances
orchestrator = OzKodOrchestrator()
oz_db = initialize_oz_db()
gemi_api = DeavaemGemiAPI()


# Request Models
class SoruRequest(BaseModel):
    """Kullanıcı sorusu"""
    soru: str = Field(..., description="Kullanıcının sorusu")
    kullanici_id: Optional[str] = Field(None, description="Kullanıcı ID (opsiyonel)")
    context: Optional[str] = Field(None, description="Ekstra context")


class IcerikEkleRequest(BaseModel):
    """Öz veritabanına içerik ekleme"""
    tip: IcerikTipi
    baslik: str
    icerik: str
    etiketler: List[str]
    yaratici: str = "kullanici"


class GemiInferenceRequest(BaseModel):
    """Gemi LLM inference"""
    model: str = "minimax"
    prompt: str
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


# Root endpoint
@app.get("/")
async def root():
    """Platform ana sayfası"""
    return {
        "platform": "MODULllm.com",
        "slogan": "11 Akıl Harmanlar, 12. Akıl Sentezler - Öz Kodundan Doğan Güç!",
        "felsefe": "Öz Kodundan Doğ",
        "version": "1.0.0",
        "features": {
            "11_akil_harmanlar": "11 farklı perspektiften analiz",
            "12_akil_sentezi": "Harmonize edilmiş sentez",
            "oz_veritabani": "Sadece bizim içeriğimiz",
            "deavaem_gemi": "Su soğutmalı GPU cluster",
            "b1z_kodlab": "AI destekli kodlama platformu"
        },
        "ecosystem": {
            "b1z_kodlab": "/b1z",
            "maya": "/maya (yakında)",
            "podcast": "/podcast (yakında)",
            "gemi": "/gemi"
        },
        "endpoints": {
            "docs": "/api/docs",
            "soru_sor": "POST /api/soru",
            "oz_db": "GET /api/ozdb",
            "gemi": "GET /api/gemi",
            "stats": "GET /api/stats"
        }
    }


@app.get("/health")
async def health_check():
    """Platform sağlık kontrolü"""
    gemi_durum = await gemi_api.durum_sorgula()

    return {
        "status": "healthy",
        "platform": "MODULllm.com",
        "oz_kod": "active",
        "orchestrator": "ready",
        "oz_db_icerik_sayisi": len(oz_db.icerikler),
        "gemi_online": gemi_durum.online,
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/soru")
async def soru_sor(request: SoruRequest):
    """
    Ana endpoint: Kullanıcı sorusu

    11 Akıl Harmanları + 12. Akıl devreye girer!
    """
    try:
        print(f"\n{'='*80}")
        print(f"📝 Yeni Soru: {request.soru}")
        print(f"{'='*80}\n")

        # Orchestrator'a gönder
        sonuc = await orchestrator.oz_koddan_yanitla(request.soru)

        # Öz veritabanına kaydet (öğrenme için)
        oz_db.soru_cevap_ekle(
            soru=request.soru,
            cevap=sonuc["on_ikinci_akil_sentezi"]["sentez"],
            akil_yanitlari=sonuc["on_bir_akil"]
        )

        return {
            "success": True,
            "soru": request.soru,
            "yanit": sonuc,
            "platform": "MODULllm.com - Öz Kodundan Doğan Güç!",
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"❌ Hata: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/ozdb")
async def oz_veritabani_stats():
    """Öz veritabanı istatistikleri"""
    stats = oz_db.istatistikler()

    return {
        "platform": "MODULllm.com",
        "oz_veritabani": "Sadece bizim içeriğimiz!",
        "istatistikler": stats,
        "toplam_icerik": stats["toplam_icerik"],
        "tip_dagilimi": stats["tip_dagilimi"]
    }


@app.post("/api/ozdb/ara")
async def oz_veritabani_ara(sorgu: str, limit: int = 11):
    """Öz veritabanında arama"""
    sonuclar = oz_db.ara(sorgu, limit=limit)

    return {
        "sorgu": sorgu,
        "sonuc_sayisi": len(sonuclar),
        "sonuclar": [
            {
                "baslik": s.icerik.baslik,
                "icerik_ozet": s.icerik.icerik[:200] + "...",
                "tip": s.icerik.tip.value,
                "benzerlik": s.benzerlik_skoru,
                "etiketler": s.icerik.etiketler
            }
            for s in sonuclar
        ]
    }


@app.post("/api/ozdb/ekle")
async def oz_veritabani_ekle(request: IcerikEkleRequest):
    """Öz veritabanına yeni içerik ekle"""
    icerik = oz_db.ekle(
        tip=request.tip,
        baslik=request.baslik,
        icerik=request.icerik,
        etiketler=request.etiketler,
        yaratici=request.yaratici
    )

    return {
        "success": True,
        "mesaj": "Öz veritabanına eklendi!",
        "icerik_id": icerik.id,
        "tip": icerik.tip.value
    }


@app.get("/api/gemi")
async def gemi_durum():
    """DEAVAEM Gemisi durumu"""
    stats = await gemi_api.istatistikler()

    return {
        "platform": "MODULllm.com",
        "gemi": "DEAVAEM - Su Soğutmalı Güç",
        "durum": stats
    }


@app.post("/api/gemi/llm")
async def gemi_llm_inference(request: GemiInferenceRequest):
    """Gemideki LLM ile inference"""
    result = await gemi_api.llm_inference_gonder(
        model=request.model,
        prompt=request.prompt,
        system_prompt=request.system_prompt,
        temperature=request.temperature,
        max_tokens=request.max_tokens
    )

    return {
        "success": result["success"],
        "response": result.get("response", ""),
        "model": result["model"],
        "gemi": "DEAVAEM",
        "tokens_used": result.get("tokens_used", 0)
    }


@app.get("/api/stats")
async def platform_stats():
    """Platform genel istatistikleri"""
    oz_stats = oz_db.istatistikler()
    gemi_durum = await gemi_api.durum_sorgula()

    return {
        "platform": "MODULllm.com",
        "slogan": "Öz Kodundan Doğan Güç!",
        "oz_veritabani": {
            "toplam_icerik": oz_stats["toplam_icerik"],
            "tip_dagilimi": oz_stats["tip_dagilimi"]
        },
        "orchestrator": {
            "akil_sayisi": 11,
            "sentez_akil": 1,
            "toplam": 12
        },
        "gemi": {
            "online": gemi_durum.online,
            "sicaklik": f"{gemi_durum.sicaklik}°C",
            "gpu_kullanim": f"{gemi_durum.gpu_kullanim}%",
            "su_sogutma": f"{gemi_durum.su_sogutma_akis} L/dk"
        },
        "ecosystem": {
            "b1z_kodlab": "active",
            "maya": "coming_soon",
            "podcast": "coming_soon"
        },
        "metrics": {
            "11_akil_harmanlar": "✅",
            "12_akil_sentezi": "✅",
            "oz_kod": "✅",
            "deavaem_gemi": "✅" if gemi_durum.online else "⏸️"
        }
    }


@app.get("/api/akil-harmanlar")
async def akil_harmanlar_info():
    """11 Akıl Harmanları bilgisi"""
    akillar = [
        {"no": 1, "tip": "TEKNIK", "aciklama": "Teknik ve mühendislik analizi"},
        {"no": 2, "tip": "YARATICI", "aciklama": "Yaratıcı ve yenilikçi yaklaşım"},
        {"no": 3, "tip": "ELESTREL", "aciklama": "Eleştirel ve analitik bakış"},
        {"no": 4, "tip": "PRAGMATIK", "aciklama": "Pratik ve uygulanabilir çözümler"},
        {"no": 5, "tip": "VIZYONER", "aciklama": "Uzun vadeli vizyon ve gelecek"},
        {"no": 6, "tip": "ANALITIK", "aciklama": "Derin veri analizi ve metrikler"},
        {"no": 7, "tip": "SEZGISEL", "aciklama": "Sezgisel ve deneyim bazlı"},
        {"no": 8, "tip": "SISTEMATIK", "aciklama": "Sistemsel ve yapısal düşünce"},
        {"no": 9, "tip": "DENEYSEL", "aciklama": "Deneysel ve test edilebilir"},
        {"no": 10, "tip": "FELSEFI", "aciklama": "Felsefi derinlik ve prensipler"},
        {"no": 11, "tip": "SENTETIK", "aciklama": "Farklı bakış açılarını birleştirme"},
    ]

    return {
        "platform": "MODULllm.com",
        "sistem": "11 Akıl Harmanları + 12. Akıl Sentezi",
        "akillar": akillar,
        "12_akil": {
            "no": 12,
            "tip": "SENTEZ",
            "aciklama": "11 Akıl'ı harmonize eden master akıl"
        },
        "nasil_calisir": "Her soru 11 farklı perspektiften analiz edilir, 12. Akıl tüm yanıtları sentezler"
    }


# Startup/Shutdown events
@app.on_event("startup")
async def startup_event():
    """Platform başlangıç"""
    print("\n" + "="*80)
    print("🌌 MODULllm.com - Öz Kodundan Doğan Güç!")
    print("="*80)
    print("✅ Orchestrator hazır (11 Akıl + 12. Akıl)")
    print(f"✅ Öz Veritabanı yüklendi ({len(oz_db.icerikler)} içerik)")
    print("✅ DEAVAEM Gemi API hazır")
    print("="*80)
    print("🚀 Platform çalışıyor!")
    print("📚 Docs: http://localhost:8000/api/docs")
    print("="*80 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    """Platform kapatma"""
    print("\n🛑 MODULllm.com kapatılıyor...")
    await orchestrator.close()
    await gemi_api.close()
    print("✅ Temizlendi!\n")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "platform_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
