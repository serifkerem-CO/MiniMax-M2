"""
MiniMax-M2 FastAPI Sunucu Şablonu
=================================
MiniMax-M2 için production-ready REST API sunucusu.

Özellikler:
- OpenAI uyumlu API endpoints
- Streaming ve non-streaming yanıtlar
- Rate limiting
- Sağlık kontrolü
- CORS desteği

Gereksinimler:
    pip install fastapi uvicorn openai python-multipart

Kullanım:
    uvicorn main:app --reload --port 8080
"""

import os
import time
import asyncio
from typing import Optional, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from openai import OpenAI

# Yapılandırma
API_BASE_URL = os.getenv("MINIMAX_API_BASE", "http://localhost:8000/v1")
API_KEY = os.getenv("MINIMAX_API_KEY", "your-api-key-here")
MODEL_NAME = os.getenv("MINIMAX_MODEL", "MiniMax-M2")
MAX_REQUESTS_PER_MINUTE = int(os.getenv("RATE_LIMIT", "60"))


# ============================================================================
# Pydantic Modeller
# ============================================================================

class Message(BaseModel):
    """Sohbet mesajı."""
    role: str = Field(..., description="Rol: system, user, assistant")
    content: str = Field(..., description="Mesaj içeriği")


class ChatRequest(BaseModel):
    """Sohbet isteği."""
    messages: list[Message] = Field(..., description="Mesaj listesi")
    temperature: float = Field(0.7, ge=0, le=2, description="Sıcaklık parametresi")
    max_tokens: int = Field(2048, ge=1, le=8192, description="Maksimum token sayısı")
    stream: bool = Field(False, description="Streaming yanıt")
    system_prompt: Optional[str] = Field(None, description="Özel sistem promptu")


class CompletionRequest(BaseModel):
    """Tamamlama isteği."""
    prompt: str = Field(..., description="Tamamlanacak metin")
    temperature: float = Field(0.7, ge=0, le=2)
    max_tokens: int = Field(2048, ge=1, le=8192)
    stream: bool = Field(False)


class ChatResponse(BaseModel):
    """Sohbet yanıtı."""
    id: str
    content: str
    model: str
    usage: dict
    created_at: str


class HealthResponse(BaseModel):
    """Sağlık kontrolü yanıtı."""
    status: str
    model: str
    timestamp: str
    uptime_seconds: float


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """Basit rate limiter."""

    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.requests: dict[str, list[float]] = {}

    def is_allowed(self, client_id: str) -> bool:
        """İsteğin izin verilip verilmediğini kontrol et."""
        now = time.time()
        minute_ago = now - 60

        if client_id not in self.requests:
            self.requests[client_id] = []

        # Eski istekleri temizle
        self.requests[client_id] = [
            t for t in self.requests[client_id] if t > minute_ago
        ]

        if len(self.requests[client_id]) >= self.requests_per_minute:
            return False

        self.requests[client_id].append(now)
        return True


# ============================================================================
# Uygulama
# ============================================================================

# Global değişkenler
client: Optional[OpenAI] = None
rate_limiter: Optional[RateLimiter] = None
start_time: float = 0


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama yaşam döngüsü."""
    global client, rate_limiter, start_time

    # Başlangıç
    print("🚀 MiniMax-M2 API Sunucusu başlatılıyor...")
    client = OpenAI(api_key=API_KEY, base_url=API_BASE_URL)
    rate_limiter = RateLimiter(MAX_REQUESTS_PER_MINUTE)
    start_time = time.time()
    print(f"✅ Bağlantı kuruldu: {API_BASE_URL}")
    print(f"📊 Rate limit: {MAX_REQUESTS_PER_MINUTE} istek/dakika")

    yield

    # Kapanış
    print("👋 Sunucu kapatılıyor...")


app = FastAPI(
    title="MiniMax-M2 API",
    description="MiniMax-M2 için REST API sunucusu",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtlayın
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# Dependency'ler
# ============================================================================

async def check_rate_limit(request: Request):
    """Rate limit kontrolü."""
    client_ip = request.client.host
    if not rate_limiter.is_allowed(client_ip):
        raise HTTPException(
            status_code=429,
            detail="Rate limit aşıldı. Lütfen bir dakika bekleyin."
        )


# ============================================================================
# Endpoints
# ============================================================================

@app.get("/", response_model=dict)
async def root():
    """Ana sayfa."""
    return {
        "service": "MiniMax-M2 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Sağlık kontrolü."""
    uptime = time.time() - start_time

    return HealthResponse(
        status="healthy",
        model=MODEL_NAME,
        timestamp=datetime.now().isoformat(),
        uptime_seconds=uptime
    )


@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completions(
    request: ChatRequest,
    _: None = Depends(check_rate_limit)
):
    """
    Sohbet tamamlama endpoint'i.

    OpenAI API ile uyumlu.
    """
    try:
        # Mesajları hazırla
        messages = []

        # Sistem promptu ekle
        if request.system_prompt:
            messages.append({"role": "system", "content": request.system_prompt})

        # Kullanıcı mesajlarını ekle
        for msg in request.messages:
            messages.append({"role": msg.role, "content": msg.content})

        # Streaming yanıt
        if request.stream:
            return StreamingResponse(
                stream_chat_response(messages, request.temperature, request.max_tokens),
                media_type="text/event-stream"
            )

        # Normal yanıt
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return ChatResponse(
            id=response.id,
            content=response.choices[0].message.content,
            model=MODEL_NAME,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            created_at=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def stream_chat_response(
    messages: list[dict],
    temperature: float,
    max_tokens: int
) -> AsyncGenerator[str, None]:
    """Streaming yanıt üreteci."""
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                yield f"data: {content}\n\n"

        yield "data: [DONE]\n\n"

    except Exception as e:
        yield f"data: [ERROR] {str(e)}\n\n"


@app.post("/v1/completions")
async def completions(
    request: CompletionRequest,
    _: None = Depends(check_rate_limit)
):
    """
    Metin tamamlama endpoint'i.
    """
    try:
        messages = [{"role": "user", "content": request.prompt}]

        if request.stream:
            return StreamingResponse(
                stream_chat_response(messages, request.temperature, request.max_tokens),
                media_type="text/event-stream"
            )

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
        )

        return {
            "id": response.id,
            "text": response.choices[0].message.content,
            "model": MODEL_NAME,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/code/analyze")
async def analyze_code(
    code: str,
    language: str = "python",
    _: None = Depends(check_rate_limit)
):
    """
    Kod analizi endpoint'i.
    """
    try:
        prompt = f"""Aşağıdaki {language} kodunu analiz et:

```{language}
{code}
```

Analiz:
1. Kodun ne yaptığını açıkla
2. Olası sorunları belirt
3. İyileştirme önerileri sun
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": "Sen uzman bir kod analistisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        return {
            "analysis": response.choices[0].message.content,
            "language": language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/code/generate")
async def generate_code(
    description: str,
    language: str = "python",
    _: None = Depends(check_rate_limit)
):
    """
    Kod üretimi endpoint'i.
    """
    try:
        prompt = f"""Aşağıdaki açıklamaya göre {language} kodu yaz:

{description}

Gereksinimler:
- Temiz ve okunabilir kod
- Uygun hata yönetimi
- Yorumlar ekle
"""

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": f"Sen uzman bir {language} geliştiricisisin."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=2048,
        )

        return {
            "code": response.choices[0].message.content,
            "language": language
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Hata İşleyiciler
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP hata işleyici."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Genel hata işleyici."""
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "message": "Sunucu hatası oluştu",
            "detail": str(exc)
        }
    )


# ============================================================================
# Ana Giriş
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
        log_level="info"
    )
