"""
12. İnci (Pearl) Modeli - Main API Server
modulLLM.com - Real-time Emotion AI
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import json
import os
from datetime import datetime
import logging

from emotion_detector import EmotionDetector
from minimax_client import MiniMaxClient

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="12. İnci Modeli API",
    description="modulLLM.com - Real-time Emotion Detection & Response",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
emotion_detector = EmotionDetector()
minimax_client = MiniMaxClient()

# Pydantic models
class EmotionAnalysisRequest(BaseModel):
    text: str
    language: str = "tr"
    context: Optional[str] = None

class Emotion(BaseModel):
    type: str
    confidence: float
    label: str
    emoji: str

class EmotionAnalysisResponse(BaseModel):
    emotions: List[Emotion]
    primary_emotion: str
    response_suggestion: str
    timestamp: str

class ChatMessage(BaseModel):
    text: str
    emotion_context: Optional[Dict] = None

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        await websocket.send_json(message)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

# Routes
@app.get("/")
async def root():
    return {
        "name": "12. İnci (Pearl) Modeli",
        "version": "1.0.0",
        "description": "modulLLM.com - Real-time Emotion AI",
        "status": "operational",
        "endpoints": {
            "analyze": "/api/v1/emotion/analyze",
            "websocket": "/ws/emotion/realtime",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "emotion_detector": emotion_detector.is_ready(),
            "minimax_client": minimax_client.is_ready()
        }
    }

@app.post("/api/v1/emotion/analyze", response_model=EmotionAnalysisResponse)
async def analyze_emotion(request: EmotionAnalysisRequest):
    """
    Analyze emotions in text and get AI-generated response
    """
    try:
        # Detect emotions
        emotions = await emotion_detector.detect(
            text=request.text,
            language=request.language
        )

        if not emotions:
            raise HTTPException(status_code=400, detail="Duygu tespiti yapılamadı")

        # Get primary emotion
        primary = emotions[0]

        # Generate emotion-aware response using MiniMax-M2
        ai_response = await minimax_client.generate_emotion_response(
            text=request.text,
            emotions=emotions,
            context=request.context
        )

        return EmotionAnalysisResponse(
            emotions=emotions,
            primary_emotion=primary.type,
            response_suggestion=ai_response,
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        logger.error(f"Emotion analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/emotion/realtime")
async def websocket_emotion_endpoint(websocket: WebSocket):
    """
    Real-time emotion detection and AI response via WebSocket
    """
    await manager.connect(websocket)

    try:
        # Send welcome message
        await manager.send_personal_message({
            "type": "connected",
            "message": "12. İnci Modeli'ne bağlandınız! 💎",
            "timestamp": datetime.now().isoformat()
        }, websocket)

        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)

            user_text = message_data.get("text", "")
            context = message_data.get("context")

            if not user_text:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Boş mesaj gönderilemez"
                }, websocket)
                continue

            # Detect emotions
            emotions = await emotion_detector.detect(
                text=user_text,
                language="tr"
            )

            # Generate AI response
            ai_response = await minimax_client.generate_emotion_response(
                text=user_text,
                emotions=emotions,
                context=context,
                stream=False  # WebSocket için streaming kapalı
            )

            # Send response
            response = {
                "type": "emotion_response",
                "user_message": user_text,
                "emotions": [e.dict() for e in emotions],
                "primary_emotion": emotions[0].type if emotions else "neutral",
                "ai_response": ai_response,
                "timestamp": datetime.now().isoformat()
            }

            await manager.send_personal_message(response, websocket)

            logger.info(f"Processed message: {user_text[:50]}... | Emotion: {emotions[0].type if emotions else 'none'}")

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        await manager.send_personal_message({
            "type": "error",
            "message": f"Bir hata oluştu: {str(e)}"
        }, websocket)

@app.post("/api/v1/chat")
async def chat_endpoint(message: ChatMessage):
    """
    Traditional REST chat endpoint
    """
    try:
        # Detect emotions
        emotions = await emotion_detector.detect(
            text=message.text,
            language="tr"
        )

        # Generate response
        ai_response = await minimax_client.generate_emotion_response(
            text=message.text,
            emotions=emotions,
            context=message.emotion_context
        )

        return {
            "response": ai_response,
            "emotions": [e.dict() for e in emotions],
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/emotions/list")
async def list_emotions():
    """
    Get list of 12 supported emotions
    """
    return {
        "emotions": emotion_detector.get_emotion_categories(),
        "total": 12,
        "description": "12 İnci (Pearl) - 12 Temel Duygu Kategorisi"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
