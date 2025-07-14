import uuid
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import ChatSession, ChatMessage
from models import MessageResponse, ChatSessionResponse

class ChatService:
    """Handles chat session and message operations"""
    
    def get_all_chats(self, db: Session) -> List[ChatSessionResponse]:
        """Get all chat sessions with messages"""
        sessions = db.query(ChatSession).all()
        
        result = []
        for session in sessions:
            messages = []
            for msg in session.messages:
                messages.append(MessageResponse(
                    id=msg.id,
                    content=msg.content,
                    role=msg.role,
                    timestamp=msg.timestamp.strftime("%H:%M"),
                    ai_suggestions=msg.ai_suggestions,
                    image_data=msg.ai_suggestions.get("images", []) if msg.ai_suggestions else [],
                    music_data=msg.ai_suggestions.get("music_data", []) if msg.ai_suggestions else [],
                    venue_data=msg.ai_suggestions.get("venue_data", []) if msg.ai_suggestions else []
                ))
            
            result.append(ChatSessionResponse(
                chatId=session.session_id,
                title=session.event_context.get("title", "Untitled Chat") if session.event_context else "Untitled Chat",
                createdAt=session.created_at.strftime("%H:%M"),
                messages=messages
            ))
        
        return result
    
    def create_new_chat(self, db: Session) -> ChatSessionResponse:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        user_session = f"user_{uuid.uuid4()}"
        
        new_session = ChatSession(
            session_id=session_id,
            user_session=user_session,
            event_context={"title": "New Event Planning Chat"}
        )
        
        db.add(new_session)
        db.commit()
        
        return ChatSessionResponse(
            chatId=session_id,
            title="New Event Planning Chat",
            createdAt=new_session.created_at.strftime("%H:%M"),
            messages=[]
        )
    
    def get_chat_by_id(self, chat_id: str, db: Session) -> ChatSessionResponse:
        """Get a specific chat session"""
        session = db.query(ChatSession).filter(ChatSession.session_id == chat_id).first()
        
        if not session:
            return None
        
        messages = []
        for msg in session.messages:
            messages.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp.strftime("%H:%M"),
                ai_suggestions=msg.ai_suggestions,
                image_data=msg.ai_suggestions.get("images", []) if msg.ai_suggestions else [],
                music_data=msg.ai_suggestions.get("music_data", []) if msg.ai_suggestions else [],
                venue_data=msg.ai_suggestions.get("venue_data", []) if msg.ai_suggestions else []
            ))
        
        return ChatSessionResponse(
            chatId=session.session_id,
            title=session.event_context.get("title", "Event Planning Chat") if session.event_context else "Event Planning Chat",
            createdAt=session.created_at.isoformat() + "Z",
            messages=messages
        )
    
    def save_user_message(self, chat_session_id: int, content: str, db: Session) -> ChatMessage:
        """Save user message to database"""
        user_message = ChatMessage(
            chat_session_id=chat_session_id,
            content=content,
            role="user",
            timestamp=datetime.utcnow()
        )
        db.add(user_message)
        db.commit()
        return user_message
    
    def save_ai_message(self, chat_session_id: int, content: str, ai_suggestions: Dict, db: Session) -> ChatMessage:
        """Save AI message to database"""
        ai_message = ChatMessage(
            chat_session_id=chat_session_id,
            content=content,
            role="assistant",
            ai_suggestions=ai_suggestions,
            timestamp=datetime.utcnow()
        )
        db.add(ai_message)
        db.commit()
        return ai_message
    
    def build_conversation_history(self, session: ChatSession) -> List[Dict]:
        """Build conversation history for AI context"""
        conversation_history = []
        for msg in session.messages:
            conversation_history.append({
                "role": msg.role,
                "content": msg.content
            })
        return conversation_history
    
    def update_session_context(self, session: ChatSession, ai_response: Dict, db: Session):
        """Update session context with event information"""
        if ai_response.get("suggestions", {}).get("event_type"):
            event_context = session.event_context or {}
            event_context["event_type"] = ai_response["suggestions"]["event_type"]
            event_context["title"] = f"{ai_response['suggestions']['event_type']} Planning"
            session.event_context = event_context
            db.commit()

chat_service = ChatService()