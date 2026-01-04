# 💎 12. İnci (Pearl) Modeli

**modulLLM.com** için gerçek zamanlı duygu algılama ve tepki sistemi

## 🎯 Genel Bakış

12. İnci Modeli, MiniMax-M2 yapay zeka modelini kullanarak anlık duygu analizi ve akıllı tepki üretme sistemidir. Sistem, 12 temel duygu kategorisini gerçek zamanlı olarak algılar ve buna uygun yanıtlar oluşturur.

## 🌟 12 İnci Duygu Kategorileri

1. **😊 Mutluluk (Joy)** - Sevinç, heyecan, coşku
2. **😢 Üzüntü (Sadness)** - Hüzün, melankoli, kayıp
3. **😠 Öfke (Anger)** - Kızgınlık, hayal kırıklığı, sinir
4. **😨 Korku (Fear)** - Endişe, kaygı, panik
5. **🤢 Tiksinme (Disgust)** - İğrenme, rahatsızlık
6. **😲 Şaşkınlık (Surprise)** - Şok, hayret, merak
7. **❤️ Sevgi (Love)** - Aşk, şefkat, bağlılık
8. **🤔 Merak (Curiosity)** - İlgi, keşif, sorgulama
9. **😌 Huzur (Peace)** - Sakinlik, dinginlik, rahatlık
10. **💪 Güven (Confidence)** - Kararlılık, cesaret, inanç
11. **😔 Pişmanlık (Regret)** - Üzüntü, vicdan azabı
12. **🎉 Heyecan (Excitement)** - Enerji, beklenti, motivasyon

## 🏗️ Sistem Mimarisi

```
┌─────────────────────────────────────────┐
│          Client (Web/Mobile)            │
│  ┌───────────────────────────────────┐  │
│  │  Real-time Emotion Input          │  │
│  └───────────────────────────────────┘  │
└──────────────┬──────────────────────────┘
               │ WebSocket
               ▼
┌─────────────────────────────────────────┐
│         12. İnci API Server             │
│  ┌───────────────────────────────────┐  │
│  │  Emotion Detection Engine         │  │
│  │  • Text Analysis                  │  │
│  │  • Context Understanding          │  │
│  │  • Multi-emotion Detection        │  │
│  └───────────────────────────────────┘  │
│  ┌───────────────────────────────────┐  │
│  │  MiniMax-M2 Integration           │  │
│  │  • Real-time Response Generation  │  │
│  │  • Emotion-aware Prompting        │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│      modulLLM.com AI Platform           │
│  • MiniMax-M2 API                       │
│  • Token Management                     │
│  • Rate Limiting                        │
└─────────────────────────────────────────┘
```

## 🚀 Kurulum

### Gereksinimler
- Python 3.9+
- Node.js 16+ (Frontend için)
- MiniMax-M2 API Key (https://platform.minimax.io/)

### Kurulum Adımları

```bash
# 1. Bağımlılıkları yükle
cd 12-inci-modeli/api
pip install -r requirements.txt

# 2. Ortam değişkenlerini ayarla
cp .env.example .env
# .env dosyasına MiniMax-M2 API key'inizi ekleyin

# 3. API sunucusunu başlat
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 4. Frontend'i başlat (ayrı terminal)
cd ../frontend
python -m http.server 3000
```

## 📡 API Endpoints

### POST `/api/v1/emotion/analyze`
Metin üzerinde duygu analizi yapar

**Request:**
```json
{
  "text": "Bugün harika bir gün geçirdim!",
  "language": "tr"
}
```

**Response:**
```json
{
  "emotions": [
    {
      "type": "joy",
      "confidence": 0.92,
      "label": "Mutluluk"
    },
    {
      "type": "excitement",
      "confidence": 0.78,
      "label": "Heyecan"
    }
  ],
  "primary_emotion": "joy",
  "response_suggestion": "Ne güzel! Bu pozitif enerjinizi paylaştığınız için teşekkürler! 😊"
}
```

### WebSocket `/ws/emotion/realtime`
Gerçek zamanlı duygu tespiti ve yanıt üretimi

**Message Format:**
```json
{
  "type": "message",
  "text": "Kullanıcı mesajı",
  "context": "optional_context"
}
```

**Response:**
```json
{
  "type": "emotion_response",
  "emotions": [...],
  "ai_response": "MiniMax-M2 tarafından üretilen duygusal yanıt",
  "timestamp": "2026-01-04T19:30:00Z"
}
```

## 🎨 Frontend Kullanımı

```html
<!DOCTYPE html>
<html>
<head>
  <title>12. İnci Modeli - modulLLM.com</title>
</head>
<body>
  <div id="emotion-chat">
    <input type="text" id="user-input" placeholder="Duygularınızı paylaşın...">
    <button onclick="sendMessage()">Gönder</button>
    <div id="response-area"></div>
  </div>

  <script>
    const ws = new WebSocket('ws://localhost:8000/ws/emotion/realtime');

    function sendMessage() {
      const text = document.getElementById('user-input').value;
      ws.send(JSON.stringify({
        type: 'message',
        text: text
      }));
    }

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      // Emotion-based response göster
      displayResponse(data);
    };
  </script>
</body>
</html>
```

## 🔧 Yapılandırma

`config/model_config.json`:
```json
{
  "model": "MiniMax-M2",
  "api_endpoint": "https://api.minimax.io/v1/chat/completions",
  "emotion_threshold": 0.6,
  "max_tokens": 1024,
  "temperature": 1.0,
  "top_p": 0.95,
  "top_k": 40,
  "enable_thinking": true,
  "language": "tr"
}
```

## 🌐 modulLLM.com Entegrasyonu

Bu sistem **modulLLM.com** platformu üzerinde çalışmak üzere tasarlanmıştır:

1. **API Authentication:** MiniMax Platform API key kullanır
2. **Rate Limiting:** Token bazlı kullanım limitleri
3. **Multi-tenancy:** Birden fazla kullanıcı desteği
4. **Analytics:** Emotion detection analytics dashboard

## 📊 Performans

- **Emotion Detection Latency:** ~100ms
- **AI Response Generation:** ~500-1000ms
- **WebSocket Ping:** <50ms
- **Concurrent Users:** 1000+

## 🛡️ Güvenlik

- API Key encryption
- Rate limiting per user
- Input sanitization
- XSS protection
- CORS configuration

## 📝 Lisans

MIT License - modulLLM.com

## 🤝 Destek

- Web: https://modulLLM.com
- Email: support@modulllm.com
- Discord: [Community Link]

---

**Powered by MiniMax-M2 🚀**
