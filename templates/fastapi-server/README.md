# MiniMax-M2 FastAPI Sunucu Şablonu

Production-ready REST API sunucusu MiniMax-M2 için.

## Hızlı Başlangıç

1. Bağımlılıkları yükle:
```bash
pip install -r requirements.txt
```

2. Ortam değişkenlerini ayarla:
```bash
export MINIMAX_API_BASE="http://localhost:8000/v1"
export MINIMAX_API_KEY="your-api-key"
export MINIMAX_MODEL="MiniMax-M2"
export RATE_LIMIT="60"
```

3. Sunucuyu başlat:
```bash
uvicorn main:app --reload --port 8080
```

4. API dokümantasyonunu görüntüle:
```
http://localhost:8080/docs
```

## Özellikler

- **OpenAI Uyumlu**: Standart chat completions API
- **Streaming**: Server-Sent Events ile streaming yanıtlar
- **Rate Limiting**: IP bazlı istek sınırlandırma
- **CORS**: Cross-origin istekler için destek
- **Sağlık Kontrolü**: Uptime ve durum izleme
- **Kod Analizi**: Özel kod analiz endpoint'i
- **Kod Üretimi**: Kod oluşturma endpoint'i

## API Endpoints

| Endpoint | Method | Açıklama |
|----------|--------|----------|
| `/` | GET | Ana sayfa |
| `/health` | GET | Sağlık kontrolü |
| `/docs` | GET | Swagger UI |
| `/v1/chat/completions` | POST | Sohbet tamamlama |
| `/v1/completions` | POST | Metin tamamlama |
| `/v1/code/analyze` | POST | Kod analizi |
| `/v1/code/generate` | POST | Kod üretimi |

## Kullanım Örnekleri

### Sohbet Tamamlama
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Merhaba!"}
    ],
    "temperature": 0.7,
    "max_tokens": 1024
  }'
```

### Streaming
```bash
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "content": "Python nedir?"}
    ],
    "stream": true
  }'
```

### Kod Analizi
```bash
curl -X POST "http://localhost:8080/v1/code/analyze?language=python" \
  -H "Content-Type: application/json" \
  -d '"def hello(): print(\"world\")"'
```

### Python Client
```python
import requests

response = requests.post(
    "http://localhost:8080/v1/chat/completions",
    json={
        "messages": [{"role": "user", "content": "Merhaba!"}],
        "temperature": 0.7
    }
)
print(response.json()["content"])
```

## Docker ile Çalıştırma

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY main.py .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
```

```bash
docker build -t minimax-api .
docker run -p 8080:8080 -e MINIMAX_API_KEY=xxx minimax-api
```

## Production Önerileri

1. **CORS**: `allow_origins` listesini production domainleri ile kısıtlayın
2. **Rate Limiting**: Redis tabanlı distributed rate limiter kullanın
3. **Logging**: Structured logging ekleyin
4. **Metrics**: Prometheus metrics endpoint'i ekleyin
5. **Authentication**: API key veya JWT authentication ekleyin
