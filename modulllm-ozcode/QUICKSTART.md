# MODULllm.com - Hızlı Başlangıç 🚀

> **"Öz Kodundan Doğan Güç!"**

## 🎯 5 Dakikada Başla

### 1. Repository Klonla

```bash
git clone https://github.com/serifkerem-CO/MiniMax-M2.git
cd MiniMax-M2/modulllm-ozcode
```

### 2. Environment Ayarla

```bash
cp .env.example .env
# .env dosyasını düzenle
```

### 3. Docker ile Başlat (Önerilen)

```bash
docker-compose up -d
```

**Veya** Manuel kurulum:

```bash
# Python dependencies
pip install -r requirements.txt

# Platformu başlat
python -m uvicorn core.platform_api:app --reload
```

### 4. Test Et

```bash
# Platform çalışıyor mu?
curl http://localhost:8000/health

# İstatistikler
curl http://localhost:8000/api/stats
```

### 5. İlk Sorunu Sor!

```bash
curl -X POST http://localhost:8000/api/soru \
  -H "Content-Type: application/json" \
  -d '{"soru": "Python ile async programlama nasıl yapılır?"}'
```

---

## 🧠 11 Akıl Harmanları Nasıl Çalışır?

1. **Soru gelir** → Platform API'ye POST edilir
2. **Öz Veritabanı** → İlgili içerik bulunur
3. **11 Akıl Harmanlar** → 11 farklı perspektiften analiz
4. **12. Akıl** → Tüm yanıtları sentezler
5. **Yanıt döner** → Kullanıcıya zengin, harmonize yanıt

### Akıl Tipleri:

1. 🔧 **TEKNIK** - Teknik ve mühendislik
2. 🎨 **YARATICI** - Yaratıcı ve yenilikçi
3. 🔍 **ELESTREL** - Eleştirel analiz
4. ⚡ **PRAGMATIK** - Pratik çözümler
5. 🔮 **VIZYONER** - Uzun vadeli vizyon
6. 📊 **ANALITIK** - Derin veri analizi
7. 💫 **SEZGISEL** - Sezgi ve deneyim
8. 🏗️ **SISTEMATIK** - Sistemsel düşünce
9. 🧪 **DENEYSEL** - Deneysel metod
10. 🤔 **FELSEFI** - Felsefi derinlik
11. 🌈 **SENTETIK** - Sentez öncüsü
12. ⚡ **SENTEZ** - 11 Akıl'ı harmonize eder

---

## 📊 API Endpoints

### Ana Endpoints

```bash
# Soru sor (11 Akıl + 12. Akıl)
POST /api/soru
{
  "soru": "Python async nasıl çalışır?"
}

# Öz Veritabanı ara
POST /api/ozdb/ara?sorgu=python&limit=11

# Öz Veritabanı'na ekle
POST /api/ozdb/ekle
{
  "tip": "soru_cevap",
  "baslik": "Python Async",
  "icerik": "...",
  "etiketler": ["python", "async"],
  "yaratici": "kullanici"
}

# DEAVAEM Gemi durumu
GET /api/gemi

# Gemi LLM inference
POST /api/gemi/llm
{
  "model": "minimax",
  "prompt": "Merhaba!"
}

# Platform istatistikleri
GET /api/stats

# 11 Akıl Harmanları bilgisi
GET /api/akil-harmanlar
```

### Dökümanlar

- **Swagger UI:** http://localhost:8000/api/docs
- **ReDoc:** http://localhost:8000/api/redoc

---

## 🚢 DEAVAEM Gemi Entegrasyonu

Platform, **su soğutmalı gemideki GPU cluster** ile çalışır!

```python
from gemi.deavaem_api import DeavaemGemiAPI

gemi = DeavaemGemiAPI()

# Durum sorgula
durum = await gemi.durum_sorgula()
print(f"Sıcaklık: {durum.sicaklik}°C")
print(f"GPU Kullanım: {durum.gpu_kullanim}%")
print(f"Su Akış: {durum.su_sogutma_akis} L/dk")

# LLM inference
result = await gemi.llm_inference_gonder(
    model="minimax",
    prompt="Merhaba MODULllm!"
)
```

---

## 🔗 Ecosystem Entegrasyonu

### B1Z KODLAB

```bash
# B1Z KODLAB'ı çalıştır
cd ../b1z-kodlab/frontend
npm install && npm run dev

# Backend
cd ../b1z-kodlab/backend
pip install -r requirements.txt
python main.py
```

**Erişim:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000 (B1Z KODLAB API)
- MODULllm Platform: http://localhost:8000 (Ana platform)

---

## 🧪 Test & Development

### Test Script

```bash
# Tüm sistemi test et
python test_platform.py
```

### Orchestrator Testi

```bash
# 11 Akıl + 12. Akıl test
python orchestration/oz_orchestrator.py
```

### Öz Veritabanı Testi

```bash
# Veritabanı test
python database/oz_database.py
```

### Gemi API Testi

```bash
# DEAVAEM Gemi test
python gemi/deavaem_api.py
```

---

## 📁 Proje Yapısı

```
modulllm-ozcode/
├── README.md              # Ana döküman
├── QUICKSTART.md          # Bu dosya
├── requirements.txt       # Python dependencies
├── docker-compose.yml     # Docker setup
├── Dockerfile
├── .env.example
│
├── core/
│   └── platform_api.py    # Ana FastAPI platform
│
├── orchestration/
│   └── oz_orchestrator.py # 11 Akıl + 12. Akıl
│
├── database/
│   └── oz_database.py     # Öz Veritabanı
│
├── gemi/
│   └── deavaem_api.py     # DEAVAEM Gemi API
│
└── ecosystem/
    └── (B1Z KODLAB, MAYA, vb.)
```

---

## 🎓 Örnek Kullanımlar

### Python ile Orchestrator Kullanımı

```python
from orchestration.oz_orchestrator import OzKodOrchestrator

orchestrator = OzKodOrchestrator()

# Soru sor
sonuc = await orchestrator.oz_koddan_yanitla(
    "MODULllm.com'un felsefesi nedir?"
)

# 11 Akıl yanıtları
for akil in sonuc["on_bir_akil"]:
    print(f"{akil['akil']}: {akil['icerik'][:100]}...")

# 12. Akıl sentezi
print(f"\nSentez:\n{sonuc['on_ikinci_akil_sentezi']['sentez']}")
```

### Öz Veritabanı Kullanımı

```python
from database.oz_database import OzVeritabani, IcerikTipi

db = OzVeritabani()

# İçerik ekle
db.ekle(
    tip=IcerikTipi.SORU_CEVAP,
    baslik="Python Async",
    icerik="Async/await ile asenkron programlama...",
    etiketler=["python", "async", "concurrency"],
    yaratici="kullanici"
)

# Ara
sonuclar = db.ara("python async", limit=5)
for sonuc in sonuclar:
    print(sonuc.icerik.baslik)
```

---

## 🚀 Production Deployment

### Docker (Önerilen)

```bash
docker-compose up -d --build
```

### Kubernetes (Gelişmiş)

```bash
# Helm chart
helm install modulllm ./helm/modulllm

# Veya kubectl
kubectl apply -f k8s/
```

### Environment Variables

Production'da mutlaka ayarla:
- `GEMI_ENDPOINT` - DEAVAEM Gemi URL
- `GEMI_API_KEY` - Gemi API key
- `REDIS_URL` - Redis connection
- `OZ_DB_PATH` - Database yolu

---

## 🔧 Troubleshooting

### Port zaten kullanımda

```bash
# Port kontrolü
lsof -i :8000

# Alternatif port kullan
uvicorn core.platform_api:app --port 8001
```

### Docker build hatası

```bash
# Cache temizle
docker-compose down
docker system prune -a
docker-compose up --build
```

### Gemi bağlantı hatası

```bash
# Gemi endpoint kontrolü
curl http://gemi.modulllm.com:8000/health

# .env'de doğru endpoint var mı kontrol et
```

---

## 💡 İpuçları

1. **Öz Veritabanı Zenginleşir:** Her soru-cevap, veritabanını büyütür
2. **11 Akıl Paralel:** Tüm akıllar paralel çalışır (hızlı!)
3. **Gemi Öncelikli:** Mümkünse gemideki LLM'leri kullan
4. **Cache Kullan:** Redis ile yanıtları cache'le
5. **Metrics İzle:** `/api/stats` ile sistemi takip et

---

## 📞 Destek

- **Docs:** http://localhost:8000/api/docs
- **GitHub:** https://github.com/serifkerem-CO/MiniMax-M2
- **Platform:** MODULllm.com

---

**🌌 MODULllm.com - Öz Kodundan Doğan Güç!**
**Built with 11111111111111111111 Energy** ⚡
