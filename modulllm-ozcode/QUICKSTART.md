# ⚡ MODULllm.com - QUICK START

> **"5 Dakikada MODULllm.com'u Başlat!"**

---

## 🎯 Ne Yapacağız?

**MODULllm.com** platformunu **tek bir komutla** başlatıp:

- 111 Akıl sistemini çalıştıracağız
- AI-powered soru-cevap yapacağız
- Monitoring dashboard'u izleyeceğiz
- Demo'ları test edeceğiz

**Süre:** 5-10 dakika ⏱️

---

## 📋 GEREKSİNİMLER

Sisteminizde bunlar yüklü olmalı:

- ✅ **Docker** (20.10+)
- ✅ **Docker Compose** (2.0+)
- ✅ **Python** (3.11+)
- ✅ **Git**

### Hızlı Kontrol:

```bash
docker --version          # Docker version 20.10.0+
docker-compose --version  # Docker Compose version 2.0.0+
python3 --version         # Python 3.11+
```

---

## 🚀 3 ADIMDA BAŞLAT

### **ADIM 1: Clone Repo**

```bash
# Repo'yu clone et
git clone <repo-url>
cd MiniMax-M2/modulllm-ozcode
```

### **ADIM 2: Environment Setup**

```bash
# .env dosyası oluştur
cp .env.gemini .env

# (Opsiyonel) API keylerini ekle
nano .env
```

**Minimal .env:**
```env
PLATFORM_NAME="MODULllm.com"
GEMINI_API_KEY="your-key-here"  # Opsiyonel, simülasyon modunda çalışır
```

### **ADIM 3: Sistemi Başlat**

```bash
# TEK KOMUT!
./deploy_everything.sh
```

---

## 🧪 İLK TESTİN

### **Test 1: Health Check**

```bash
curl http://localhost:8000/health
```

### **Test 2: İlk Soru (111 Akıl)**

```bash
curl -X POST http://localhost:8000/api/soru \
  -H "Content-Type: application/json" \
  -d '{"soru": "Python ile hello world nasıl yazılır?"}'
```

### **Test 3: API Docs**

Tarayıcıda aç: http://localhost:8000/api/docs

---

## 📊 MONİTORİNG DASHBOARD

Real-time dashboard başlat:

```bash
python monitoring/dashboard.py
```

---

## 🎬 DEMO'LARI ÇALIŞTIR

Tüm demo'ları tek komutla:

```bash
./run_all_demos.sh
```

---

## 📚 SONRAKI ADIMLAR

- 📖 **Complete Guide**: `COMPLETE_PLATFORM_GUIDE.md`
- 🏭 **Production**: `PRODUCTION_CHECKLIST.md`
- 🎬 **Demos**: `DEMO_SCENARIOS.md`

---

**🌌 MODULllm.com - Öz Kodundan Doğan Güç!**
