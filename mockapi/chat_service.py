import uuid
from datetime import datetime
from typing import List, Dict, Any
# from sqlalchemy.orm import Session
from dynamodb_database import ChatSession, ChatMessage
from models import MessageResponse, ChatSessionResponse
from memory_store import memory_store

class ChatService:
    """Handles chat session and message operations"""
    
    def get_all_chats(self, db) -> List[ChatSessionResponse]:
        """Get all chat sessions with messages"""
        sessions = db.query(ChatSession).all()
        
        result = []
        for session in sessions:
            messages = []
            # Query messages separately for DynamoDB
            chat_messages = db.query(ChatMessage).filter({'chat_session_id': session.id}).all()
            for msg in chat_messages:
                # Handle timestamp properly for DynamoDB
                timestamp_str = msg.timestamp.strftime("%H:%M") if isinstance(msg.timestamp, datetime) else msg.timestamp
                messages.append(MessageResponse(
                    id=msg.id,
                    content=msg.content,
                    role=msg.role,
                    timestamp=timestamp_str,
                    ai_suggestions=msg.ai_suggestions,
                    image_data=msg.ai_suggestions.get("images", []) if msg.ai_suggestions else [],
                    music_data=msg.ai_suggestions.get("music_data", []) if msg.ai_suggestions else [],
                    venue_data=msg.ai_suggestions.get("venue_data", []) if msg.ai_suggestions else []
                ))
            
            result.append(ChatSessionResponse(
                chatId=session.session_id,
                title=session.event_context.get("title", "Untitled Chat") if session.event_context else "Untitled Chat",
                createdAt=session.created_at if isinstance(session.created_at, str) else session.created_at.strftime("%H:%M"),
                messages=messages
            ))
        
        return result
    
    def create_new_chat(self, db) -> ChatSessionResponse:
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
            createdAt=new_session.created_at if isinstance(new_session.created_at, str) else new_session.created_at.strftime("%H:%M"),
            messages=[]
        )
    
    def get_chat_by_id(self, chat_id: str, db) -> ChatSessionResponse:
        """Get a specific chat session"""
        session = db.query(ChatSession).filter({'session_id': chat_id}).first()
        
        if not session:
            return None
        
        messages = []
        chat_messages = db.query(ChatMessage).filter({'chat_session_id': session.id}).all()
        for msg in chat_messages:
            messages.append(MessageResponse(
                id=msg.id,
                content=msg.content,
                role=msg.role,
                timestamp=msg.timestamp.strftime("%H:%M") if isinstance(msg.timestamp, datetime) else msg.timestamp,
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
    
    def save_user_message(self, chat_session_id: int, content: str, db) -> ChatMessage:
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
    
    def save_ai_message(self, chat_session_id: int, content: str, ai_suggestions: Dict, db) -> ChatMessage:
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
    
    def build_conversation_history(self, session: ChatSession, db) -> List[Dict]:
        """Build conversation history for AI context - now uses memory store"""
        chat_id = session.session_id
        conversation_history = memory_store.get_conversation_history(chat_id, limit=25)
        print(f"🧠 Built conversation history from memory: {len(conversation_history)} messages for chat {chat_id[:8]}")
        
        # Convert memory format to AI format
        ai_history = []
        for msg in conversation_history:
            ai_history.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        return ai_history
    
    def update_session_context(self, session: ChatSession, ai_response: Dict, db):
        """Update session context - now delegates to memory store"""
        chat_id = session.session_id
        
        # **NEW**: Store AI response in memory instead of complex database context
        memory_store.add_conversation_message(chat_id, "assistant", ai_response.get("message", ""))
        
        # Update extracted data if present
        suggestions = ai_response.get("suggestions", {})
        if suggestions:
            memory_store.update_extracted_data(chat_id, suggestions)
        
        # Update generation state
        generation_updates = {}
        for state_field in ["awaiting_confirmation", "user_confirmed_generation", "conversation_stage", 
                           "awaiting_pdf_confirmation", "pdf_confirmed"]:
            if state_field in ai_response:
                generation_updates[state_field] = ai_response[state_field]
        
        if generation_updates:
            memory_store.update_generation_state(chat_id, generation_updates)
        
        # Store AI suggestions for continuity
        memory_store.store_ai_suggestions(chat_id, ai_response)
        
        # Debug: Show current memory state
        memory_summary = memory_store.get_session_summary(chat_id)
        print(f"🧠 Memory updated: {memory_summary['extracted_fields']} fields, {memory_summary['message_count']} messages")

chat_service = ChatService()