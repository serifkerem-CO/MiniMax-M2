# B1Z KODLAB - Deployment Guide 🚀

## Hızlı Başlangıç

### Gereksinimler

**Backend:**
- Python 3.9+
- pip

**Frontend:**
- Node.js 18+
- npm veya yarn

**Opsiyonel:**
- Docker & Docker Compose
- Rust compiler (kod çalıştırma için)
- Go compiler (kod çalıştırma için)

## 🐳 Docker ile Deployment (Önerilen)

### 1. Tüm Sistemi Çalıştır

```bash
# Repository klonla
git clone https://github.com/serifkerem/MiniMax-M2.git
cd MiniMax-M2/b1z-kodlab

# Docker Compose ile başlat
docker-compose up -d
```

### 2. Erişim

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/api/docs

## 💻 Manuel Kurulum

### Backend Setup

```bash
cd b1z-kodlab/backend

# Virtual environment oluştur
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment değişkenlerini ayarla
cp .env.example .env
# .env dosyasını düzenle ve MINIMAX_API_KEY'i ekle

# Sunucuyu başlat
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup

```bash
cd b1z-kodlab/frontend

# Bağımlılıkları yükle
npm install

# Development server başlat
npm run dev
```

## 🔑 Environment Configuration

### Backend (.env)

```env
# MiniMax-M2 API
MINIMAX_API_KEY=your_api_key_here
MINIMAX_API_BASE=https://api.minimax.chat/v1
MINIMAX_MODEL=MiniMax-M2

# Server
HOST=0.0.0.0
PORT=8000
RELOAD=true

# B1Z Configuration
PARALLEL_AI_COUNT=11
DAILY_CHALLENGE_POINTS=111
MASTERY_POINTS=1111
```

### MiniMax-M2 API Key Alma

1. https://platform.minimax.io adresine git
2. Kayıt ol / Giriş yap
3. API Keys bölümünden yeni key oluştur
4. `.env` dosyasına ekle

## 🚢 Production Deployment

### Backend (FastAPI)

```bash
# Gunicorn ile production server
pip install gunicorn

gunicorn main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

### Frontend (React)

```bash
# Production build
npm run build

# Serve static files
npm install -g serve
serve -s dist -p 3000
```

### Nginx Reverse Proxy

```nginx
server {
    listen 80;
    server_name modulllm.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

## 🐳 Docker Compose (Tam Sistem)

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - MINIMAX_API_KEY=${MINIMAX_API_KEY}
      - MINIMAX_API_BASE=https://api.minimax.chat/v1
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./backend:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    command: npm run dev -- --host 0.0.0.0

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - backend
      - frontend
```

## 🔒 Security Checklist

- [ ] API keys'leri environment variables'da sakla
- [ ] HTTPS kullan (production)
- [ ] CORS ayarlarını kontrol et
- [ ] Rate limiting ekle
- [ ] Input validation yap
- [ ] SQL injection koruması (eğer DB kullanılıyorsa)
- [ ] XSS koruması

## 📊 Monitoring

### Health Check Endpoints

- Backend: `GET http://localhost:8000/health`
- Execution runtimes: `GET http://localhost:8000/execute/health`

### Logs

```bash
# Backend logs
tail -f backend/logs/app.log

# Frontend logs (development)
npm run dev

# Docker logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

## 🚀 MODULLLM.COM Deployment

### Vercel (Frontend)

```bash
# Vercel CLI ile deploy
npm i -g vercel
cd frontend
vercel --prod
```

### Railway/Render (Backend)

1. Repository'yi bağla
2. Root directory: `b1z-kodlab/backend`
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Environment variables ekle

## 🔧 Troubleshooting

### Backend Başlamıyor

```bash
# Port kullanımda mı kontrol et
lsof -i :8000

# Python version kontrol
python3 --version  # 3.9+ olmalı
```

### Frontend Build Hatası

```bash
# Node modules temizle
rm -rf node_modules package-lock.json
npm install

# Cache temizle
npm cache clean --force
```

### MiniMax API Hatası

- API key'in doğru olduğundan emin ol
- Rate limit kontrolü yap
- Network bağlantısını kontrol et

## 📞 Destek

Sorun yaşıyorsan:
1. GitHub Issues: https://github.com/serifkerem/MiniMax-M2/issues
2. AI'ya sor: MiniMax-M2 platformunda
3. Email: kod@modulllm.com

---

**B1Z KODLAB** - Built with 11111111111111111111 Energy ⚡
