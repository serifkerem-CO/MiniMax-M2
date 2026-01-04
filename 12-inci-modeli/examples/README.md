# 💎 12. İnci Modeli - Demo Örnekleri

Bu klasör, 12. İnci Modeli'nin farklı kullanım senaryolarını gösteren demo uygulamaları içerir.

## 📋 Demo Listesi

### 1. REST API Demo (`demo_client.py`)

Temel REST API kullanımını gösteren interaktif demo.

**Özellikler:**
- ✅ Temel duygu analizi
- ✅ 12 duygu kategorisi listesi
- ✅ İnteraktif mod

**Kullanım:**
```bash
# API sunucusunun çalıştığından emin olun
cd ../api
python main.py

# Demo'yu çalıştırın (yeni terminal)
cd ../examples
python demo_client.py
```

**Örnek Çıktı:**
```
╔═══════════════════════════════════════════════════════════╗
║           💎 12. İnci Modeli - Demo Client 💎             ║
╚═══════════════════════════════════════════════════════════╝

📋 Demo Seçenekleri:

  1. Temel Duygu Analizi
  2. 12 Duygu Kategorileri
  3. İnteraktif Mod
  q. Çıkış

Seçiminiz: 1

============================================================
📝 Metin: Bugün harika bir gün geçirdim, çok mutluyum!
============================================================

🎯 Tespit Edilen Duygular:
  1. 😊 Mutluluk - 92% güven
  2. 🎉 Heyecan - 78% güven

💎 Birincil Duygu: joy

🤖 AI Yanıtı:
  Ne güzel! Mutluluğunuzu paylaştığınız için teşekkürler! 😊
```

---

### 2. WebSocket Demo (`websocket_demo.py`)

Real-time WebSocket bağlantısı ile canlı emotion chat.

**Özellikler:**
- ⚡ Real-time iletişim
- 💬 Anlık duygu tespiti
- 🤖 AI yanıtları

**Kullanım:**
```bash
# Gerekli kütüphaneyi yükleyin
pip install websockets

# Demo'yu çalıştırın
python websocket_demo.py
```

**Örnek Oturum:**
```
╔═══════════════════════════════════════════════════════════╗
║      💎 12. İnci Modeli - Real-time WebSocket Chat 💎     ║
╚═══════════════════════════════════════════════════════════╝

✅ 12. İnci Modeli'ne bağlandınız! 💎

Mesajınızı yazın (çıkmak için 'q'):

➤ Siz: Bugün harika bir gün!

[😊 Mutluluk 🎉 Heyecan]
🤖 AI: Ne güzel! Bu pozitif enerjinizi hissetmek harika!

➤ Siz: q

👋 Görüşürüz!
```

---

### 3. JavaScript/Browser Demo (`demo.html`)

Tarayıcı tabanlı WebSocket demo'su.

**Kullanım:**
```bash
# Frontend'i başlatın
cd ../frontend
python -m http.server 3000

# Tarayıcıda açın
open http://localhost:3000
```

---

### 4. cURL Örnekleri (`curl_examples.sh`)

Terminal'den hızlı API testleri.

**Kullanım:**
```bash
bash curl_examples.sh
```

**Örnekler:**

```bash
# Emotion analizi
curl -X POST http://localhost:8000/api/v1/emotion/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Çok mutluyum!", "language": "tr"}'

# Duygu listesi
curl http://localhost:8000/api/v1/emotions/list

# Health check
curl http://localhost:8000/health
```

---

## 🎯 Test Senaryoları

### Mutluluk Tespiti
```python
text = "Bugün harika bir gün geçirdim, çok mutluyum!"
# Beklenen: joy (Mutluluk)
```

### Üzüntü Tespiti
```python
text = "Çok üzgünüm, bugün kötü bir gün"
# Beklenen: sadness (Üzüntü)
```

### Öfke Tespiti
```python
text = "Bu duruma çok sinirlendim, yeter artık!"
# Beklenen: anger (Öfke)
```

### Çoklu Duygu
```python
text = "Hem mutluyum hem de biraz endişeliyim"
# Beklenen: joy + fear
```

---

## 📊 Performance Testing

### Locust Load Test

```bash
# Yükle
pip install locust

# Çalıştır
locust -f performance_test.py --host=http://localhost:8000
```

---

## 🐳 Docker Demo

```bash
# Docker Compose ile başlat
docker-compose up -d

# Demo'yu çalıştır
python demo_client.py
```

---

## 🔧 Troubleshooting

### API bağlantı hatası?

```bash
# API durumunu kontrol et
curl http://localhost:8000/health

# Çıktı olmalı:
{"status":"healthy","timestamp":"..."}
```

### WebSocket bağlanamıyor?

1. API sunucusunun çalıştığını kontrol edin
2. Port 8000'in açık olduğunu kontrol edin
3. Firewall ayarlarını kontrol edin

---

## 📚 Daha Fazla Bilgi

- **API Dokümantasyonu:** http://localhost:8000/docs
- **Ana README:** ../README.md
- **Quick Start:** ../QUICKSTART.md

---

**💎 Powered by MiniMax-M2 | modulLLM.com**
