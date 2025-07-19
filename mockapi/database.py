from sqlalchemy import create_engine, Column, String, Text, Float, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

load_dotenv()

# Database configuration - use /tmp for Lambda compatibility
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////tmp/tiles_events.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class UserMemory(Base):
    """Store user preferences and learned patterns"""
    __tablename__ = "user_memory"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_session = Column(String(255), nullable=False)
    preference_type = Column(String(100), nullable=False)  # 'color', 'style', 'music', 'venue', 'event_type'
    preference_value = Column(Text, nullable=False)
    confidence_score = Column(Float, default=1.0)  # How confident we are about this preference
    context = Column(JSON, nullable=True)  # Additional context data
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatSession(Base):
    """Store chat sessions with event context"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(255), unique=True, nullable=False)
    event_context = Column(JSON, nullable=True)  # event type, current preferences, etc.
    user_session = Column(String(255), nullable=False)  # Link to user memory
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with messages
    messages = relationship("ChatMessage", back_populates="chat_session", cascade="all, delete-orphan")

class ChatMessage(Base):
    """Store individual chat messages with AI suggestions"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    content = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    ai_suggestions = Column(JSON, nullable=True)  # Generated images, music, etc.
    user_feedback = Column(String(50), nullable=True)  # 'approved', 'rejected', 'modified'
    preference_updates = Column(JSON, nullable=True)  # What preferences were learned from this message
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    chat_session = relationship("ChatSession", back_populates="messages")

class GeneratedContent(Base):
    """Store generated images and music for caching and learning"""
    __tablename__ = "generated_content"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_message_id = Column(String, ForeignKey("chat_messages.id"), nullable=False)
    content_type = Column(String(20), nullable=False)  # 'image' or 'music'
    content_data = Column(JSON, nullable=False)  # Image URLs, music data, etc.
    generation_prompt = Column(Text, nullable=False)  # What prompt was used
    user_rating = Column(Float, nullable=True)  # User feedback score
    created_at = Column(DateTime, default=datetime.utcnow)

class PlanSession(Base):
    """Track plan state and completion"""
    __tablename__ = "plan_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    plan_status = Column(String, default="discovering")  # discovering → planning → generating → reviewing → completed
    satisfaction_score = Column(Float, default=0.0)
    completion_confidence = Column(Float, default=0.0)
    user_goals = Column(JSON, nullable=True)  # What user wants to achieve
    generated_content = Column(JSON, nullable=True)  # Images, music, etc.
    refinement_history = Column(JSON, nullable=True)  # Track what's been changed
    last_state_change = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    chat_session = relationship("ChatSession", backref="plan_sessions")

# Plan state constants
PLAN_STATES = {
    "discovering": "Learning user preferences and event goals",
    "planning": "Developing specific event recommendations", 
    "generating": "Creating visual and audio content",
    "reviewing": "User is evaluating the generated plan",
    "refining": "Making adjustments based on feedback",
    "completed": "Plan approved and finalized"
}

# Create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Dependency for database sessions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Helper functions for user memory
def store_user_preference(db, user_session: str, pref_type: str, pref_value: str, confidence: float = 1.0, context: dict = None):
    """Store or update a user preference"""
    # Check if preference already exists
    existing = db.query(UserMemory).filter(
        UserMemory.user_session == user_session,
        UserMemory.preference_type == pref_type,
        UserMemory.preference_value == pref_value
    ).first()
    
    if existing:
        # Update confidence score (weighted average)
        existing.confidence_score = (existing.confidence_score + confidence) / 2
        existing.updated_at = datetime.utcnow()
        if context:
            existing.context = context
    else:
        # Create new preference
        new_pref = UserMemory(
            user_session=user_session,
            preference_type=pref_type,
            preference_value=pref_value,
            confidence_score=confidence,
            context=context
        )
        db.add(new_pref)
    
    db.commit()

def get_user_preferences(db, user_session: str, pref_type: str = None):
    """Retrieve user preferences, optionally filtered by type"""
    query = db.query(UserMemory).filter(UserMemory.user_session == user_session)
    
    if pref_type:
        query = query.filter(UserMemory.preference_type == pref_type)
    
    return query.order_by(UserMemory.confidence_score.desc()).all()

# Plan management functions
def get_or_create_plan_session(db, chat_session_id: str):
    """Get existing plan session or create new one"""
    plan_session = db.query(PlanSession).filter(
        PlanSession.chat_session_id == chat_session_id
    ).first()
    
    if not plan_session:
        plan_session = PlanSession(
            chat_session_id=chat_session_id,
            plan_status="discovering",
            user_goals={},
            generated_content={},
            refinement_history=[]
        )
        db.add(plan_session)
        db.commit()
    
    return plan_session

def update_plan_state(db, plan_session: PlanSession, new_status: str, **kwargs):
    """Update plan session state with additional data"""
    plan_session.plan_status = new_status
    plan_session.last_state_change = datetime.utcnow()
    
    # Update optional fields
    if 'satisfaction_score' in kwargs:
        plan_session.satisfaction_score = kwargs['satisfaction_score']
    if 'completion_confidence' in kwargs:
        plan_session.completion_confidence = kwargs['completion_confidence']
    if 'user_goals' in kwargs:
        plan_session.user_goals = kwargs['user_goals']
    if 'generated_content' in kwargs:
        plan_session.generated_content = kwargs['generated_content']
    if 'refinement_history' in kwargs:
        plan_session.refinement_history = kwargs['refinement_history']
    
    db.commit()
    return plan_session

def get_plan_progress(db, chat_session_id: str):
    """Get plan progress summary"""
    plan_session = db.query(PlanSession).filter(
        PlanSession.chat_session_id == chat_session_id
    ).first()
    
    if not plan_session:
        return {"status": "not_started", "progress": 0.0}
    
    # Calculate progress percentage
    progress_map = {
        "discovering": 0.1,
        "planning": 0.3,
        "generating": 0.6,
        "reviewing": 0.8,
        "refining": 0.9,
        "completed": 1.0
    }
    
    return {
        "status": plan_session.plan_status,
        "progress": progress_map.get(plan_session.plan_status, 0.0),
        "satisfaction": plan_session.satisfaction_score,
        "confidence": plan_session.completion_confidence,
        "description": PLAN_STATES.get(plan_session.plan_status, "Unknown state")
    }