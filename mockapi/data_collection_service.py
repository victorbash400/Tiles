#!/usr/bin/env python3
"""
Data Collection Service - Streamlined AI-powered event data collection
"""

import os
import httpx
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class DataCollectionService:
    """
    Streamlined event planning data collection using AI-powered extraction.
    No regex patterns - pure AI extraction with strict validation.
    """
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required for data collection service")
        
        print("✅ Initialized Streamlined Data Collection Service (AI-only)")
        
        # Core mandatory fields - minimal requirements for generation
        self.mandatory_fields = {
            "event_type": "Type of event",
            "location": "City and country", 
            "guest_count": "Number of guests"
        }
        
        # Optional fields that enhance the experience but aren't required
        self.optional_fields = {
            "budget": "Budget amount or style preference",
            "meal_type": "Meal service type",
            "dietary_restrictions": "Dietary needs",
            "date": "Event date or timeframe"
        }
    
    def get_data_collection_prompt(self, has_generated_content: bool = False) -> str:
        """
        Strict AI prompt that prevents placeholder values and ensures accurate extraction.
        Updates behavior based on whether content has been generated.
        """
        
        if has_generated_content:
            return """You are a warm, enthusiastic AI event planner! 🎉

CONTEXT: You have already generated event recommendations (images, music, venues, food) for the user's event.

CRITICAL: You MUST extract the event details from the conversation history for PDF generation and refinements to work properly.

POST-GENERATION BEHAVIOR:
1. Acknowledge the generated content and ask for feedback
2. Offer refinements: "How do you like the recommendations? Would you like me to adjust anything?"
3. Ask about specific changes: music style, venue type, food preferences, colors, etc.
4. Offer to generate a comprehensive event plan PDF based on their selections
5. Be ready to refine or regenerate based on their feedback

AVAILABLE ACTIONS:
- "refine_music": Adjust music recommendations
- "refine_venues": Change venue suggestions  
- "refine_food": Modify food recommendations
- "refine_style": Adjust colors/theme/style
- "generate_pdf": Create comprehensive event plan document
- "regenerate_all": Start fresh with new recommendations

PDF DETECTION: If user asks for PDF, document, plan, or similar words (like "pfd", "pdf", "document", "plan"), set action_requested to "generate_pdf"

REGENERATION CONFIRMATION: If user asks to regenerate, ask for confirmation before proceeding

RESPOND WITH JSON:
{
    "message": "Your warm response asking for feedback and offering refinements",
    "suggestions": {
        "has_generated": true,
        "action_requested": null or "specific action if user requests",
        "refinement_type": null or "music/venues/food/style/pdf",
        "refinement_details": null or "specific changes requested",
        "event_type": "extract from conversation history",
        "location": "extract from conversation history",
        "guest_count": "extract from conversation history",
        "budget": "extract from conversation history",
        "meal_type": "extract from conversation history",
        "dietary_restrictions": "extract from conversation history"
    },
    "ready_to_generate": false,
    "ready_to_refine": true,
    "conversation_stage": "post_generation_feedback"
}

REMEMBER: Focus on improving the existing recommendations based on user feedback!"""
        
        else:
            return """You are a warm, enthusiastic AI event planner! 🎉

CRITICAL RULES:
1. ONLY extract information that the user has EXPLICITLY stated
2. NEVER fill in placeholder values or ask about unnecessary details
3. If user hasn't mentioned something, leave that field as null
4. Be conversational and natural - don't interrogate with lists of questions
5. Accept flexible, casual responses (ranges, approximations, general locations)
6. Focus on the event vision, not rigid data collection

CONVERSATION FLOW:
- Greet warmly and understand their event vision
- Ask naturally about what's needed for recommendations
- Build on their excitement and ideas
- Don't ask for specific details unless crucial for generation
- When you have enough to create something amazing, ASK FOR CONFIRMATION

CONFIRMATION LOGIC:
- When you have the essentials (event type, general location, rough guest count): ready_to_generate = false, awaiting_confirmation = true
- Ask: "I have enough to create some amazing recommendations! Should I generate your personalized event ideas?"
- Only proceed with generation when user confirms

MINIMAL REQUIRED FIELDS (only ask if missing):
1. event_type - What kind of event they're planning
2. location - General area/city where it's happening  
3. guest_count - Rough idea of how many people (ranges/approximations OK)

OPTIONAL FIELDS (enhance experience but don't require):
- budget - Amount or style preference (luxury/budget/mid-range)
- meal_type - Food/drink needs if relevant to event
- dietary_restrictions - Only if they mention it
- date - Only if they want to mention it (don't ask specifically)

RESPOND WITH JSON:
{
    "message": "Your warm response and next question",
    "suggestions": {
        "event_type": null or "specific type if stated",
        "location": null or "area/city if stated",
        "guest_count": null or number/range if stated,
        "budget": null or "amount/style if mentioned",
        "meal_type": null or "meal type if mentioned",
        "dietary_restrictions": null or "restrictions/none if mentioned",
        "date": null or "timeframe if mentioned"
    },
    "ready_to_generate": false,
    "awaiting_confirmation": false (true when all fields complete),
    "user_confirmed_generation": false (true when user says yes to generate),
    "missing_requirements": ["list of fields still needed"],
    "conversation_stage": "greeting/collecting_basics/collecting_details/awaiting_confirmation/confirmed"
}

REMEMBER: Only extract what user EXPLICITLY said. No placeholders! Always ask for confirmation before generating!"""
    
    def analyze_conversation_completeness(self, suggestions: Dict[str, Any], has_generated_content: bool = False, session_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Strict validation ensuring no placeholder values pass through.
        Includes confirmation logic to prevent auto-generation.
        Respects generation state to prevent regeneration loops.
        """
        # **FIX**: Merge session extracted data with current suggestions to prevent memory loss
        if session_context and "extracted_data" in session_context:
            session_extracted_data = session_context["extracted_data"]
            # Merge session data with suggestions, prioritizing existing session data
            for field, value in session_extracted_data.items():
                if field not in suggestions or suggestions[field] is None:
                    suggestions[field] = value
                    print(f"🔄 Data completeness check - restored from session: {field} = {value}")
        
        # If content already exists, don't regenerate automatically
        if has_generated_content:
            return {
                "ready_to_generate": False,  # Never regenerate automatically
                "awaiting_confirmation": False,
                "user_confirmed_generation": False,
                "missing_requirements": [],
                "conversation_stage": "post_generation_feedback",
                "completion_percentage": 100
            }
        
        missing_mandatory = []
        
        for field in self.mandatory_fields:
            value = suggestions.get(field)
            is_valid = False
            
            if field == "guest_count":
                # More flexible guest count - accept ranges and approximations
                if isinstance(value, (int, float)):
                    is_valid = value > 0
                elif isinstance(value, str):
                    value_clean = value.strip().lower()
                    # Accept numbers, ranges like "10-15", "around 20", "about 50"
                    if any(word in value_clean for word in ["around", "about", "roughly", "approximately"]):
                        is_valid = True
                    elif "-" in value_clean or "to" in value_clean:
                        is_valid = True
                    elif value.isdigit():
                        suggestions[field] = int(value)
                        is_valid = int(value) > 0
                    elif any(char.isdigit() for char in value_clean):
                        is_valid = True  # Has some numbers, good enough
                    
            elif field == "location":
                # Much more flexible location - accept general areas
                if isinstance(value, str):
                    value_clean = value.strip()
                    # Just needs to be more than a few characters and not completely empty
                    is_valid = (
                        len(value_clean) >= 3 and
                        value_clean.lower() not in ["unspecified", "not specified", "tbd"]
                    )
                    
            elif field == "event_type":
                # Very flexible event type - just needs something meaningful
                if isinstance(value, str):
                    value_clean = value.strip()
                    is_valid = (
                        len(value_clean) >= 3 and
                        value_clean.lower() not in ["unspecified", "not specified", "tbd", "unknown", "event"]
                    )
            
            if not is_valid:
                missing_mandatory.append(field)
                # Reduced logging: only show invalid fields
                print(f"❌ Field '{field}' invalid: {value}")
            # Valid fields don't need logging unless debugging
        
        # Determine stage and confirmation logic
        stage = "greeting"
        awaiting_confirmation = False
        user_confirmed_generation = False
        ready_to_generate = False
        
        if suggestions.get("event_type"):
            if len(missing_mandatory) > 3:
                stage = "collecting_basics"
            elif len(missing_mandatory) > 0:
                stage = "collecting_details"
            else:
                # All fields complete - check for confirmation and post-generation flow
                session_ctx = session_context or {}
                awaiting_confirmation = session_ctx.get("awaiting_confirmation", False)
                user_confirmed_generation = session_ctx.get("user_confirmed_generation", False)
                
                # Check if content has already been generated
                if has_generated_content:
                    # Post-generation flow: reviewing content or awaiting PDF confirmation
                    if session_ctx.get("awaiting_pdf_confirmation", False):
                        stage = "awaiting_pdf_confirmation"
                        awaiting_confirmation = False
                        user_confirmed_generation = False
                        ready_to_generate = False
                    else:
                        stage = "reviewing_content"
                        awaiting_confirmation = False
                        user_confirmed_generation = False
                        ready_to_generate = False
                else:
                    # Pre-generation flow: collect data and confirm
                    if not awaiting_confirmation and not user_confirmed_generation:
                        stage = "awaiting_confirmation"
                        awaiting_confirmation = True
                    elif user_confirmed_generation:
                        stage = "confirmed"
                        ready_to_generate = True
                    else:
                        stage = "awaiting_confirmation"
        
        return {
            "ready_to_generate": ready_to_generate,
            "awaiting_confirmation": awaiting_confirmation,
            "user_confirmed_generation": user_confirmed_generation,
            "missing_requirements": missing_mandatory,
            "conversation_stage": stage,
            "completion_percentage": int(((6 - len(missing_mandatory)) / 6) * 100)
        }
    
    async def detect_user_confirmation(self, user_message: str) -> bool:
        """
        Use AI to detect if user is EXPLICITLY confirming to generate recommendations.
        Returns True ONLY if user explicitly confirmed, False otherwise.
        """
        try:
            response = await httpx.AsyncClient().post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system", 
                            "content": """You are analyzing whether a user message is confirming they want to generate event recommendations.

CONTEXT: The user has provided all their event details and the system asked "Would you like me to generate your recommendations now?"

TASK: Determine if the user's response is confirming they want generation to start.

CONFIRMATIONS (TRUE):
- "yes" / "yeah" / "yep"
- "go ahead" / "sure" / "okay" 
- "generate" / "create" / "start"
- "do it" / "proceed"
- Any message with words like "generate", "create", "start", "begin" in context of recommendations
- "generate i have confirmed begin generating" → TRUE
- "ok generate" → TRUE

NOT CONFIRMATIONS (FALSE):
- Providing more event details
- Asking questions about the event
- Giving requirements or preferences
- Messages that don't mention generation/confirmation

RULE: If the message contains confirmation words or generation intent, return TRUE.

Return ONLY: true or false"""
                        },
                        {
                            "role": "user",
                            "content": f"User message: '{user_message}'\n\nIs this EXPLICITLY confirming they want generation to start?"
                        }
                    ],
                    "temperature": 0,
                    "max_tokens": 10
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip().lower()
                confirmed = ai_response == "true"
                print(f"🤖 AI confirmation check: '{user_message[:50]}...' → AI says: '{ai_response}' → Confirmed: {confirmed}")
                return confirmed
            else:
                print(f"❌ AI confirmation check failed: {response.status_code} - defaulting to FALSE")
                return False
                
        except Exception as e:
            print(f"❌ AI confirmation check error: {str(e)} - defaulting to FALSE")
            return False
    
    async def detect_pdf_confirmation(self, user_message: str) -> bool:
        """
        Use AI to detect if user is confirming they want a PDF plan generated.
        Returns True ONLY if user explicitly confirmed PDF generation, False otherwise.
        """
        try:
            response = await httpx.AsyncClient().post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "system", 
                            "content": """You are analyzing whether a user message is confirming they want a PDF event plan generated.

CRITICAL: Be VERY strict. Only return TRUE if the user is clearly saying YES to PDF generation.

CONTEXT: The user has reviewed their event recommendations and the system asked "Would you like me to create a detailed PDF plan for your event?"

TASK: Determine if the user's response is EXPLICITLY confirming they want a PDF plan created.

EXPLICIT PDF CONFIRMATIONS (TRUE):
- "yes, create the PDF"
- "generate the plan"
- "make the PDF"
- "yes, I want the plan"
- "create it"
- "go ahead with the PDF"
- "generate the PDF plan"

NOT PDF CONFIRMATIONS (FALSE):
- "I like the music recommendations" (just feedback)
- "what venues do you recommend?" (asking questions)
- "the colors look good" (giving preferences)
- "can you change something?" (requesting modifications)
- "I prefer venue 2" (stating preferences)
- Any message just giving feedback or preferences

RULE: When in doubt, return FALSE. Only return TRUE for clear, explicit PDF confirmation.

Return ONLY: true or false"""
                        },
                        {
                            "role": "user",
                            "content": f"User message: '{user_message}'\n\nIs this EXPLICITLY confirming they want a PDF plan created?"
                        }
                    ],
                    "temperature": 0,
                    "max_tokens": 10
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"].strip().lower()
                confirmed = ai_response == "true"
                print(f"🤖 AI PDF confirmation check: '{user_message[:50]}...' → AI says: '{ai_response}' → PDF Confirmed: {confirmed}")
                return confirmed
            else:
                print(f"❌ AI PDF confirmation check failed: {response.status_code} - defaulting to FALSE")
                return False
                
        except Exception as e:
            print(f"❌ AI PDF confirmation check error: {str(e)} - defaulting to FALSE")
            return False
    
    async def ai_extract_data(self, conversation_text: str) -> Dict[str, Any]:
        """
        Pure AI extraction with strict null handling.
        """
        prompt = f"""Extract event planning data from this conversation.

CRITICAL: Only extract what is EXPLICITLY stated. Return null for anything not mentioned.

Conversation:
{conversation_text}

Rules:
- guest_count: Return as INTEGER (50 not "50") or null
- meal_type: Return ONE type (dinner) not multiple (dinner/lunch) or null
- dietary_restrictions: Return specific restrictions OR "none" if user said no restrictions OR null
- location: Must be specific city/country or null
- Never return placeholders like "unspecified" - use null

Return JSON:
{{
    "event_type": "exact type or null",
    "guest_count": integer or null,
    "location": "city, country or null",
    "budget": "amount with currency or null",
    "meal_type": "ONE meal type or null",
    "dietary_restrictions": "restrictions/none or null",
    "style_theme": "theme if mentioned or null",
    "colors": ["colors mentioned or empty array"],
    "date": "date if mentioned or null"
}}"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.1,
                        "max_tokens": 300
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    return json.loads(response.json()["choices"][0]["message"]["content"])
                else:
                    print(f"❌ AI extraction failed: {response.status_code}")
                    return {}
                    
        except Exception as e:
            print(f"❌ AI extraction error: {str(e)}")
            return {}
    
    async def analyze_conversation_with_ai(self, conversation_history: List[Dict], user_message: str, session_extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Simplified AI analysis focusing on core extraction.
        **FIX**: Include session extracted data to maintain context.
        """
        # Build conversation text
        messages = []
        for msg in conversation_history[-10:]:  # Last 10 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            messages.append(f"{role}: {content}")
        
        messages.append(f"user: {user_message}")
        conversation_text = "\n".join(messages)
        
        # Extract data
        extracted = await self.ai_extract_data(conversation_text)
        
        # Build context with only non-null values
        context = {}
        for field, value in extracted.items():
            if value is not None and value != "null":
                context[field] = value
        
        # **FIX**: Merge with session extracted data to prevent memory loss
        if session_extracted_data:
            for field, value in session_extracted_data.items():
                if field not in context or context[field] is None:
                    context[field] = value
                    print(f"🔄 AI analysis - preserved from session: {field} = {value}")
        
        # Add metadata
        context["ai_extracted"] = True
        context["has_food_preference"] = any(
            field in context for field in ["meal_type", "dietary_restrictions", "cuisine_preference"]
        )
        
        print(f"🎯 AI extracted {len(context)} fields from conversation")
        return context
    
    def get_next_question_focus(self, suggestions: Dict[str, Any]) -> str:
        """
        Determine what to ask next based on missing fields.
        """
        if not suggestions.get("event_type"):
            return "Ask about the event type"
        elif not suggestions.get("location"):
            return "Ask for specific city and country"
        elif not suggestions.get("guest_count"):
            return "Ask for exact number of guests"
        elif not suggestions.get("budget"):
            return "Ask about budget or style preference"
        elif not suggestions.get("meal_type"):
            return "Ask what type of meal (breakfast/lunch/dinner/cocktails/snacks)"
        elif not suggestions.get("dietary_restrictions"):
            return "Ask about dietary restrictions"
        else:
            return "All fields collected"
    
    def validate_location(self, location: str) -> Dict[str, Any]:
        """
        Simple location validation.
        """
        if not location or len(location) < 5:
            return {"valid": False, "reason": "Location too short"}
        
        generic = ["home", "house", "outdoor", "indoor", "venue", "backyard"]
        if location.lower() in generic:
            return {"valid": False, "reason": "Need specific city/country"}
        
        return {"valid": True, "reason": "Location is specific"}
    
    def get_completion_summary(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simple progress summary.
        """
        collected = sum(1 for field in self.mandatory_fields if suggestions.get(field))
        
        return {
            "collected": collected,
            "total": 6,
            "percentage": int((collected / 6) * 100),
            "ready": collected == 6
        }

# Global instance
data_collection_service = DataCollectionService()