"""
Analytics & Monitoring System for 12. İnci Modeli
Tracks emotion patterns, usage metrics, and system performance
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import json
import logging
from dataclasses import dataclass, asdict
from prometheus_client import Counter as PromCounter, Histogram, Gauge
import asyncio

logger = logging.getLogger(__name__)

# ============================================
# Prometheus Metrics
# ============================================

# Request metrics
emotion_analysis_requests = PromCounter(
    'emotion_analysis_requests_total',
    'Total emotion analysis requests',
    ['emotion_type', 'language']
)

websocket_connections = Gauge(
    'websocket_connections_active',
    'Number of active WebSocket connections'
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method']
)

emotion_detection_duration = Histogram(
    'emotion_detection_duration_seconds',
    'Emotion detection duration'
)

ai_response_duration = Histogram(
    'ai_response_generation_duration_seconds',
    'AI response generation duration'
)

# Error metrics
api_errors = PromCounter(
    'api_errors_total',
    'Total API errors',
    ['error_type', 'endpoint']
)

# ============================================
# Analytics Data Models
# ============================================

@dataclass
class EmotionEvent:
    """Single emotion detection event"""
    timestamp: str
    user_id: Optional[str]
    text_length: int
    primary_emotion: str
    all_emotions: List[str]
    confidence: float
    response_time_ms: float
    language: str = "tr"

@dataclass
class SessionMetrics:
    """User session metrics"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    message_count: int
    emotions_detected: Dict[str, int]
    avg_response_time: float
    total_duration_seconds: float

@dataclass
class SystemMetrics:
    """System-wide metrics"""
    timestamp: str
    total_requests: int
    active_connections: int
    avg_response_time: float
    error_rate: float
    emotion_distribution: Dict[str, int]

# ============================================
# Analytics Engine
# ============================================

class AnalyticsEngine:
    """
    Analytics and monitoring engine for 12. İnci Modeli
    """

    def __init__(self):
        self.events: List[EmotionEvent] = []
        self.sessions: Dict[str, SessionMetrics] = {}
        self.emotion_counts = Counter()
        self.hourly_stats = defaultdict(lambda: {
            'requests': 0,
            'emotions': Counter(),
            'avg_time': []
        })

        logger.info("Analytics engine initialized")

    async def track_emotion_event(
        self,
        text: str,
        emotions: List,
        response_time_ms: float,
        user_id: Optional[str] = None,
        language: str = "tr"
    ):
        """
        Track an emotion detection event
        """
        try:
            if not emotions:
                return

            primary = emotions[0]

            # Create event
            event = EmotionEvent(
                timestamp=datetime.now().isoformat(),
                user_id=user_id,
                text_length=len(text),
                primary_emotion=primary.type,
                all_emotions=[e.type for e in emotions],
                confidence=primary.confidence,
                response_time_ms=response_time_ms,
                language=language
            )

            # Store event
            self.events.append(event)

            # Update counters
            self.emotion_counts[primary.type] += 1

            # Update Prometheus metrics
            emotion_analysis_requests.labels(
                emotion_type=primary.type,
                language=language
            ).inc()

            # Update hourly stats
            hour_key = datetime.now().strftime("%Y-%m-%d-%H")
            self.hourly_stats[hour_key]['requests'] += 1
            self.hourly_stats[hour_key]['emotions'][primary.type] += 1
            self.hourly_stats[hour_key]['avg_time'].append(response_time_ms)

            logger.debug(f"Tracked emotion event: {primary.type} ({primary.confidence:.2f})")

        except Exception as e:
            logger.error(f"Error tracking emotion event: {str(e)}")

    async def track_websocket_connection(self, connected: bool):
        """Track WebSocket connection changes"""
        if connected:
            websocket_connections.inc()
        else:
            websocket_connections.dec()

    async def track_error(self, error_type: str, endpoint: str):
        """Track API errors"""
        api_errors.labels(
            error_type=error_type,
            endpoint=endpoint
        ).inc()

    def get_emotion_distribution(self, hours: int = 24) -> Dict[str, int]:
        """
        Get emotion distribution for the last N hours
        """
        cutoff = datetime.now() - timedelta(hours=hours)

        distribution = Counter()
        for event in self.events:
            event_time = datetime.fromisoformat(event.timestamp)
            if event_time >= cutoff:
                distribution[event.primary_emotion] += 1

        return dict(distribution)

    def get_top_emotions(self, limit: int = 5) -> List[Dict]:
        """Get top N emotions"""
        return [
            {"emotion": emotion, "count": count}
            for emotion, count in self.emotion_counts.most_common(limit)
        ]

    def get_hourly_stats(self, hours: int = 24) -> List[Dict]:
        """Get hourly statistics"""
        stats = []
        now = datetime.now()

        for i in range(hours):
            hour_time = now - timedelta(hours=i)
            hour_key = hour_time.strftime("%Y-%m-%d-%H")

            if hour_key in self.hourly_stats:
                data = self.hourly_stats[hour_key]
                avg_time = (
                    sum(data['avg_time']) / len(data['avg_time'])
                    if data['avg_time'] else 0
                )

                stats.append({
                    "hour": hour_key,
                    "requests": data['requests'],
                    "avg_response_time": round(avg_time, 2),
                    "top_emotion": data['emotions'].most_common(1)[0][0]
                    if data['emotions'] else None
                })

        return sorted(stats, key=lambda x: x['hour'])

    def get_system_metrics(self) -> SystemMetrics:
        """Get current system metrics"""
        recent_events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) > datetime.now() - timedelta(hours=1)
        ]

        avg_response = (
            sum(e.response_time_ms for e in recent_events) / len(recent_events)
            if recent_events else 0
        )

        return SystemMetrics(
            timestamp=datetime.now().isoformat(),
            total_requests=len(self.events),
            active_connections=int(websocket_connections._value.get()),
            avg_response_time=round(avg_response, 2),
            error_rate=0.0,  # Would calculate from error tracking
            emotion_distribution=self.get_emotion_distribution(hours=1)
        )

    def get_analytics_summary(self) -> Dict:
        """Get comprehensive analytics summary"""
        return {
            "total_events": len(self.events),
            "emotion_distribution": dict(self.emotion_counts),
            "top_emotions": self.get_top_emotions(),
            "hourly_stats": self.get_hourly_stats(hours=24),
            "system_metrics": asdict(self.get_system_metrics())
        }

    def export_metrics(self, filepath: str):
        """Export metrics to JSON file"""
        try:
            data = self.get_analytics_summary()
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            logger.info(f"Metrics exported to {filepath}")

        except Exception as e:
            logger.error(f"Error exporting metrics: {str(e)}")

    def clear_old_events(self, days: int = 7):
        """Clear events older than N days"""
        cutoff = datetime.now() - timedelta(days=days)

        original_count = len(self.events)
        self.events = [
            e for e in self.events
            if datetime.fromisoformat(e.timestamp) >= cutoff
        ]

        removed = original_count - len(self.events)
        logger.info(f"Cleared {removed} old events")


# ============================================
# Global Analytics Instance
# ============================================

analytics = AnalyticsEngine()


# ============================================
# Analytics API Endpoints (to add to main.py)
# ============================================

"""
Add these endpoints to main.py:

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    return analytics.get_analytics_summary()

@app.get("/api/v1/analytics/emotions")
async def get_emotion_distribution(hours: int = 24):
    return {
        "hours": hours,
        "distribution": analytics.get_emotion_distribution(hours)
    }

@app.get("/api/v1/analytics/top-emotions")
async def get_top_emotions(limit: int = 5):
    return {
        "top_emotions": analytics.get_top_emotions(limit)
    }

@app.get("/metrics")
async def prometheus_metrics():
    from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
"""
