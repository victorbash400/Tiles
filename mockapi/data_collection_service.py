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
        
        # Core mandatory fields - simplified
        self.mandatory_fields = {
            "event_type": "Type of event",
            "location": "City and country",
            "guest_count": "Number of guests",
            "budget": "Budget amount or style preference",
            "meal_type": "Meal service type",
            "dietary_restrictions": "Dietary needs"
        }
    
    def get_data_collection_prompt(self) -> str:
        """
        Strict AI prompt that prevents placeholder values and ensures accurate extraction.
        """
        return """You are a warm, enthusiastic AI event planner! 🎉

CRITICAL RULES:
1. ONLY extract information that the user has EXPLICITLY stated
2. NEVER fill in placeholder values or list multiple options
3. If user hasn't answered a question, leave that field as null
4. For meal_type: MUST be ONE specific type (breakfast/lunch/dinner/cocktails/snacks), not multiple
5. For dietary_restrictions: Only set if user explicitly mentions them OR says "none"
6. ready_to_generate is true ONLY when ALL 6 mandatory fields have explicit values

CONVERSATION FLOW:
- Greet warmly and ask about the occasion
- Ask ONE question at a time based on what's missing
- Build naturally on their responses
- Never ask for info they already provided

MANDATORY FIELDS TO COLLECT:
1. event_type - The type of event (wedding/birthday/corporate/etc)
2. location - SPECIFIC city + country (not "home" or "outdoor")
3. guest_count - EXACT number (not "around 50")
4. budget - Amount with currency OR detailed style description
5. meal_type - ONE type: breakfast/lunch/dinner/cocktails/snacks
6. dietary_restrictions - Specific restrictions OR "none"

RESPOND WITH JSON:
{
    "message": "Your warm response and next question",
    "suggestions": {
        "event_type": null or "specific type if stated",
        "location": null or "city, country if stated",
        "guest_count": null or exact number if stated,
        "budget": null or "amount/style if stated",
        "meal_type": null or "ONE meal type if stated",
        "dietary_restrictions": null or "restrictions/none if stated"
    },
    "ready_to_generate": false (true only when ALL 6 fields have values),
    "missing_requirements": ["list of fields still needed"],
    "conversation_stage": "greeting/collecting_basics/collecting_details/ready"
}

REMEMBER: Only extract what user EXPLICITLY said. No placeholders!"""
    
    def analyze_conversation_completeness(self, suggestions: Dict[str, Any]) -> Dict[str, Any]:
        """
        Strict validation ensuring no placeholder values pass through.
        """
        missing_mandatory = []
        
        for field in self.mandatory_fields:
            value = suggestions.get(field)
            is_valid = False
            
            if field == "guest_count":
                # Must be a positive number
                if isinstance(value, (int, float)):
                    is_valid = value > 0
                elif isinstance(value, str) and value.isdigit():
                    suggestions[field] = int(value)
                    is_valid = int(value) > 0
                    
            elif field == "meal_type":
                # Must be exactly ONE meal type
                valid_types = ["breakfast", "lunch", "dinner", "cocktails", "snacks", "brunch", "buffet"]
                if isinstance(value, str):
                    value_clean = value.lower().strip()
                    # Check it's a single valid type (no slashes, commas, or multiple options)
                    is_valid = (
                        value_clean in valid_types and 
                        "/" not in value and 
                        "," not in value and
                        " or " not in value.lower()
                    )
                    
            elif field == "dietary_restrictions":
                # Can be "none" or actual restrictions
                if isinstance(value, str):
                    value_clean = value.lower().strip()
                    is_valid = (
                        value_clean in ["none", "no", "no restrictions"] or
                        (len(value_clean) >= 3 and value_clean not in ["unspecified", "not specified"])
                    )
                elif isinstance(value, list) and len(value) > 0:
                    is_valid = True
                    
            elif field == "location":
                # Must be specific city/country, not generic
                if isinstance(value, str):
                    value_clean = value.lower().strip()
                    generic_terms = ["home", "house", "outdoor", "indoor", "venue", "backyard", "office"]
                    is_valid = (
                        len(value_clean) >= 5 and
                        not any(value_clean == term for term in generic_terms) and
                        value_clean not in ["unspecified", "not specified"]
                    )
                    
            else:
                # Budget and event_type - must be non-empty and not placeholder
                if isinstance(value, str):
                    value_clean = value.strip()
                    is_valid = (
                        len(value_clean) >= 2 and
                        value_clean.lower() not in ["unspecified", "not specified", "tbd", "unknown"]
                    )
            
            if not is_valid:
                missing_mandatory.append(field)
                print(f"❌ Field '{field}' invalid: {value}")
            else:
                print(f"✅ Field '{field}' valid: {value}")
        
        # Determine stage
        stage = "greeting"
        if suggestions.get("event_type"):
            if len(missing_mandatory) > 3:
                stage = "collecting_basics"
            elif len(missing_mandatory) > 0:
                stage = "collecting_details"
            else:
                stage = "ready"
        
        return {
            "ready_to_generate": len(missing_mandatory) == 0,
            "missing_requirements": missing_mandatory,
            "conversation_stage": stage,
            "completion_percentage": int(((6 - len(missing_mandatory)) / 6) * 100)
        }
    
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
    
    async def analyze_conversation_with_ai(self, conversation_history: List[Dict], user_message: str) -> Dict[str, Any]:
        """
        Simplified AI analysis focusing on core extraction.
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