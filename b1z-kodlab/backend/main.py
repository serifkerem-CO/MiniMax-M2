"""
B1Z KODLAB - Main FastAPI Application
"Kodla, Kodlat, B1Z Ol" 🚀

Powered by MiniMax-M2
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .config import settings
from .routers import ai_feedback, code_execution, lessons

# Create B1Z KODLAB app
app = FastAPI(
    title=settings.PLATFORM_NAME,
    description="Kodlama öğrenen ve öğretenlerin AI destekli platformu",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ai_feedback.router)
app.include_router(code_execution.router)
app.include_router(lessons.router)


@app.get("/")
async def root():
    """B1Z KODLAB API Root"""
    return {
        "platform": settings.PLATFORM_NAME,
        "slogan": "Kodla, Kodlat, B1Z Ol",
        "powered_by": "MiniMax-M2",
        "version": "1.0.0",
        "features": {
            "kodla": "Canlı kod editörü ve AI feedback",
            "kodlat": "AI öğretmeni ile adım adım öğrenim",
            "b1z": "Topluluk ve işbirliği"
        },
        "stats": {
            "total_lessons": 11,
            "points_system": "111 / 1111",
            "ai_perspectives": settings.PARALLEL_AI_COUNT
        },
        "endpoints": {
            "docs": "/api/docs",
            "lessons": "/lessons",
            "ai_analyze": "/ai/analyze",
            "execute_code": "/execute/run"
        }
    }


@app.get("/health")
async def health_check():
    """Platform health check"""
    return {
        "status": "healthy",
        "platform": settings.PLATFORM_NAME,
        "model": settings.MINIMAX_MODEL,
        "features": ["kodla", "kodlat", "b1z"],
        "theme": "11111111111111111111 Energy ⚡"
    }


@app.get("/stats")
async def platform_stats():
    """B1Z KODLAB statistics"""
    return {
        "total_lessons": 11,
        "total_points_available": sum([111] * 10 + [1111]),  # 10 lessons x 111 + final lesson 1111
        "supported_languages": ["Python", "JavaScript", "TypeScript", "Rust", "Go", "C++"],
        "ai_perspectives": settings.PARALLEL_AI_COUNT,
        "daily_challenge_points": settings.DAILY_CHALLENGE_POINTS,
        "mastery_points": settings.MASTERY_POINTS
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "platform": settings.PLATFORM_NAME
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD
    )
