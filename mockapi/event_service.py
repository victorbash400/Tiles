import asyncio
import re
from typing import Dict, List, Any
# from sqlalchemy.orm import Session
from dynamodb_database import (
    ChatSession, ChatMessage, PlanSession, UserMemory,
    get_or_create_plan_session, update_plan_state, get_plan_progress,
    store_user_preference, get_user_preferences
)
from ai_services import AIService
from prompt_service import prompt_service
from data_collection_service import data_collection_service
from memory_store import memory_store

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
        db
    ) -> Dict[str, Any]:
        """Process user message and generate AI response with content generation"""
        
        # **NEW**: Use in-memory store instead of complex DynamoDB queries
        # Add message to conversation history
        memory_store.add_conversation_message(chat_id, "user", message_content)
        
        # Build AI context directly from memory (no database queries)
        ai_context = memory_store.build_ai_context(chat_id, include_history=True, history_limit=25)
        
        # Legacy: Still get plan session for database persistence (optional)
        plan_session = get_or_create_plan_session(db, session.id)
        
        # Generate AI response using in-memory context
        ai_response = await self._generate_ai_response(
            message_content, ai_context["conversation_history"], ai_context
        )
        
        # **NEW**: Store extracted data directly in memory (instant access, no database delays)
        suggestions = ai_response.get("suggestions", {})
        if suggestions:
            # Store ALL AI suggestions in memory for immediate access
            memory_store.update_extracted_data(chat_id, suggestions)
            
            # Update generation state
            generation_updates = {}
            for state_field in ["awaiting_confirmation", "user_confirmed_generation", "conversation_stage"]:
                if state_field in ai_response:
                    generation_updates[state_field] = ai_response[state_field]
            
            if generation_updates:
                memory_store.update_generation_state(chat_id, generation_updates)
        
        # Generate content if ready using memory context
        generated_content = await self._generate_event_content(
            ai_response, ai_context["conversation_history"], message_content, chat_id
        )
        
        # **NEW**: Store generated content in memory for instant access
        if generated_content["has_content"]:
            # Store each content type in memory
            for content_type in ["images", "music", "venues", "food"]:
                if generated_content[content_type]:
                    memory_store.store_generated_content(chat_id, content_type, generated_content[content_type])
            
            # Update generation state
            memory_store.update_generation_state(chat_id, {
                "has_generated": True,
                "conversation_stage": "reviewing_content"
            })
        
        # **NEW**: Build AI suggestions from memory data
        current_memory = memory_store.get_session_summary(chat_id)
        
        # **DISABLE AUTO-REFRESH AFTER FIRST GENERATION**
        # Once content is generated, no more auto-refresh - user can manually refresh
        has_already_generated = current_memory["generation_state"].get("has_generated", False)
        refresh_gallery_value = generated_content["has_content"] and not has_already_generated
        
        ai_suggestions = {
            "suggestions": ai_response.get("suggestions", {}),
            "questions": ai_response.get("questions", []),
            "ready_to_generate": ai_response.get("ready_to_generate", False),
            "generation_status": "Generated and saved to gallery" if generated_content["has_content"] else "No generation requested",
            "refresh_gallery": refresh_gallery_value,
            "generated_count": generated_content["total_count"],
            "plan_status": "reviewing" if current_memory["generation_state"]["has_generated"] else "discovering",
            "plan_progress": current_memory["generation_state"].get("has_generated", False) * 1.0,
            "image_data": generated_content["images"],
            "music_data": generated_content["music"],
            "venue_data": generated_content["venues"],
            "food_data": generated_content["food"],
            "pdf_requested": ai_response.get("pdf_requested", False)
        }
        
        # Store AI suggestions in memory for next request
        memory_store.store_ai_suggestions(chat_id, ai_suggestions)
        
        print(f"📤 AI suggestions being sent to frontend:")
        print(f"   - refresh_gallery: {ai_suggestions['refresh_gallery']}")
        print(f"   - image_data: {len(ai_suggestions['image_data'])} items")
        print(f"   - music_data: {len(ai_suggestions['music_data'])} items")
        print(f"   - venue_data: {len(ai_suggestions['venue_data'])} items")
        print(f"   - food_data: {len(ai_suggestions['food_data'])} items")
        
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
    
    async def _generate_event_content(self, ai_response: Dict, conversation_history: List[Dict], message_content: str, chat_id: str) -> Dict:
        """Generate event content (images, music, venues) if conditions are met"""
        # **NEW**: Get all data from memory instead of just AI response
        memory_data = memory_store.get_extracted_data(chat_id)
        generation_state = memory_store.get_generation_state(chat_id)
        
        # Merge AI suggestions with memory data (memory has priority for existing fields)
        suggestions = ai_response.get("suggestions", {})
        for field, value in memory_data.items():
            if value is not None and (field not in suggestions or suggestions[field] is None):
                suggestions[field] = value
        
        # **FLEXIBLE**: Let AI determine completeness instead of hardcoded validation
        completeness_check = memory_store.check_data_completeness(chat_id)
        
        # Simplified completion check - only 3 essentials needed
        has_essential_data = (
            suggestions.get("event_type") and 
            suggestions.get("location") and 
            suggestions.get("guest_count")  # Just the 3 core fields
        )
        
        # Check if we're in post-generation phase (prevent double generation)
        conversation_stage = generation_state.get("conversation_stage", "")
        if generation_state.get("has_generated", False) or conversation_stage in ["reviewing_content", "awaiting_pdf_confirmation", "pdf_generation"]:
            print(f"🚫 Skipping generation - already generated or in post-generation phase: {conversation_stage}")
            # Return existing generated content from memory instead of empty arrays
            existing_content = memory_store.get_generated_content(chat_id)
            total_count = sum(len(existing_content.get(content_type, [])) for content_type in ["images", "music", "venues", "food"])
            return {
                "images": existing_content.get("images", []),
                "music": existing_content.get("music", []),
                "venues": existing_content.get("venues", []),
                "food": existing_content.get("food", []),
                "has_content": total_count > 0,
                "total_count": total_count
            }
        
        ai_ready = ai_response.get("ready_to_generate", False)
        user_confirmed = generation_state.get("user_confirmed", False) or ai_response.get("user_confirmed_generation", False)
        
        print(f"🔍 Generation check: AI ready={ai_ready}, has_essential_data={has_essential_data}, user_confirmed={user_confirmed}")
        print(f"📊 Memory completeness: {completeness_check['field_count']} fields, score: {completeness_check['completeness_score']:.1f}")
        
        if not (ai_ready and ai_response.get("image_generation_prompt") and has_essential_data and user_confirmed):
            if ai_ready and not has_essential_data:
                print(f"⚠️ AI wanted to generate but missing essential data")
                ai_response["message"] = f"I need a few more details to create the perfect event for you! 🎯 Can you tell me more about your event?"
                ai_response["ready_to_generate"] = False
            elif ai_ready and has_essential_data and not user_confirmed:
                print(f"⚠️ Essential data complete but user hasn't confirmed generation")
                ai_response["message"] = "I have your event details! Would you like me to generate your personalized recommendations now? Just say 'yes' or 'go ahead' to start! 🎉"
                ai_response["ready_to_generate"] = False
                ai_response["awaiting_confirmation"] = True
            return {"images": [], "music": [], "venues": [], "food": [], "has_content": False, "total_count": 0}
        
        try:
            print(f"🎨 User requested generation: {ai_response['image_generation_prompt']}")
            
            # Generate images using AI service with conversation context
            generated_images = []
            generated_music = []
            generated_venues = []
            
            if self.ai_service:
                # **NEW**: Use memory data instead of session context
                conversation_context = await data_collection_service.analyze_conversation_with_ai(
                    conversation_history, message_content, memory_data
                )
                
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
                
                # Generate images (with error handling to not block other services)
                try:
                    generated_images = await asyncio.wait_for(
                        self.ai_service.generate_event_images(
                            ai_response["image_generation_prompt"],
                            suggestions,
                            conversation_context
                        ),
                        timeout=60.0
                    )
                    print(f"✅ Generated {len(generated_images)} images for gallery")
                except Exception as e:
                    print(f"⚠️ Image generation failed: {str(e)}")
                    generated_images = []
                
                # Get music and venue recommendations (always run these if we have location)
                if final_location and len(final_location) > 3:
                    recommendations = await self.ai_service.get_comprehensive_recommendations(
                        {"event_type": suggestions.get("event_type", "party"), "location": final_location},
                        suggestions
                    )
                    generated_music = recommendations.get("music", [])
                    generated_venues = recommendations.get("venues", [])
                    generated_food = recommendations.get("food", [])
                    print(f"✅ Generated {len(generated_music)} music tracks, {len(generated_venues)} venues, and {len(generated_food)} food items")
            
            total_count = len(generated_images) + len(generated_music) + len(generated_venues) + len(generated_food)
            return {
                "images": generated_images,
                "music": generated_music,
                "venues": generated_venues,
                "food": generated_food,
                "has_content": total_count > 0,
                "total_count": total_count
            }
            
        except asyncio.TimeoutError:
            print("Content generation timed out")
            return {"images": [], "music": [], "venues": [], "food": [], "has_content": False, "total_count": 0}
        except Exception as e:
            print(f"Error generating content: {str(e)}")
            return {"images": [], "music": [], "venues": [], "food": [], "has_content": False, "total_count": 0}
    
    def get_ai_memory(self, user_session: str, db) -> Dict:
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