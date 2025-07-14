from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class MessageCreate(BaseModel):
    content: str
    user_session: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    content: str
    role: str
    timestamp: str
    ai_suggestions: Optional[Dict] = None
    image_data: Optional[List] = None
    music_data: Optional[List] = None
    venue_data: Optional[List] = None

class ChatSessionResponse(BaseModel):
    chatId: str
    title: str
    createdAt: str
    messages: List[MessageResponse] = []

class AIMemoryResponse(BaseModel):
    summary: str
    active_monitoring: List[str]
    plan_status: str
    satisfaction_score: float = 1.0
    completion_confidence: float = 1.0

class GalleryResponse(BaseModel):
    images: List[Dict]
    message: Optional[str] = None
    style: Optional[str] = None

class ServiceStatusResponse(BaseModel):
    message: str
    services: Dict[str, bool]