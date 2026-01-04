# 🚀 12. İnci Modeli - Hızlı Başlangıç Kılavuzu

**modulLLM.com için Real-time Emotion AI**

## ⚡ 5 Dakikada Çalıştır

### 1️⃣ Gereksinimler

```bash
# Python 3.9+ kontrolü
python --version

# MiniMax API Key
# https://platform.minimax.io/ adresinden ücretsiz key alın
```

### 2️⃣ Kurulum

```bash
# Repository'yi klonlayın veya klasöre girin
cd 12-inci-modeli

# API bağımlılıklarını yükleyin
cd api
pip install -r requirements.txt
```

### 3️⃣ Yapılandırma

```bash
# .env dosyası oluşturun
cp .env.example .env

# .env dosyasını düzenleyin ve API key'inizi ekleyin
nano .env
```

**.env dosyasına ekleyin:**
```env
MINIMAX_API_KEY=your_actual_api_key_here
MINIMAX_GROUP_ID=your_group_id_here
```

### 4️⃣ Başlatın

**Terminal 1 - API Server:**
```bash
cd api
python main.py
```

API şu adreste çalışacak: http://localhost:8000

**Terminal 2 - Frontend:**
```bash
cd frontend
python -m http.server 3000
```

Frontend şu adreste: http://localhost:3000

### 5️⃣ Test Edin

Tarayıcınızda http://localhost:3000 adresini açın ve mesaj gönderin:

```
"Bugün çok mutluyum!"
"Biraz üzgünüm ve kaygılıyım"
"Bu harika bir haber, çok heyecanlıyım!"
```

---

## 🐳 Docker ile Çalıştırma (Önerilen)

```bash
# .env dosyasını oluşturun
cp api/.env.example api/.env

# API key'inizi ekleyin
nano api/.env

# Docker Compose ile başlatın
docker-compose up -d

# Logları izleyin
docker-compose logs -f api
```

**Erişim:**
- Frontend: http://localhost:3000
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Durdurma:**
```bash
docker-compose down
```

---

## 📡 API Kullanımı

### REST API

```bash
# Emotion analizi
curl -X POST http://localhost:8000/api/v1/emotion/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "Bugün harika bir gün!", "language": "tr"}'

# Yanıt:
{
  "emotions": [
    {
      "type": "joy",
      "confidence": 0.92,
      "label": "Mutluluk",
      "emoji": "😊"
    }
  ],
  "primary_emotion": "joy",
  "response_suggestion": "Ne güzel! Bu pozitif enerjinizi paylaştığınız için teşekkürler!",
  "timestamp": "2026-01-04T19:30:00Z"
}
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/emotion/realtime');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'message',
    text: 'Merhaba!'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('AI Response:', data.ai_response);
  console.log('Emotions:', data.emotions);
};
```

---

## 🎨 12 İnci Duygu Kategorileri

| # | Emoji | Duygu | İngilizce | Örnek |
|---|-------|-------|-----------|-------|
| 1 | 😊 | Mutluluk | Joy | "Çok sevindim!" |
| 2 | 😢 | Üzüntü | Sadness | "Üzgünüm" |
| 3 | 😠 | Öfke | Anger | "Çok sinirliyim" |
| 4 | 😨 | Korku | Fear | "Endişeliyim" |
| 5 | 🤢 | Tiksinme | Disgust | "İğrenç" |
| 6 | 😲 | Şaşkınlık | Surprise | "İnanamıyorum!" |
| 7 | ❤️ | Sevgi | Love | "Seni seviyorum" |
| 8 | 🤔 | Merak | Curiosity | "Acaba nasıl?" |
| 9 | 😌 | Huzur | Peace | "Çok rahatım" |
| 10 | 💪 | Güven | Confidence | "Başarabilirim!" |
| 11 | 😔 | Pişmanlık | Regret | "Keşke yapmasa" |
| 12 | 🎉 | Heyecan | Excitement | "Muhteşem!" |

---

## 🔧 Sorun Giderme

### API bağlantı hatası?

1. API sunucusunun çalıştığını kontrol edin: http://localhost:8000/health
2. .env dosyasında API key'in doğru olduğundan emin olun
3. Firewall/antivirus 8000 portunu engelliyor olabilir

### WebSocket bağlanamıyor?

Frontend'deki `app.js` dosyasında WebSocket URL'ini kontrol edin:
```javascript
const wsUrl = 'ws://localhost:8000/ws/emotion/realtime';
```

### MiniMax API hatası?

- API key'in aktif olduğundan emin olun
- Rate limit kontrolü: https://platform.minimax.io/
- API logs: `docker-compose logs api`

---

## 📊 Performans İpuçları

### Production için:

1. **Gunicorn/Uvicorn workers:** 4-8 worker
2. **Redis caching:** Aktif edin
3. **Rate limiting:** Endpoint başına limit ekleyin
4. **CORS:** Sadece güvenli origin'lere izin verin
5. **HTTPS:** Production'da SSL kullanın

### .env Production ayarları:

```env
DEBUG=False
ALLOWED_ORIGINS=https://modulllm.com,https://www.modulllm.com
LOG_LEVEL=WARNING
```

---

## 🌐 modulLLM.com Deployment

### Vercel/Netlify (Frontend)

```bash
# Build
cd frontend
# Static files hazır

# Deploy
vercel deploy
# veya
netlify deploy
```

### Heroku/Railway (Backend)

```bash
# Procfile oluştur
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

### Kubernetes (Scalable)

```bash
# k8s manifests'ı docs/ klasöründe bulabilirsiniz
kubectl apply -f k8s/
```

---

## 🆘 Destek

- **Dokümantasyon:** README.md
- **API Docs:** http://localhost:8000/docs
- **GitHub Issues:** [Link]
- **Email:** support@modulllm.com
- **Discord:** [Community]

---

## 🎉 Başarılı!

Şimdi modulLLM.com üzerinde gerçek zamanlı duygu tespiti yapan bir AI sisteminiz var! 🚀

**Sonraki adımlar:**
- [ ] Kendi custom emotion keyword'lerinizi ekleyin
- [ ] Frontend tasarımını özelleştirin
- [ ] Emotion analytics dashboard ekleyin
- [ ] Multi-user desteği geliştirin
- [ ] Voice input entegrasyonu

**Powered by MiniMax-M2 💎**
