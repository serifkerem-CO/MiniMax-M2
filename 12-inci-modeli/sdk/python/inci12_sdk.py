"""
12. İnci Modeli - Python SDK
Official Python client for 12. İnci Emotion AI API

Installation:
    pip install inci12-sdk

Usage:
    from inci12_sdk import InciClient

    client = InciClient(api_key="your_api_key")
    result = client.analyze_emotion("Bugün çok mutluyum!")
    print(result.primary_emotion)  # "joy"
"""

import requests
import json
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from datetime import datetime
import asyncio
import aiohttp
import websockets


__version__ = "1.0.0"
__author__ = "modulLLM.com"


# ============================================
# Data Models
# ============================================

@dataclass
class Emotion:
    """Detected emotion"""
    type: str
    confidence: float
    label: str
    emoji: str

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


@dataclass
class EmotionAnalysisResult:
    """Result of emotion analysis"""
    emotions: List[Emotion]
    primary_emotion: str
    response_suggestion: str
    timestamp: str

    @property
    def top_emotion(self) -> Emotion:
        """Get primary emotion object"""
        return self.emotions[0] if self.emotions else None

    @classmethod
    def from_dict(cls, data: dict):
        emotions = [Emotion.from_dict(e) for e in data.get("emotions", [])]
        return cls(
            emotions=emotions,
            primary_emotion=data.get("primary_emotion"),
            response_suggestion=data.get("response_suggestion"),
            timestamp=data.get("timestamp")
        )


# ============================================
# Synchronous Client
# ============================================

class InciClient:
    """
    Synchronous client for 12. İnci Modeli API

    Example:
        client = InciClient(api_key="your_key")
        result = client.analyze_emotion("Merhaba!")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000"
    ):
        """
        Initialize client

        Args:
            api_key: Optional API key for authentication
            base_url: Base API URL
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

        if api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {api_key}"
            })

    def analyze_emotion(
        self,
        text: str,
        language: str = "tr",
        context: Optional[str] = None
    ) -> EmotionAnalysisResult:
        """
        Analyze emotion in text

        Args:
            text: Text to analyze
            language: Language code (tr or en)
            context: Optional context

        Returns:
            EmotionAnalysisResult

        Raises:
            requests.HTTPError: If API request fails
        """
        endpoint = f"{self.base_url}/api/v1/emotion/analyze"
        payload = {
            "text": text,
            "language": language
        }
        if context:
            payload["context"] = context

        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()

        return EmotionAnalysisResult.from_dict(response.json())

    def get_emotions_list(self) -> List[Dict]:
        """
        Get list of 12 emotion categories

        Returns:
            List of emotion category dicts
        """
        endpoint = f"{self.base_url}/api/v1/emotions/list"
        response = self.session.get(endpoint)
        response.raise_for_status()

        return response.json().get("emotions", [])

    def chat(
        self,
        message: str,
        emotion_context: Optional[Dict] = None
    ) -> Dict:
        """
        Send chat message

        Args:
            message: Chat message
            emotion_context: Optional emotion context

        Returns:
            Chat response dict
        """
        endpoint = f"{self.base_url}/api/v1/chat"
        payload = {"text": message}
        if emotion_context:
            payload["emotion_context"] = emotion_context

        response = self.session.post(endpoint, json=payload)
        response.raise_for_status()

        return response.json()

    def health_check(self) -> bool:
        """
        Check API health

        Returns:
            True if healthy, False otherwise
        """
        try:
            endpoint = f"{self.base_url}/health"
            response = self.session.get(endpoint, timeout=5)
            return response.status_code == 200
        except:
            return False


# ============================================
# Async Client
# ============================================

class AsyncInciClient:
    """
    Async client for 12. İnci Modeli API

    Example:
        async with AsyncInciClient(api_key="your_key") as client:
            result = await client.analyze_emotion("Merhaba!")
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "http://localhost:8000"
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        headers = {}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        self.session = aiohttp.ClientSession(headers=headers)
        return self

    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()

    async def analyze_emotion(
        self,
        text: str,
        language: str = "tr",
        context: Optional[str] = None
    ) -> EmotionAnalysisResult:
        """Async emotion analysis"""
        endpoint = f"{self.base_url}/api/v1/emotion/analyze"
        payload = {
            "text": text,
            "language": language
        }
        if context:
            payload["context"] = context

        async with self.session.post(endpoint, json=payload) as response:
            response.raise_for_status()
            data = await response.json()
            return EmotionAnalysisResult.from_dict(data)

    async def get_emotions_list(self) -> List[Dict]:
        """Get emotion categories async"""
        endpoint = f"{self.base_url}/api/v1/emotions/list"
        async with self.session.get(endpoint) as response:
            response.raise_for_status()
            data = await response.json()
            return data.get("emotions", [])


# ============================================
# WebSocket Client
# ============================================

class InciWebSocketClient:
    """
    WebSocket client for real-time emotion chat

    Example:
        async with InciWebSocketClient() as client:
            response = await client.send_message("Merhaba!")
            print(response)
    """

    def __init__(self, ws_url: str = "ws://localhost:8000/ws/emotion/realtime"):
        self.ws_url = ws_url
        self.websocket = None

    async def __aenter__(self):
        self.websocket = await websockets.connect(self.ws_url)
        # Receive welcome message
        welcome = await self.websocket.recv()
        return self

    async def __aexit__(self, *args):
        if self.websocket:
            await self.websocket.close()

    async def send_message(self, text: str) -> Dict:
        """
        Send message and receive response

        Args:
            text: Message text

        Returns:
            Response dict with emotions and AI response
        """
        message = {
            "type": "message",
            "text": text
        }

        await self.websocket.send(json.dumps(message))
        response = await self.websocket.recv()

        return json.loads(response)

    async def listen(self, callback):
        """
        Listen for messages

        Args:
            callback: Async function to call with each message
        """
        async for message in self.websocket:
            data = json.loads(message)
            await callback(data)


# ============================================
# Convenience Functions
# ============================================

def quick_analyze(text: str, api_key: Optional[str] = None) -> EmotionAnalysisResult:
    """
    Quick emotion analysis

    Args:
        text: Text to analyze
        api_key: Optional API key

    Returns:
        EmotionAnalysisResult
    """
    client = InciClient(api_key=api_key)
    return client.analyze_emotion(text)


async def async_quick_analyze(
    text: str,
    api_key: Optional[str] = None
) -> EmotionAnalysisResult:
    """Async quick analysis"""
    async with AsyncInciClient(api_key=api_key) as client:
        return await client.analyze_emotion(text)


# ============================================
# CLI Tool
# ============================================

def cli():
    """Command-line interface"""
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="12. İnci Modeli CLI")
    parser.add_argument("text", help="Text to analyze")
    parser.add_argument("--api-key", help="API key")
    parser.add_argument("--lang", default="tr", help="Language (tr/en)")

    args = parser.parse_args()

    try:
        result = quick_analyze(args.text, api_key=args.api_key)

        print(f"\n{'='*50}")
        print(f"📝 Text: {args.text}")
        print(f"{'='*50}")
        print(f"\n🎯 Detected Emotions:")

        for i, emotion in enumerate(result.emotions, 1):
            print(f"  {i}. {emotion.emoji} {emotion.label} - {emotion.confidence*100:.0f}%")

        print(f"\n💎 Primary: {result.primary_emotion}")
        print(f"\n🤖 AI Response:")
        print(f"  {result.response_suggestion}")
        print(f"\n{'='*50}\n")

    except Exception as e:
        print(f"❌ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    cli()
