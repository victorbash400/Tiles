import asyncio
import httpx
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from prompt_service import prompt_service
from data_collection_service import data_collection_service
from unsplash_service import UnsplashService
from qloo_music_service import QlooMusicService
from qloo_venue_service import QlooVenueService
from qloo_food_service import QlooFoodService
from memory_store import memory_store

load_dotenv()

class AIService:
    """Simple GPT-4 chat responses and Azure DALL-E 3 image generation"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        if not self.openai_api_key:
            print("⚠️  OpenAI API key not found")
        if not self.azure_api_key or not self.azure_endpoint:
            print("⚠️  Azure DALL-E 3 credentials not found")
            
        print("Initialized AI service with GPT-4.1 nano and Azure DALL-E 3")
    
    def _get_context_limit_for_model(self, model_name: str) -> int:
        """Get appropriate context limit based on model capabilities"""
        model_limits = {
            "gpt-3.5-turbo": 100,      # 4K tokens ~100 messages
            "gpt-4o-mini": 3000,       # 128K tokens ~3000 messages
            "gpt-4.1-nano": 25000,     # 1M tokens ~25000 messages
            "gpt-4": 2000,             # 8K tokens ~2000 messages
            "gpt-4-32k": 8000,         # 32K tokens ~8000 messages
        }
        return model_limits.get(model_name, 100)  # Default to conservative limit
    
    async def generate_event_response(self, user_message: str, user_preferences: Dict = None, conversation_history: List = None, memory_context: Dict = None) -> Dict[str, Any]:
        """Generate event planning response"""
        
        # **NEW**: Check generation status from memory context
        has_generated_content = False
        session_extracted_data = {}
        
        if memory_context:
            has_generated_content = memory_context.get("has_generated_content", False)
            session_extracted_data = memory_context.get("extracted_data", {})
            
            print(f"🔍 Content generation status: has_generated_content={has_generated_content}")
            if session_extracted_data:
                print(f"🧠 Found {len(session_extracted_data)} fields in memory")
                for field, value in session_extracted_data.items():
                    print(f"   {field}: {value}")
        
        # Get the appropriate prompt based on generation state
        prompt = data_collection_service.get_data_collection_prompt(has_generated_content)
        
        if not self.openai_api_key:
            return {
                "message": "Hey there! 👋 I'm so excited to help you plan something special! What kind of event are you thinking about? 🎊",
                "suggestions": {},
                "questions": [],
                "ready_to_generate": False,
                "confidence": 0.5
            }
        
        try:
            messages = [{"role": "system", "content": prompt}]
            
            # Add conversation history - dynamic limits based on model capability
            if conversation_history:
                model_name = "gpt-4.1-nano"  # Current model used in this service
                max_messages = self._get_context_limit_for_model(model_name)
                recent_history = conversation_history[-max_messages:] if len(conversation_history) > max_messages else conversation_history
                messages.extend(recent_history)
                print(f"📝 Context: Using {len(recent_history)} messages (max: {max_messages} for {model_name})")
            
            # Add the current message
            messages.append({"role": "user", "content": user_message})
            
            # Reduced logging: only show message count
            print(f"🧠 AI context: {len(messages)} messages including current")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4.1-nano",  # Cheapest, fastest, 1M context window
                        "messages": messages,
                        "response_format": {"type": "json_object"},
                        "temperature": 0.7,  # Balanced for speed and creativity
                        "max_tokens": 300  # Reduced for faster response
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    try:
                        result = json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"❌ JSON parsing error: {e}")
                        print(f"Raw content: {content}")
                        # Fallback response when JSON fails
                        result = {
                            "message": "Let me help you plan your event! Can you tell me more about what you have in mind?",
                            "suggestions": {},
                            "ready_to_generate": False,
                            "missing_requirements": ["event_type", "location", "guest_count", "budget", "meal_type", "dietary_restrictions"],
                            "conversation_stage": "collecting_basics"
                        }
                    
                    # Use DataCollectionService to analyze and enhance the response
                    suggestions = result.get("suggestions", {})
                    
                    # **NEW**: Merge memory data with AI suggestions to prevent memory loss
                    if session_extracted_data:
                        # Merge memory data with AI suggestions, prioritizing existing memory data
                        for field, value in session_extracted_data.items():
                            if field not in suggestions or suggestions[field] is None:
                                suggestions[field] = value
                                print(f"🧠 Restored from memory: {field} = {value}")
                        
                        # Update the result with merged suggestions
                        result["suggestions"] = suggestions
                    
                    # Check if PDF generation was requested
                    if suggestions.get("action_requested") == "generate_pdf":
                        result["pdf_requested"] = True
                        result["message"] = "Perfect! I'll generate a comprehensive event plan PDF for you right away! 📋✨"
                    
                    # **NEW**: Get generation state from memory context
                    generation_state = memory_context.get("generation_state", {}) if memory_context else {}
                    
                    # Check if we're in a confirmation state from previous turn
                    awaiting_confirmation = generation_state.get("awaiting_confirmation", False)
                    user_confirmed_generation = generation_state.get("user_confirmed_generation", False)
                    
                    # Analyze conversation completeness using memory context
                    memory_session_context = {"extracted_data": session_extracted_data, **generation_state}
                    analysis = data_collection_service.analyze_conversation_completeness(suggestions, has_generated_content, memory_session_context)
                    
                    # Add analysis data to result
                    result.update(analysis)
                    print(f"🔍 AI flow: has_generated={has_generated_content}, stage={result.get('conversation_stage')}, awaiting_confirmation={result.get('awaiting_confirmation')}")
                    
                    # Override with session state if available or if analysis says to await confirmation
                    if awaiting_confirmation or result.get("awaiting_confirmation", False):
                        result["awaiting_confirmation"] = True
                        result["ready_to_generate"] = False
                    
                    # Handle post-generation conversation flow FIRST (higher priority)
                    if result.get("conversation_stage") == "reviewing_content":
                        print("🎯 Entering reviewing_content stage")
                        # User is reviewing generated content - ask for preferences and offer PDF
                        result["message"] = "🎉 Great! I've generated your event recommendations. Take a look at the images, music, venues, and food suggestions I've created for you.\n\nWhich ones catch your eye? Do any of the venues or styles look perfect for your event? Once you've had a chance to review everything, I can create a detailed PDF plan with your favorites! Would you like me to create a comprehensive event plan PDF for you?"
                        result["awaiting_pdf_confirmation"] = True
                        result["ready_to_generate"] = False
                    
                    elif result.get("conversation_stage") == "awaiting_pdf_confirmation":
                        print("🎯 Checking PDF confirmation")
                        # Check if user confirmed PDF generation
                        pdf_confirmed = await data_collection_service.detect_pdf_confirmation(user_message)
                        if pdf_confirmed:
                            result["pdf_confirmed"] = True
                            result["message"] = "Perfect! I'll create a detailed PDF plan for your event with all the recommendations. This will include timelines, checklists, and all the curated suggestions! 📄✨"
                            result["conversation_stage"] = "pdf_generation"
                        else:
                            # User is giving preferences/feedback but not confirming PDF yet
                            result["message"] = "Thanks for the feedback! I can incorporate your preferences into the plan. When you're ready for a detailed PDF with your selected venues, music, and complete event timeline, just let me know! Would you like me to create the PDF plan now?"
                            result["awaiting_pdf_confirmation"] = True
                    
                    # Handle confirmation logic for initial generation (lower priority)
                    elif result.get("awaiting_confirmation") and not user_confirmed_generation:
                        print("🎯 Checking initial generation confirmation")
                        # Check if user confirmed generation using AI
                        user_confirmed = await data_collection_service.detect_user_confirmation(user_message)
                        if user_confirmed:
                            result["user_confirmed_generation"] = True
                            result["ready_to_generate"] = True
                            result["awaiting_confirmation"] = False
                            result["conversation_stage"] = "confirmed"
                            result["message"] = "Perfect! Let me generate your event recommendations now! 🎉✨"
                    
                    # Validate location if provided
                    if suggestions.get("location"):
                        location_validation = data_collection_service.validate_location(suggestions["location"])
                        if not location_validation["valid"]:
                            result["ready_to_generate"] = False
                            result["location_validation"] = location_validation
                    
                    # Auto-infer obvious settings
                    if result.get("suggestions", {}).get("event_type") == "wedding" and "beach" in user_message.lower():
                        result["suggestions"]["setting"] = "outdoor"
                    
                    # Add completion summary for debugging
                    result["completion_summary"] = data_collection_service.get_completion_summary(suggestions)
                    
                    # Ensure image_generation_prompt is present when ready_to_generate is True
                    if result.get("ready_to_generate") and not result.get("image_generation_prompt"):
                        # Generate image prompt from available data
                        event_type = suggestions.get("event_type", "party")
                        location = suggestions.get("location", "")
                        style = suggestions.get("style", "")
                        colors = suggestions.get("colors", [])
                        
                        color_text = f" {', '.join(colors)} theme" if colors else ""
                        style_text = f" {style}" if style else ""
                        
                        result["image_generation_prompt"] = f"{event_type} in {location}{style_text}{color_text}"
                    
                    return result
                else:
                    print(f"OpenAI API error: {response.status_code}")
                    return {
                        "message": "Oops! 😅 Had a little hiccup there. Tell me about your event!",
                        "ready_to_generate": False
                    }
                    
        except Exception as e:
            print(f"Error: {str(e)}")
            return {
                "message": "Sorry about that! 😊 Let's try again - what kind of event are you planning?",
                "ready_to_generate": False
            }
    
    async def generate_event_images(self, event_prompt: str, suggestions: Dict = None, conversation_context: Dict = None) -> List[Dict]:
        """Generate 3 different themed images for event inspiration using Prompt Service"""
        
        if not self.azure_api_key or not self.azure_endpoint:
            print("❌ Azure DALL-E 3 not configured")
            return []
        
        # Use Prompt Engineering Service to generate targeted prompts
        event_context = {
            "event_type": suggestions.get("event_type", "party") if suggestions else "party",
            "raw_prompt": event_prompt
        }
        
        # Add conversation context if available
        if conversation_context:
            event_context.update(conversation_context)
        
        # Generate 3 different perspective prompts
        prompts = prompt_service.generate_image_prompts(event_context, suggestions or {})
        
        # Generate images
        images = []
        for i, prompt in enumerate(prompts):
            try:
                print(f"🎨 Generating image {i+1} with prompt: {prompt[:100]}...")
                image = await self._generate_single_image(prompt, i)
                if image:
                    images.append(image)
                    print(f"✅ Generated image {i+1}/3")
                else:
                    print(f"❌ Failed image {i+1}/3")
                
                # Rate limit delay
                if i < 2:
                    await asyncio.sleep(2)
                    
            except Exception as e:
                print(f"❌ Error generating image {i+1}: {str(e)}")
        
        print(f"✅ Generated {len(images)} event images")
        return images
    
    async def get_comprehensive_recommendations(self, event_data: Dict, suggestions: Dict = None) -> Dict:
        """Get comprehensive event recommendations using multiple services"""
        event_type = event_data.get("event_type", "party")
        location = event_data.get("location", "")
        style_preferences = suggestions or {}
        
        # Get recommendations in parallel
        music_results = await self._get_music_recommendations(
            event_type, style_preferences, count=3
        )
        
        venue_results = await self._get_venue_recommendations(
            event_type, location, budget=style_preferences.get("budget"), count=6
        )
        
        food_results = await self._get_food_recommendations(
            event_type, location, style_preferences, count=5
        )
        
        return {
            "music": music_results,
            "venues": venue_results,
            "food": food_results,
            "total_recommendations": len(music_results) + len(venue_results) + len(food_results)
        }
    
    async def _get_music_recommendations(self, event_type: str, style_preferences: Dict = None, count: int = 5) -> List[Dict]:
        """Get playlist recommendations using QlooMusicService with enhanced context"""
        try:
            music_service = QlooMusicService()
            return await music_service.get_music_recommendations(event_type, style_preferences, count)
        except Exception as e:
            print(f"Music service error: {str(e)}")
            return []
    
    async def _get_venue_recommendations(self, event_type: str, location: str = None, budget: str = None, count: int = 6) -> List[Dict]:
        """Get venue recommendations using QlooVenueService"""
        try:
            venue_service = QlooVenueService()
            return await venue_service.get_venue_recommendations(event_type, location, budget, count)
        except Exception as e:
            print(f"Venue service error: {str(e)}")
            return []
    
    async def _get_food_recommendations(self, event_type: str, location: str = None, style_preferences: Dict = None, count: int = 5) -> List[Dict]:
        """Get food recommendations using QlooFoodService"""
        try:
            food_service = QlooFoodService()
            
            # Extract food-specific preferences from style_preferences
            budget = style_preferences.get("budget") if style_preferences else None
            dietary_restrictions = style_preferences.get("dietary_restrictions", []) if style_preferences else []
            meal_type = style_preferences.get("meal_type") if style_preferences else None
            cuisine_preference = style_preferences.get("cuisine_preference") if style_preferences else None
            guest_count = style_preferences.get("guest_count") if style_preferences else None
            
            # Convert single dietary restriction to list
            if dietary_restrictions and not isinstance(dietary_restrictions, list):
                dietary_restrictions = [dietary_restrictions]
            
            return await food_service.get_food_recommendations(
                event_type=event_type,
                location=location,
                budget=budget,
                dietary_restrictions=dietary_restrictions,
                meal_type=meal_type,
                cuisine_preference=cuisine_preference,
                guest_count=guest_count,
                count=count
            )
        except Exception as e:
            print(f"Food service error: {str(e)}")
            return []
    
    async def _generate_single_image(self, prompt: str, index: int) -> Dict:
        """Generate single image with Azure DALL-E 3"""
        
        try:
            url = f"{self.azure_endpoint}/openai/deployments/dall-e-3/images/generations?api-version=2024-02-01"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={
                        "api-key": self.azure_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "prompt": prompt,
                        "size": "1024x1024",
                        "n": 1,
                        "quality": "standard",
                        "style": "natural"
                    },
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get("data") and len(data["data"]) > 0:
                        image_url = data["data"][0].get("url")
                        if image_url:
                            return {
                                "id": f"dalle_{index}_{hash(prompt) % 10000}",
                                "type": "generated",
                                "platform": "azure_dalle",
                                "urls": {
                                    "regular": image_url,
                                    "small": image_url,
                                    "thumb": image_url
                                },
                                "user": {"name": "Azure DALL-E 3"},
                                "height": 1024,
                                "width": 1024,
                                "alt_description": prompt,
                                "prompt": prompt
                            }
                else:
                    error_text = response.text
                    print(f"❌ Azure API error: {response.status_code} - {error_text}")
                    
        except Exception as e:
            print(f"❌ Azure DALL-E 3 error: {str(e)}")
            
        return None

