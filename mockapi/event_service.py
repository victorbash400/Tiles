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
            return self._fallback_response(message_content, conversation_history)
        
        try:
            return await asyncio.wait_for(
                self.ai_service.generate_event_response(
                    message_content,
                    {},  # No cross-chat preferences
                    conversation_history,
                    plan_context
                ),
                timeout=15.0
            )
        except asyncio.TimeoutError:
            print("AI response generation timed out")
            return self._fallback_response(message_content, conversation_history)
        except Exception as e:
            print(f"AI response generation error: {str(e)}")
            return self._fallback_response(message_content, conversation_history)
    
    def _fallback_response(self, message_content: str, conversation_history: List[Dict]) -> Dict:
        """Generate fallback response when AI service fails"""
        conversation_text = " ".join([msg.get("content", "") for msg in conversation_history]) + " " + message_content
        
        # Infer event type and details from conversation
        event_type, colors, style = self._analyze_conversation_context(conversation_text)
        location = self._extract_location_from_conversation(conversation_text)
        
        return {
            "message": f"I'm creating your beautiful {event_type} inspiration! Let me generate some amazing ideas for you.",
            "suggestions": {
                "event_type": event_type,
                "style": style,
                "colors": colors,
                "mood": "joyful",
                "location": location
            },
            "ready_to_generate": True,
            "image_generation_prompt": f"{event_type} {location} {' '.join(colors)} theme",
            "confidence": 0.8
        }
    
    def _analyze_conversation_context(self, conversation_text: str) -> tuple:
        """Analyze conversation to extract event context"""
        conversation_lower = conversation_text.lower()
        
        # Determine event type
        if "wedding" in conversation_lower:
            return "wedding", ["white", "ivory", "gold"], "romantic"
        elif "birthday" in conversation_lower:
            return "birthday", ["pink", "gold", "white"], "celebration"
        else:
            return "party", ["pink", "gold", "white"], "celebration"
    
    def _extract_location_from_conversation(self, conversation_text: str) -> str:
        """Extract location with improved patterns"""
        known_places = [
            'hawaii', 'california', 'florida', 'new york', 'texas', 'chicago', 
            'miami', 'los angeles', 'brooklyn', 'manhattan', 'boston', 'seattle',
            'denver', 'atlanta', 'vegas', 'las vegas', 'san francisco', 'san diego',
            'philadelphia', 'washington', 'dc', 'maryland', 'virginia', 'nairobi',
            'kenya', 'mombasa', 'kisumu'
        ]
        
        # Location correction map
        location_corrections = {
            'hawwai': 'Hawaii',
            'hawai': 'Hawaii',
            'californa': 'California',
            'flordia': 'Florida',
            'chigago': 'Chicago'
        }
        
        # Look for specific geographic location patterns
        specific_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',
            r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',
        ]
        
        for pattern in specific_patterns:
            matches = re.findall(pattern, conversation_text, re.IGNORECASE)
            for match in matches:
                extracted_location = match.strip()
                if 2 < len(extracted_location) < 30:
                    location_lower = extracted_location.lower()
                    if any(place in location_lower for place in known_places):
                        return extracted_location.title()
        
        # Fallback to direct keyword matching
        for place in known_places:
            if place in conversation_text.lower():
                corrected_location = location_corrections.get(place, place.title())
                return corrected_location
        
        return ""
    
    async def _generate_event_content(self, ai_response: Dict, conversation_history: List[Dict], message_content: str) -> Dict:
        """Generate event content (images, music, venues) if conditions are met"""
        suggestions = ai_response.get("suggestions", {})
        has_specific_location = suggestions.get("location") and len(suggestions.get("location", "")) > 3
        ai_ready = ai_response.get("ready_to_generate", False)
        
        print(f"🔍 Generation check: AI ready={ai_ready}, has_location={has_specific_location}, location='{suggestions.get('location', '')}'")
        
        if not (ai_ready and ai_response.get("image_generation_prompt") and has_specific_location):
            if ai_ready and not has_specific_location:
                print(f"⚠️ AI wanted to generate but location '{suggestions.get('location', '')}' is insufficient")
                ai_response["message"] = "I need more specific details! 🎯 Please tell me the exact city and country for your event so I can find the perfect venues and create amazing inspiration for you!"
                ai_response["ready_to_generate"] = False
            return {"images": [], "music": [], "venues": [], "has_content": False, "total_count": 0}
        
        try:
            print(f"🎨 User requested generation: {ai_response['image_generation_prompt']}")
            
            # Generate images using AI service with conversation context
            generated_images = []
            generated_music = []
            generated_venues = []
            
            if self.ai_service:
                # Extract conversation context for prompt service
                conversation_context = prompt_service.analyze_conversation_context(conversation_history, message_content)
                
                # Determine final location
                ai_location = suggestions.get("location", "")
                conversation_location = conversation_context.get("location", "")
                final_location = conversation_location if conversation_location else ai_location
                
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