# MiniMax-M2 API Dokümantasyon Üretici Şablonu

AI destekli otomatik API dokümantasyon üretimi.

## Özellikler

- **Kod Analizi**: FastAPI/Flask endpoint tespiti
- **OpenAPI Üretimi**: Swagger uyumlu spec
- **Markdown Docs**: Okunabilir dokümantasyon
- **Örnek Kod**: Python, JavaScript, cURL örnekleri

## Kurulum

```bash
pip install -r requirements.txt
```

## Kullanım

```bash
# OpenAPI + Markdown üret
python main.py generate app.py

# Sadece OpenAPI
python main.py generate app.py --format openapi

# Sadece Markdown
python main.py generate app.py --format markdown

# Özel başlık
python main.py generate app.py --title "My API"

# Örnek kod üret
python main.py examples app.py

# Belirli endpoint için örnek
python main.py examples app.py --endpoint /users

# Demo
python main.py demo
```

## Çıktı Formatları

### OpenAPI 3.0

```yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Kullanıcı listesi
      parameters:
        - name: limit
          in: query
          schema:
            type: integer
```

### Markdown

```markdown
## GET /users

Kullanıcı listesini getir.

**Parametreler:**
| İsim | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| limit | integer | ❌ | Sayfa limiti |
```

## Örnek Kod Çıktısı

```python
# Python
import requests
response = requests.get("http://api.example.com/users", params={"limit": 10})
```

```javascript
// JavaScript
const response = await fetch("http://api.example.com/users?limit=10");
```

```bash
# cURL
curl -X GET "http://api.example.com/users?limit=10"
```
