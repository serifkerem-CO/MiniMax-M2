"""
Test Suite for 12. İnci Modeli
pytest test suite for emotion detection and API endpoints
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket
import json

# Import from main app
import sys
sys.path.insert(0, '..')
from main import app
from emotion_detector import EmotionDetector, Emotion
from minimax_client import MiniMaxClient

# Test client
client = TestClient(app)

# ============================================
# Emotion Detector Tests
# ============================================

class TestEmotionDetector:
    """Test emotion detection engine"""

    @pytest.fixture
    def detector(self):
        return EmotionDetector()

    @pytest.mark.asyncio
    async def test_joy_detection(self, detector):
        """Test happiness/joy detection"""
        text = "Bugün çok mutluyum! Harika bir gün geçirdim!"
        emotions = await detector.detect(text)

        assert len(emotions) > 0
        assert emotions[0].type == "joy"
        assert emotions[0].confidence > 0.5
        assert emotions[0].emoji == "😊"

    @pytest.mark.asyncio
    async def test_sadness_detection(self, detector):
        """Test sadness detection"""
        text = "Çok üzgünüm, bugün kötü bir gün geçirdim"
        emotions = await detector.detect(text)

        assert len(emotions) > 0
        assert emotions[0].type == "sadness"
        assert emotions[0].label == "Üzüntü"

    @pytest.mark.asyncio
    async def test_anger_detection(self, detector):
        """Test anger detection"""
        text = "Çok sinirliyim, bu duruma çok kızdım!"
        emotions = await detector.detect(text)

        assert len(emotions) > 0
        assert emotions[0].type == "anger"

    @pytest.mark.asyncio
    async def test_multiple_emotions(self, detector):
        """Test multiple emotion detection"""
        text = "Hem mutluyum hem de biraz endişeliyim"
        emotions = await detector.detect(text)

        assert len(emotions) >= 2
        emotion_types = [e.type for e in emotions]
        assert "joy" in emotion_types or "fear" in emotion_types

    @pytest.mark.asyncio
    async def test_neutral_text(self, detector):
        """Test neutral/no emotion text"""
        text = "Bugün bir toplantı var"
        emotions = await detector.detect(text)

        assert len(emotions) > 0  # Should return default emotion

    @pytest.mark.asyncio
    async def test_empty_text(self, detector):
        """Test empty text"""
        text = ""
        emotions = await detector.detect(text)

        # Should handle gracefully
        assert isinstance(emotions, list)

    def test_emotion_categories(self, detector):
        """Test getting emotion categories"""
        categories = detector.get_emotion_categories()

        assert len(categories) == 12
        assert all('type' in cat for cat in categories)
        assert all('emoji' in cat for cat in categories)

    def test_detector_ready(self, detector):
        """Test detector is ready"""
        assert detector.is_ready() == True


# ============================================
# API Endpoint Tests
# ============================================

class TestAPIEndpoints:
    """Test REST API endpoints"""

    def test_root_endpoint(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "12. İnci" in data["name"]

    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "services" in data

    def test_emotion_analyze_endpoint(self):
        """Test emotion analysis endpoint"""
        payload = {
            "text": "Bugün çok mutluyum!",
            "language": "tr"
        }
        response = client.post("/api/v1/emotion/analyze", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "emotions" in data
        assert "primary_emotion" in data
        assert len(data["emotions"]) > 0

    def test_emotion_analyze_empty_text(self):
        """Test emotion analysis with empty text"""
        payload = {
            "text": "",
            "language": "tr"
        }
        response = client.post("/api/v1/emotion/analyze", json=payload)
        # Should handle gracefully (might be 400 or return neutral)
        assert response.status_code in [200, 400]

    def test_emotion_list_endpoint(self):
        """Test emotion list endpoint"""
        response = client.get("/api/v1/emotions/list")
        assert response.status_code == 200

        data = response.json()
        assert "emotions" in data
        assert data["total"] == 12

    def test_chat_endpoint(self):
        """Test chat endpoint"""
        payload = {
            "text": "Merhaba, nasılsın?"
        }
        response = client.post("/api/v1/chat", json=payload)
        assert response.status_code == 200

        data = response.json()
        assert "response" in data
        assert "emotions" in data


# ============================================
# WebSocket Tests
# ============================================

class TestWebSocket:
    """Test WebSocket functionality"""

    def test_websocket_connection(self):
        """Test WebSocket connection"""
        with client.websocket_connect("/ws/emotion/realtime") as websocket:
            # Should receive welcome message
            data = websocket.receive_json()
            assert data["type"] == "connected"

    def test_websocket_message_exchange(self):
        """Test sending and receiving messages via WebSocket"""
        with client.websocket_connect("/ws/emotion/realtime") as websocket:
            # Receive welcome
            welcome = websocket.receive_json()

            # Send message
            message = {
                "type": "message",
                "text": "Bugün mutluyum!"
            }
            websocket.send_json(message)

            # Receive response
            response = websocket.receive_json()
            assert response["type"] == "emotion_response"
            assert "emotions" in response
            assert "ai_response" in response


# ============================================
# MiniMax Client Tests
# ============================================

class TestMiniMaxClient:
    """Test MiniMax-M2 client"""

    @pytest.fixture
    def client_instance(self):
        return MiniMaxClient()

    def test_client_initialization(self, client_instance):
        """Test client initializes correctly"""
        assert client_instance is not None
        assert hasattr(client_instance, 'api_key')

    def test_emotion_context_building(self, client_instance):
        """Test emotion context building"""
        emotions = [
            Emotion(type="joy", confidence=0.9, label="Mutluluk", emoji="😊"),
            Emotion(type="excitement", confidence=0.7, label="Heyecan", emoji="🎉")
        ]

        context = client_instance._build_emotion_context(emotions)
        assert "Mutluluk" in context
        assert "😊" in context

    def test_fallback_response(self, client_instance):
        """Test fallback response generation"""
        emotions = [
            Emotion(type="joy", confidence=0.9, label="Mutluluk", emoji="😊")
        ]

        response = client_instance._generate_fallback_response(emotions)
        assert isinstance(response, str)
        assert len(response) > 0


# ============================================
# Integration Tests
# ============================================

class TestIntegration:
    """Integration tests for full workflow"""

    @pytest.mark.asyncio
    async def test_full_emotion_flow(self):
        """Test complete emotion detection and response flow"""
        detector = EmotionDetector()

        # Step 1: Detect emotion
        text = "Bugün harika bir gün geçirdim, çok mutluyum!"
        emotions = await detector.detect(text)

        assert len(emotions) > 0

        # Step 2: Generate response (would use MiniMax in production)
        assert emotions[0].type == "joy"

    def test_api_to_emotion_detection_flow(self):
        """Test API -> Emotion Detection flow"""
        payload = {
            "text": "Çok üzgünüm bugün",
            "language": "tr"
        }

        response = client.post("/api/v1/emotion/analyze", json=payload)
        assert response.status_code == 200

        data = response.json()
        emotions = data["emotions"]
        assert len(emotions) > 0
        # Should detect sadness
        assert any(e["type"] == "sadness" for e in emotions)


# ============================================
# Performance Tests
# ============================================

class TestPerformance:
    """Performance and load tests"""

    @pytest.mark.asyncio
    async def test_emotion_detection_speed(self):
        """Test emotion detection speed"""
        import time

        detector = EmotionDetector()
        text = "Bugün çok mutluyum!"

        start = time.time()
        emotions = await detector.detect(text)
        end = time.time()

        elapsed = (end - start) * 1000  # Convert to ms

        # Should be under 200ms
        assert elapsed < 200
        assert len(emotions) > 0

    def test_api_response_time(self):
        """Test API response time"""
        import time

        payload = {"text": "Merhaba", "language": "tr"}

        start = time.time()
        response = client.post("/api/v1/emotion/analyze", json=payload)
        end = time.time()

        elapsed = (end - start) * 1000

        # Should be reasonably fast (under 2 seconds for local)
        assert elapsed < 2000
        assert response.status_code == 200


# ============================================
# Run Tests
# ============================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
