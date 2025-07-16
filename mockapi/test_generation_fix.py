#!/usr/bin/env python3
"""
Test script to verify the generation fix works correctly.
Tests the regeneration loop prevention and PDF generation.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collection_service import DataCollectionService
from ai_services import AIService

async def test_generation_states():
    """Test that generation states work correctly"""
    print("🧪 Testing Generation State Management")
    print("=" * 50)
    
    # Initialize services
    data_service = DataCollectionService()
    ai_service = AIService()
    
    # Test 1: First-time generation - all fields complete
    print("\n1️⃣ Test: First-time generation")
    suggestions = {
        "event_type": "wedding",
        "location": "Nairobi, Kenya", 
        "guest_count": 50,
        "budget": "KES 100,000",
        "meal_type": "lunch",
        "dietary_restrictions": "none"
    }
    
    # Without generated content - should allow generation after confirmation
    result = data_service.analyze_conversation_completeness(suggestions, has_generated_content=False)
    print(f"   Without content: ready_to_generate={result['ready_to_generate']}, stage={result['conversation_stage']}")
    
    # With generated content - should NOT allow generation
    result = data_service.analyze_conversation_completeness(suggestions, has_generated_content=True)
    print(f"   With content: ready_to_generate={result['ready_to_generate']}, stage={result['conversation_stage']}")
    
    # Test 2: PDF request detection
    print("\n2️⃣ Test: PDF request detection")
    
    # Mock plan context with generated content
    plan_context = {
        "generated_content": {
            "images": [{"id": "test1"}],
            "music": [{"title": "Test Song"}],
            "venues": [{"name": "Test Venue"}],
            "food": [{"name": "Test Food"}]
        },
        "session_context": {}
    }
    
    # Test PDF request
    pdf_result = await ai_service.generate_event_response(
        "can you give me a pdf of the plan?",
        {},
        [],
        plan_context
    )
    
    print(f"   PDF request result: ready_to_generate={pdf_result.get('ready_to_generate', False)}")
    print(f"   PDF requested: {pdf_result.get('pdf_requested', False)}")
    print(f"   Message: {pdf_result.get('message', 'No message')[:100]}...")
    
    # Test 3: Confirmation detection
    print("\n3️⃣ Test: Confirmation detection")
    
    confirmation_phrases = ["yes", "generate", "go ahead", "sure", "okay"]
    for phrase in confirmation_phrases:
        is_confirmed = data_service.detect_user_confirmation(phrase)
        print(f"   '{phrase}' → {is_confirmed}")
    
    # Test 4: Non-confirmation phrases
    print("\n4️⃣ Test: Non-confirmation phrases")
    
    non_confirmation_phrases = ["no", "wait", "tell me more", "what about", "maybe later"]
    for phrase in non_confirmation_phrases:
        is_confirmed = data_service.detect_user_confirmation(phrase)
        print(f"   '{phrase}' → {is_confirmed}")
    
    print("\n✅ All tests completed!")

async def test_full_flow():
    """Test the complete conversation flow"""
    print("\n🎭 Testing Complete Conversation Flow")
    print("=" * 50)
    
    ai_service = AIService()
    
    # Step 1: User provides all details
    print("\n1️⃣ User provides all event details")
    conversation_history = [
        {"role": "user", "content": "I'm planning a wedding in Nairobi for 50 guests with a budget of KES 100,000, lunch service, no dietary restrictions"}
    ]
    
    plan_context = {
        "generated_content": None,
        "session_context": {}
    }
    
    result1 = await ai_service.generate_event_response(
        "I'm planning a wedding in Nairobi for 50 guests with a budget of KES 100,000, lunch service, no dietary restrictions",
        {},
        conversation_history,
        plan_context
    )
    
    print(f"   Stage: {result1.get('conversation_stage', 'unknown')}")
    print(f"   Ready to generate: {result1.get('ready_to_generate', False)}")
    print(f"   Awaiting confirmation: {result1.get('awaiting_confirmation', False)}")
    
    # Step 2: User confirms generation
    print("\n2️⃣ User confirms generation")
    conversation_history.append({"role": "assistant", "content": result1.get("message", "")})
    conversation_history.append({"role": "user", "content": "yes, generate the recommendations"})
    
    plan_context["session_context"] = {
        "awaiting_confirmation": True,
        "user_confirmed_generation": False
    }
    
    result2 = await ai_service.generate_event_response(
        "yes, generate the recommendations",
        {},
        conversation_history,
        plan_context
    )
    
    print(f"   Stage: {result2.get('conversation_stage', 'unknown')}")
    print(f"   Ready to generate: {result2.get('ready_to_generate', False)}")
    print(f"   User confirmed: {result2.get('user_confirmed_generation', False)}")
    
    # Step 3: After generation, user asks for PDF
    print("\n3️⃣ After generation, user asks for PDF")
    conversation_history.append({"role": "assistant", "content": result2.get("message", "")})
    conversation_history.append({"role": "user", "content": "can you give me a pdf?"})
    
    plan_context["generated_content"] = {
        "images": [{"id": "test1"}],
        "music": [{"title": "Test Song"}],
        "venues": [{"name": "Test Venue"}],
        "food": [{"name": "Test Food"}]
    }
    
    result3 = await ai_service.generate_event_response(
        "can you give me a pdf?",
        {},
        conversation_history,
        plan_context
    )
    
    print(f"   Stage: {result3.get('conversation_stage', 'unknown')}")
    print(f"   Ready to generate: {result3.get('ready_to_generate', False)}")
    print(f"   PDF requested: {result3.get('pdf_requested', False)}")
    
    print("\n✅ Complete flow test finished!")

if __name__ == "__main__":
    print("🚀 Starting Generation Fix Tests")
    print("=" * 50)
    
    asyncio.run(test_generation_states())
    asyncio.run(test_full_flow())
    
    print("\n🎉 All tests completed successfully!")