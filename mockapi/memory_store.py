#!/usr/bin/env python3
"""
In-Memory Session Store - Fast, flexible session management without database dependencies
"""

import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import json

class InMemorySessionStore:
    """
    Flexible in-memory session store that eliminates database round-trips for chat context.
    AI can dynamically determine data types and categories without hardcoded validation.
    """
    
    def __init__(self):
        self.sessions = {}
        print("✅ Initialized In-Memory Session Store (zero database dependencies)")
    
    def get_session(self, chat_id: str) -> Dict[str, Any]:
        """Get or create session data for a chat"""
        if chat_id not in self.sessions:
            self.sessions[chat_id] = {
                "chat_id": chat_id,
                "created_at": datetime.utcnow().isoformat(),
                "extracted_data": {},  # Flexible key-value storage for AI-extracted data
                "conversation_history": [],
                "generation_state": {
                    "awaiting_confirmation": False,
                    "user_confirmed": False,
                    "has_generated": False,
                    "conversation_stage": "greeting"
                },
                "generated_content": {
                    "images": [],
                    "music": [],
                    "venues": [],
                    "food": []
                },
                "ai_suggestions": {},  # Last AI response for context
                "metadata": {
                    "message_count": 0,
                    "last_updated": datetime.utcnow().isoformat()
                }
            }
        return self.sessions[chat_id]
    
    def update_extracted_data(self, chat_id: str, new_data: Dict[str, Any]) -> None:
        """
        Flexibly update extracted data - AI determines what's valid, not hardcoded rules.
        Merges new data with existing, preserving non-null values.
        """
        session = self.get_session(chat_id)
        extracted = session["extracted_data"]
        
        # Merge new data, preserving existing non-null values
        for key, value in new_data.items():
            if value is not None and value != "null" and str(value).strip():
                extracted[key] = value
        
        session["metadata"]["last_updated"] = datetime.utcnow().isoformat()
        print(f"🧠 Memory updated: {len(extracted)} fields stored for chat {chat_id[:8]}")
    
    def get_extracted_data(self, chat_id: str) -> Dict[str, Any]:
        """Get all extracted data for AI context building"""
        return self.get_session(chat_id)["extracted_data"]
    
    def add_conversation_message(self, chat_id: str, role: str, content: str) -> None:
        """Add message to conversation history"""
        session = self.get_session(chat_id)
        session["conversation_history"].append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        session["metadata"]["message_count"] += 1
        session["metadata"]["last_updated"] = datetime.utcnow().isoformat()
    
    def get_conversation_history(self, chat_id: str, limit: Optional[int] = None) -> List[Dict]:
        """Get conversation history for AI context"""
        history = self.get_session(chat_id)["conversation_history"]
        if limit:
            return history[-limit:]
        return history
    
    def update_generation_state(self, chat_id: str, state_updates: Dict[str, Any]) -> None:
        """Update generation state (confirmation, stage, etc.)"""
        session = self.get_session(chat_id)
        session["generation_state"].update(state_updates)
        session["metadata"]["last_updated"] = datetime.utcnow().isoformat()
    
    def get_generation_state(self, chat_id: str) -> Dict[str, Any]:
        """Get current generation state"""
        return self.get_session(chat_id)["generation_state"]
    
    def store_generated_content(self, chat_id: str, content_type: str, content: List[Dict]) -> None:
        """Store generated content (images, music, venues, food)"""
        session = self.get_session(chat_id)
        if content_type in session["generated_content"]:
            session["generated_content"][content_type] = content
            session["generation_state"]["has_generated"] = True
            session["metadata"]["last_updated"] = datetime.utcnow().isoformat()
            print(f"🎨 Stored {len(content)} {content_type} items in memory for chat {chat_id[:8]}")
    
    def get_generated_content(self, chat_id: str) -> Dict[str, List]:
        """Get all generated content"""
        return self.get_session(chat_id)["generated_content"]
    
    def store_ai_suggestions(self, chat_id: str, suggestions: Dict[str, Any]) -> None:
        """Store last AI response for context continuity"""
        session = self.get_session(chat_id)
        session["ai_suggestions"] = suggestions
        session["metadata"]["last_updated"] = datetime.utcnow().isoformat()
    
    def get_ai_suggestions(self, chat_id: str) -> Dict[str, Any]:
        """Get last AI suggestions"""
        return self.get_session(chat_id).get("ai_suggestions", {})
    
    def check_data_completeness(self, chat_id: str, required_fields: List[str] = None) -> Dict[str, Any]:
        """
        Flexible completeness check - AI determines what's required based on context.
        No hardcoded validation rules.
        """
        extracted = self.get_extracted_data(chat_id)
        
        if not required_fields:
            # AI will determine completeness dynamically
            return {
                "has_data": len(extracted) > 0,
                "field_count": len(extracted),
                "fields": list(extracted.keys()),
                "completeness_score": min(len(extracted) * 0.15, 1.0)  # Rough estimate
            }
        
        # Check specific fields if provided
        missing = [field for field in required_fields if not extracted.get(field)]
        return {
            "has_data": len(extracted) > 0,
            "field_count": len(extracted),
            "fields": list(extracted.keys()),
            "missing_fields": missing,
            "completeness_score": (len(required_fields) - len(missing)) / len(required_fields) if required_fields else 1.0
        }
    
    def get_session_summary(self, chat_id: str) -> Dict[str, Any]:
        """Get comprehensive session summary for debugging"""
        if chat_id not in self.sessions:
            return {"exists": False}
        
        session = self.sessions[chat_id]
        extracted = session["extracted_data"]
        generated = session["generated_content"]
        
        return {
            "exists": True,
            "chat_id": chat_id,
            "created_at": session["created_at"],
            "message_count": session["metadata"]["message_count"],
            "extracted_fields": len(extracted),
            "extracted_data": extracted,
            "generation_state": session["generation_state"],
            "generated_content_counts": {
                "images": len(generated["images"]),
                "music": len(generated["music"]), 
                "venues": len(generated["venues"]),
                "food": len(generated["food"])
            },
            "last_updated": session["metadata"]["last_updated"]
        }
    
    def clear_session(self, chat_id: str) -> None:
        """Clear specific session"""
        if chat_id in self.sessions:
            del self.sessions[chat_id]
            print(f"🧹 Cleared session {chat_id[:8]} from memory")
    
    def clear_all_sessions(self) -> None:
        """Clear all sessions (for testing/reset)"""
        count = len(self.sessions)
        self.sessions.clear()
        print(f"🧹 Cleared {count} sessions from memory")
    
    def get_active_session_count(self) -> int:
        """Get number of active sessions"""
        return len(self.sessions)
    
    def build_ai_context(self, chat_id: str, include_history: bool = True, history_limit: int = 10) -> Dict[str, Any]:
        """
        Build comprehensive AI context from memory - no database queries needed.
        This replaces all the complex DynamoDB session merging logic.
        """
        session = self.get_session(chat_id)
        
        context = {
            "extracted_data": session["extracted_data"],
            "generation_state": session["generation_state"],
            "generated_content": session["generated_content"],
            "conversation_stage": session["generation_state"].get("conversation_stage", "greeting"),
            "has_generated_content": session["generation_state"].get("has_generated", False),
            "message_count": session["metadata"]["message_count"]
        }
        
        if include_history:
            context["conversation_history"] = self.get_conversation_history(chat_id, history_limit)
        
        return context

# Global instance - survives for Lambda execution lifetime
memory_store = InMemorySessionStore()