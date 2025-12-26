FROM python:3.11-slim

WORKDIR /app

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY main.py .

# Port
EXPOSE 8080

# Ortam değişkenleri
ENV MINIMAX_API_BASE="http://localhost:8000/v1"
ENV MINIMAX_API_KEY=""
ENV MINIMAX_MODEL="MiniMax-M2"
ENV RATE_LIMIT="60"

# Başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
