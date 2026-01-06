"""
Database Models for 12. İnci Modeli
SQLAlchemy models for users, sessions, emotions, and analytics
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()


class User(Base):
    """User model for authentication and tracking"""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=True)

    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)

    api_key = Column(String(64), unique=True, nullable=True)
    api_calls_count = Column(Integer, default=0)
    api_calls_limit = Column(Integer, default=1000)  # per month

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    sessions = relationship("EmotionSession", back_populates="user", cascade="all, delete-orphan")
    emotions = relationship("EmotionRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username}>"


class EmotionSession(Base):
    """Conversation/chat session"""
    __tablename__ = "emotion_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    session_type = Column(String(50), default="chat")  # chat, api, websocket
    status = Column(String(20), default="active")  # active, completed, abandoned

    message_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)  # milliseconds
    total_duration = Column(Integer, default=0)  # seconds

    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    metadata = Column(JSON, nullable=True)  # Browser info, IP, etc.

    # Relationships
    user = relationship("User", back_populates="sessions")
    emotions = relationship("EmotionRecord", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<EmotionSession {self.id}>"


class EmotionRecord(Base):
    """Individual emotion detection record"""
    __tablename__ = "emotion_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("emotion_sessions.id"), nullable=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)

    # Input
    text = Column(Text, nullable=False)
    text_length = Column(Integer, nullable=False)
    language = Column(String(10), default="tr")

    # Primary emotion
    primary_emotion = Column(String(50), nullable=False)
    primary_confidence = Column(Float, nullable=False)

    # All detected emotions
    emotions_detected = Column(JSON, nullable=False)  # List of emotion objects

    # AI response
    ai_response = Column(Text, nullable=True)
    ai_model = Column(String(50), default="MiniMax-M2")

    # Performance metrics
    detection_time_ms = Column(Float, nullable=True)
    response_time_ms = Column(Float, nullable=True)
    total_time_ms = Column(Float, nullable=True)

    # Flags
    cached = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    # Relationships
    session = relationship("EmotionSession", back_populates="emotions")
    user = relationship("User", back_populates="emotions")

    def __repr__(self):
        return f"<EmotionRecord {self.primary_emotion} @ {self.created_at}>"


class EmotionFeedback(Base):
    """User feedback on emotion detection accuracy"""
    __tablename__ = "emotion_feedback"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    emotion_record_id = Column(String(36), ForeignKey("emotion_records.id"))

    was_accurate = Column(Boolean, nullable=False)
    correct_emotion = Column(String(50), nullable=True)  # If was_accurate=False

    rating = Column(Integer, nullable=True)  # 1-5 stars
    comment = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Feedback {self.was_accurate}>"


class APIUsage(Base):
    """API usage tracking for rate limiting and analytics"""
    __tablename__ = "api_usage"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    api_key = Column(String(64), nullable=True, index=True)

    endpoint = Column(String(200), nullable=False)
    method = Column(String(10), nullable=False)

    status_code = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)

    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)

    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    def __repr__(self):
        return f"<APIUsage {self.endpoint} @ {self.created_at}>"


class EmotionStats(Base):
    """Aggregated emotion statistics (hourly/daily)"""
    __tablename__ = "emotion_stats"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    period = Column(String(20), nullable=False)  # hourly, daily, weekly
    period_start = Column(DateTime, nullable=False, index=True)
    period_end = Column(DateTime, nullable=False)

    total_requests = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)

    # Emotion distribution
    emotion_counts = Column(JSON, nullable=False)  # {"joy": 150, "sadness": 30, ...}

    avg_confidence = Column(Float, nullable=True)
    avg_response_time = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<EmotionStats {self.period} @ {self.period_start}>"


# ============================================
# Database Setup Functions
# ============================================

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_database_url():
    """Get database URL from environment"""
    return os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/inci12"
    )

def create_tables(database_url: str = None):
    """Create all tables"""
    url = database_url or get_database_url()
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    print(f"✅ Database tables created: {url}")

def get_session_maker(database_url: str = None):
    """Get SQLAlchemy session maker"""
    url = database_url or get_database_url()
    engine = create_engine(url, pool_pre_ping=True)
    return sessionmaker(bind=engine)

# Dependency for FastAPI
def get_db():
    """Database session dependency for FastAPI"""
    SessionLocal = get_session_maker()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
