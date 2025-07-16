import asyncio
import re
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from database import (
    ChatSession, PlanSession, UserMemory,
    get_or_create_plan_session, update_plan_state, get_plan_progress,
    store_user_preference, get_user_preferences
)
from ai_services import AIService
from prompt_service import prompt_service
from data_collection_service import data_collection_service

class EventService:
    """Handles event planning logic and AI coordination"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    async def process_message_and_generate_response(
        self, 
        chat_id: str, 
        message_content: str, 
        session: ChatSession, 
        conversation_history: List[Dict],
        db: Session
    ) -> Dict[str, Any]:
        """Process user message and generate AI response with content generation"""
        
        # Each chat gets its own isolated user session
        user_session = f"chat_{chat_id}"
        session.user_session = user_session
        
        # Get or create plan session for state management
        plan_session = get_or_create_plan_session(db, session.id)
        
        # Build plan context
        plan_context = {
            "plan_status": plan_session.plan_status,
            "message_count": len(session.messages)
        }
        
        # Generate AI response
        ai_response = await self._generate_ai_response(
            message_content, conversation_history, plan_context
        )
        
        # Generate content if ready
        generated_content = await self._generate_event_content(
            ai_response, conversation_history, message_content
        )
        
        # Update plan state if content was generated
        if generated_content["has_content"]:
            content_data = {
                "images": generated_content["images"],
                "music": generated_content["music"],
                "venues": generated_content["venues"],
                "generation_prompt": ai_response.get("image_generation_prompt", ""),
                "suggestions": ai_response.get("suggestions", {})
            }
            update_plan_state(db, plan_session, "reviewing", generated_content=content_data)
            print(f"💾 Saved generated content to plan session")
        
        # Prepare AI suggestions
        ai_suggestions = {
            "suggestions": ai_response.get("suggestions", {}),
            "questions": ai_response.get("questions", []),
            "ready_to_generate": ai_response.get("ready_to_generate", False),
            "generation_status": "Generated and saved to gallery" if generated_content["has_content"] else "No generation requested",
            "refresh_gallery": generated_content["has_content"],
            "generated_count": generated_content["total_count"],
            "plan_status": plan_session.plan_status,
            "plan_progress": get_plan_progress(db, session.id)["progress"],
            "music_data": ai_response.get("music_data", []),
            "venue_data": ai_response.get("venue_data", [])
        }
        
        return {
            "ai_response": ai_response,
            "ai_suggestions": ai_suggestions
        }
    
    async def _generate_ai_response(self, message_content: str, conversation_history: List[Dict], plan_context: Dict) -> Dict:
        """Generate AI response with timeout handling"""
        if not self.ai_service:
            return await self._fallback_response(message_content, conversation_history)
        
        try:
            return await asyncio.wait_for(
                self.ai_service.generate_event_response(
                    message_content,
                    {},  # No cross-chat preferences
                    conversation_history,
                    plan_context
                ),
                timeout=60.0
            )
        except asyncio.TimeoutError:
            print("AI response generation timed out")
            return {
                "message": "I'm still thinking about your event. Please provide more details or try again.",
                "suggestions": {},
                "ready_to_generate": False,
                "confidence": 0.0
            }
        except Exception as e:
            print(f"AI response generation error: {str(e)}")
            return {
                "message": "I encountered an error processing your request. Please try again.",
                "suggestions": {},
                "ready_to_generate": False,
                "confidence": 0.0
            }
    
    
    def _analyze_conversation_context_basic(self, conversation_text: str) -> tuple:
        """Analyze conversation to extract event context"""
        conversation_lower = conversation_text.lower()
        
        # Determine event type
        if "wedding" in conversation_lower:
            return "wedding", ["white", "ivory", "gold"], "romantic"
        elif "birthday" in conversation_lower:
            return "birthday", ["pink", "gold", "white"], "celebration"
        else:
            return "party", ["pink", "gold", "white"], "celebration"
    
    def _extract_location_basic(self, conversation_text: str) -> str:
        """AI handles location extraction better - using fallback only"""
        # Simple fallback - AI in data_collection_service does the heavy lifting
        return ""
    
    async def _generate_event_content(self, ai_response: Dict, conversation_history: List[Dict], message_content: str) -> Dict:
        """Generate event content (images, music, venues) if conditions are met"""
        suggestions = ai_response.get("suggestions", {})
        
        # Check ALL mandatory fields from data collection service
        mandatory_fields = {
            "event_type": "event type",
            "location": "location (city + country)",
            "guest_count": "number of guests", 
            "budget": "budget or style preference",
            "meal_type": "meal type",
            "dietary_restrictions": "dietary restrictions"
        }
        
        missing_fields = []
        for field, description in mandatory_fields.items():
            value = suggestions.get(field)
            is_valid = False
            
            if field == "guest_count":
                # Guest count must be a positive integer - convert string numbers
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                    suggestions[field] = value  # Update the original value
                is_valid = isinstance(value, (int, float)) and value > 0
            elif field == "dietary_restrictions":
                # Dietary restrictions can be empty array, string "none", or actual restrictions
                is_valid = (
                    isinstance(value, list) or 
                    (isinstance(value, str) and len(value.strip()) >= 2) or
                    value == "none"
                )
            else:
                # Other fields must be non-empty strings and not "unspecified"
                is_valid = (value and isinstance(value, str) and len(value.strip()) >= 2 and 
                           value.strip().lower() != "unspecified")
            
            if not is_valid:
                missing_fields.append(description)
                print(f"❌ Field '{field}' invalid: {value} (type: {type(value)})")
            else:
                print(f"✅ Field '{field}' valid: {value}")
        
        # Special validation for location - must be specific
        location = suggestions.get("location", "")
        has_specific_location = location and len(location) > 3 and not any(generic in location.lower() for generic in ["venue", "place", "somewhere", "anywhere"])
        
        if not has_specific_location:
            missing_fields.append("specific location (city + country)")
        
        ai_ready = ai_response.get("ready_to_generate", False)
        all_fields_complete = len(missing_fields) == 0
        
        print(f"🔍 Generation check: AI ready={ai_ready}, all_fields_complete={all_fields_complete}")
        if missing_fields:
            print(f"⚠️ Missing mandatory fields: {missing_fields}")
        
        if not (ai_ready and ai_response.get("image_generation_prompt") and all_fields_complete):
            if ai_ready and not all_fields_complete:
                print(f"⚠️ AI wanted to generate but missing: {missing_fields}")
                ai_response["message"] = f"I need a few more details to create the perfect event for you! 🎯 Please tell me: {', '.join(missing_fields[:3])}"
                ai_response["ready_to_generate"] = False
            return {"images": [], "music": [], "venues": [], "food": [], "has_content": False, "total_count": 0}
        
        try:
            print(f"🎨 User requested generation: {ai_response['image_generation_prompt']}")
            
            # Generate images using AI service with conversation context
            generated_images = []
            generated_music = []
            generated_venues = []
            
            if self.ai_service:
                # Use AI-powered conversation analysis for better data extraction
                conversation_context = await data_collection_service.analyze_conversation_with_ai(conversation_history, message_content)
                
                # Use AI-extracted location - it's smarter than regex
                final_location = suggestions.get("location", "")
                
                # Fallback to conversation context if AI didn't extract location
                if not final_location or final_location == "null":
                    final_location = conversation_context.get("location", "")
                
                # Final fallback
                if not final_location or final_location == "null":
                    final_location = "location not specified"
                
                print(f"🎯 Final location used: '{final_location}'")
                
                conversation_context.update({
                    "event_type": suggestions.get("event_type", "party"),
                    "location": final_location,
                    "user_message": message_content
                })
                
                # Generate images
                generated_images = await asyncio.wait_for(
                    self.ai_service.generate_event_images(
                        ai_response["image_generation_prompt"],
                        suggestions,
                        conversation_context
                    ),
                    timeout=120.0
                )
                print(f"✅ Generated {len(generated_images)} images for gallery")
                
                # Get music and venue recommendations
                if has_specific_location:
                    recommendations = await self.ai_service.get_comprehensive_recommendations(
                        {"event_type": suggestions.get("event_type", "party"), "location": final_location},
                        suggestions
                    )
                    generated_music = recommendations.get("music", [])
                    generated_venues = recommendations.get("venues", [])
                    print(f"✅ Generated {len(generated_music)} music tracks and {len(generated_venues)} venues")
            
            total_count = len(generated_images) + len(generated_music) + len(generated_venues)
            return {
                "images": generated_images,
                "music": generated_music,
                "venues": generated_venues,
                "has_content": total_count > 0,
                "total_count": total_count
            }
            
        except asyncio.TimeoutError:
            print("Content generation timed out")
            return {"images": [], "music": [], "venues": [], "has_content": False, "total_count": 0}
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return {"images": [], "music": [], "venues": [], "has_content": False, "total_count": 0}
    
    def get_ai_memory(self, user_session: str, db: Session) -> Dict:
        """Get AI memory/personalization data for isolated chats"""
        # Return simplified response for isolated chats
        return {
            "summary": "Each chat is independent - no shared memory across conversations",
            "active_monitoring": ["Fresh start", "Event planning", "Creative ideas"],
            "plan_status": "ready",
            "satisfaction_score": 1.0,
            "completion_confidence": 1.0
        }

def create_event_service(ai_service: AIService) -> EventService:
    """Factory function to create event service"""
    return EventService(ai_service)