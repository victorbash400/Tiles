#!/usr/bin/env python3
"""
Qloo Food Service - Handles food and cuisine recommendations using Qloo AI
"""

import asyncio
import httpx
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv
from prompt_service import prompt_service

load_dotenv()

class QlooFoodService:
    """Qloo food and cuisine recommendations with cultural intelligence"""
    
    def __init__(self):
        self.qloo_api_key = os.getenv("QLOO_API_KEY")
        self.qloo_api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        
        if not self.qloo_api_key:
            print("⚠️  Qloo API key not found")
        if not self.openai_api_key:
            print("⚠️  OpenAI API key not found for AI food curation")
        
        print("Initialized Qloo Food service with GPT-4.1 nano cultural cuisine intelligence")
    
    async def get_food_recommendations(self, event_type: str, location: str = None, 
                                     budget: str = None, dietary_restrictions: List[str] = None,
                                     meal_type: str = None, cuisine_preference: str = None,
                                     guest_count: int = None, count: int = 5) -> List[Dict]:
        """Get culturally intelligent food recommendations using Qloo"""
        
        if not self.qloo_api_key:
            return await self._fallback_food_recommendations(event_type, location, count)
        
        # Build comprehensive food context
        food_context = {
            "event_type": event_type,
            "location": self._enhance_location_context(location) if location else None,
            "budget": budget,
            "dietary_restrictions": dietary_restrictions or [],
            "meal_type": meal_type,
            "cuisine_preference": cuisine_preference,
            "guest_count": guest_count
        }
        
        try:
            # Generate culturally intelligent food search queries
            search_queries = self._build_food_search_queries(food_context)
            print(f"🍽️  Food search queries: {search_queries}")
            
            all_food_items = []
            for i, query in enumerate(search_queries[:3]):  # Try max 3 queries
                print(f"🔄 Executing food query {i+1}/3: '{query}'")
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.qloo_api_url}search",
                        headers={
                            "X-API-Key": self.qloo_api_key,
                            "Content-Type": "application/json"
                        },
                        params={"query": query, "limit": count * 2},  # Get more for better filtering
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        print(f"📊 Qloo API returned {len(results)} results for query '{query}'")
                        
                        # Convert restaurant/catering places to food recommendations
                        food_items = []
                        for result in results:
                            types = result.get("types", [])
                            name = result.get("name", "").lower()
                            tags = result.get("tags", [])
                            tag_names = [tag.get("name", "").lower() for tag in tags]
                            
                            # Look for places (restaurants/catering) with food-related tags
                            is_place_entity = "urn:entity:place" in types
                            has_food_tags = any(
                                food_keyword in tag_name for tag_name in tag_names
                                for food_keyword in [
                                    "food", "restaurant", "cuisine", "catering", "dining", "cafe", 
                                    "bakery", "kitchen", "buffet", "grill", "bbq", "cooking", "chef",
                                    "meal", "lunch", "dinner", "breakfast", "snack", "beverage", "drink"
                                ]
                            )
                            has_food_name = any(
                                food_word in name for food_word in [
                                    "restaurant", "cuisine", "food", "catering", "cafe", "bakery",
                                    "kitchen", "dining", "buffet", "grill", "bbq", "hotel", "resort"
                                ]
                            )
                            
                            # Include if it's a place with food-related tags or name
                            is_food_entity = is_place_entity and (has_food_tags or has_food_name)
                            
                            if is_food_entity:
                                
                                food_item = {
                                    "id": f"qloo_food_{result.get('entity_id', '')}",
                                    "type": "food_recommendation",
                                    "platform": "qloo",
                                    "name": result.get("name", ""),
                                    "cuisine_type": self._extract_cuisine_type(result.get("tags", [])),
                                    "description": self._generate_food_description(result, food_context),
                                    "cultural_context": self._extract_cultural_context(result.get("tags", []), location),
                                    "dietary_info": self._extract_dietary_info(result.get("tags", []), dietary_restrictions),
                                    "price_range": self._estimate_price_range(result.get("properties", {}), budget),
                                    "serving_style": self._suggest_serving_style(result, meal_type, guest_count),
                                    "popularity": result.get("popularity", 0),
                                    "qloo_id": result.get("entity_id", ""),
                                    "confidence": result.get("popularity", 0) * 0.8,  # Qloo confidence
                                    "image_url": result.get("properties", {}).get("image", {}).get("url", ""),
                                    "urls": {
                                        "regular": result.get("properties", {}).get("image", {}).get("url", ""),
                                        "small": result.get("properties", {}).get("image", {}).get("url", ""),
                                        "thumb": result.get("properties", {}).get("image", {}).get("url", "")
                                    },
                                    "height": 400,
                                    "width": 600,
                                    "alt_description": f"{result.get('name', 'Food recommendation')} for {event_type}",
                                    "user": {"name": "Qloo Cultural Intelligence"},
                                    "tags": result.get("tags", [])
                                }
                                food_items.append(food_item)
                        
                        all_food_items.extend(food_items)
                        print(f"📋 Query '{query}' found {len(food_items)} food items")
                    
                    else:
                        print(f"❌ Qloo food search error: {response.status_code} - {response.text}")
            
            # Deduplicate and apply AI filtering
            print(f"🔄 Processing {len(all_food_items)} total food items")
            unique_food_items = []
            seen_ids = set()
            for item in all_food_items:
                if item["qloo_id"] not in seen_ids:
                    unique_food_items.append(item)
                    seen_ids.add(item["qloo_id"])
            
            print(f"📝 Deduped to {len(unique_food_items)} unique food items, applying AI curation...")
            
            # Apply AI curation for cultural appropriateness and event suitability
            curated_food = await self._ai_curate_food(unique_food_items, food_context, count)
            
            # Enhance with food images if no Qloo images available
            final_food = await self._enhance_food_images(curated_food)
            
            print(f"🎯 Final curated food recommendations: {len(final_food)}")
            for i, food in enumerate(final_food, 1):
                print(f"  #{i}: '{food.get('name', 'No name')}' - {food.get('cuisine_type', 'Unknown cuisine')}")
            
            return final_food
            
        except Exception as e:
            print(f"❌ Qloo Food API error: {str(e)}")
            return await self._fallback_food_recommendations(event_type, location, count)
    
    def _build_food_search_queries(self, food_context: Dict) -> List[str]:
        """Build culturally intelligent food search queries"""
        
        event_type = food_context.get("event_type", "")
        location = food_context.get("location", "")
        meal_type = food_context.get("meal_type", "")
        cuisine_preference = food_context.get("cuisine_preference", "")
        dietary_restrictions = food_context.get("dietary_restrictions", [])
        
        queries = []
        
        # Event-specific restaurant/catering queries
        if event_type == "wedding":
            queries.extend([
                "wedding catering", "wedding restaurant", "wedding venue dining",
                "celebration catering", "elegant restaurant", "special occasion dining"
            ])
        elif "birthday" in event_type:
            queries.extend([
                "party catering", "birthday restaurant", "celebration dining",
                "party venue", "festive restaurant"
            ])
        elif "corporate" in event_type:
            queries.extend([
                "corporate catering", "business restaurant", "office catering",
                "professional catering", "meeting catering"
            ])
        else:
            queries.extend([
                "celebration restaurant", "party catering", "special occasion dining"
            ])
        
        # Location-based cultural restaurant queries
        if location:
            location_lower = location.lower()
            if "kenya" in location_lower or "nairobi" in location_lower or "mombasa" in location_lower:
                queries.extend([
                    "kenyan restaurant", "east african restaurant", "swahili restaurant",
                    "kenyan catering", "african restaurant"
                ])
            elif "diani" in location_lower:
                queries.extend([
                    "coastal restaurant", "seafood restaurant", "swahili restaurant",
                    "beach restaurant", "tropical restaurant"
                ])
            
            # Add location-specific queries
            queries.append(f"{location} restaurant")
            queries.append(f"{location} catering")
        
        # Meal type specific
        if meal_type:
            queries.append(f"{meal_type} restaurant")
            queries.append(f"{meal_type} catering")
        
        # Cuisine preference
        if cuisine_preference:
            queries.append(f"{cuisine_preference} restaurant")
            queries.append(f"{cuisine_preference} catering")
        
        # Dietary restrictions
        for restriction in dietary_restrictions:
            if restriction:
                queries.append(f"{restriction} restaurant")
                queries.append(f"{restriction} catering")
        
        # Generic high-success queries
        queries.extend([
            "catering", "restaurant", "dining", "buffet restaurant"
        ])
        
        # Remove duplicates and return top queries
        unique_queries = list(dict.fromkeys(queries))
        selected_queries = unique_queries[:6]  # Max 6 queries
        
        print(f"🍽️  Generated {len(selected_queries)} food search queries")
        return selected_queries
    
    def _enhance_location_context(self, location: str) -> str:
        """Enhance location with cultural context for food search"""
        if not location:
            return location
            
        location_lower = location.lower()
        
        # Cultural food context enhancements
        if "diani" in location_lower:
            return "Diani Beach Kenya coastal cuisine"
        elif "mombasa" in location_lower:
            return "Mombasa Kenya swahili cuisine"
        elif "nairobi" in location_lower:
            return "Nairobi Kenya urban cuisine"
        elif "kenya" in location_lower:
            return f"{location} east african cuisine"
        else:
            return location
    
    def _extract_cuisine_type(self, tags: List[Dict]) -> str:
        """Extract cuisine type from Qloo tags"""
        cuisines = []
        for tag in tags:
            tag_name = tag.get("name", "").lower()
            if any(cuisine_keyword in tag_name for cuisine_keyword in 
                   ["cuisine", "food", "dish", "cooking", "culinary"]):
                cuisines.append(tag["name"])
        
        return ", ".join(cuisines[:2]) if cuisines else "International"
    
    def _extract_cultural_context(self, tags: List[Dict], location: str) -> str:
        """Extract cultural context for food appropriateness"""
        cultural_info = []
        
        # Look for cultural/regional tags
        for tag in tags:
            tag_name = tag.get("name", "").lower()
            if any(cultural_keyword in tag_name for cultural_keyword in 
                   ["traditional", "authentic", "cultural", "regional", "local", "heritage"]):
                cultural_info.append(tag["name"])
        
        # Add location-based cultural context
        if location:
            location_lower = location.lower()
            if "kenya" in location_lower:
                cultural_info.append("East African heritage")
            elif "diani" in location_lower:
                cultural_info.append("Coastal tradition")
        
        return ", ".join(cultural_info[:3]) if cultural_info else "Contemporary"
    
    def _extract_dietary_info(self, tags: List[Dict], dietary_restrictions: List[str]) -> List[str]:
        """Extract dietary information and match with user restrictions"""
        dietary_info = []
        
        # Look for dietary tags
        for tag in tags:
            tag_name = tag.get("name", "").lower()
            if any(dietary_keyword in tag_name for dietary_keyword in 
                   ["vegetarian", "vegan", "halal", "kosher", "gluten-free", "dairy-free"]):
                dietary_info.append(tag["name"])
        
        # Match with user restrictions
        if dietary_restrictions:
            for restriction in dietary_restrictions:
                if restriction.lower() in str(tags).lower():
                    dietary_info.append(f"Suitable for {restriction}")
        
        return dietary_info
    
    def _estimate_price_range(self, properties: Dict, budget: str) -> str:
        """Estimate price range based on Qloo properties and user budget"""
        
        # Try to get price info from properties
        price_level = properties.get("price_level", 0)
        
        if price_level:
            if price_level <= 1:
                return "Budget-friendly"
            elif price_level <= 2:
                return "Moderate"
            elif price_level <= 3:
                return "Premium"
            else:
                return "Luxury"
        
        # Use budget context if available
        if budget:
            budget_lower = budget.lower()
            if any(budget_indicator in budget_lower for budget_indicator in 
                   ["cheap", "budget", "affordable", "low"]):
                return "Budget-friendly"
            elif any(budget_indicator in budget_lower for budget_indicator in 
                     ["expensive", "high-end", "luxury", "premium"]):
                return "Premium"
        
        return "Moderate"
    
    def _suggest_serving_style(self, result: Dict, meal_type: str, guest_count: int) -> str:
        """Suggest appropriate serving style based on context"""
        
        # Consider guest count
        if guest_count:
            if guest_count < 10:
                return "Plated service"
            elif guest_count < 50:
                return "Family style"
            else:
                return "Buffet style"
        
        # Consider meal type
        if meal_type:
            meal_lower = meal_type.lower()
            if "cocktail" in meal_lower or "snack" in meal_lower:
                return "Cocktail style"
            elif "breakfast" in meal_lower:
                return "Continental"
            elif "lunch" in meal_lower:
                return "Buffet style"
            elif "dinner" in meal_lower:
                return "Plated service"
        
        return "Flexible serving"
    
    def _generate_food_description(self, result: Dict, food_context: Dict) -> str:
        """Generate contextual food description"""
        
        name = result.get("name", "")
        event_type = food_context.get("event_type", "")
        location = food_context.get("location", "")
        
        # Build description based on context
        description_parts = []
        
        if name:
            description_parts.append(f"Delicious {name}")
        
        if event_type:
            description_parts.append(f"perfect for {event_type} celebrations")
        
        if location and any(loc in location.lower() for loc in ["kenya", "diani", "mombasa"]):
            description_parts.append("featuring authentic East African flavors")
        
        # Add cultural context
        tags = result.get("tags", [])
        if any("traditional" in tag.get("name", "").lower() for tag in tags):
            description_parts.append("prepared with traditional methods")
        
        return " ".join(description_parts) if description_parts else "Culturally curated cuisine recommendation"
    
    async def _ai_curate_food(self, food_items: List[Dict], food_context: Dict, count: int) -> List[Dict]:
        """Use AI to curate food recommendations for cultural appropriateness and event suitability"""
        
        if not self.openai_api_key:
            print("⚠️ No OpenAI API key, returning first food items")
            return food_items[:count]
        
        # Prepare food data for AI analysis
        food_data = []
        for food in food_items:
            food_data.append({
                "name": food.get("name", ""),
                "cuisine_type": food.get("cuisine_type", ""),
                "cultural_context": food.get("cultural_context", ""),
                "dietary_info": food.get("dietary_info", []),
                "qloo_id": food.get("qloo_id", "")
            })
        
        event_type = food_context.get("event_type", "")
        location = food_context.get("location", "")
        dietary_restrictions = food_context.get("dietary_restrictions", [])
        meal_type = food_context.get("meal_type", "")
        guest_count = food_context.get("guest_count", 0)
        
        prompt = f"""You are a cultural food expert. Curate the best food recommendations for this event:

EVENT CONTEXT:
- Event Type: {event_type}
- Location: {location}
- Meal Type: {meal_type}
- Guest Count: {guest_count}
- Dietary Restrictions: {dietary_restrictions}

CULTURAL CONSIDERATIONS:
- If location is in Kenya/East Africa, prioritize authentic regional cuisine
- Consider cultural dietary laws and preferences
- Ensure food is appropriate for the event formality level
- Match serving style to guest count and event type

FOOD OPTIONS:
{food_data}

Select the {count} MOST appropriate food recommendations considering:
1. Cultural appropriateness for the location
2. Suitable for the event type and formality
3. Accommodates dietary restrictions
4. Practical for guest count and serving style
5. Authentic and high-quality options

Return ONLY a JSON object with this exact structure:
{{
  "recommendations": ["qloo_id_1", "qloo_id_2", "qloo_id_3"]
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
                        "model": "gpt-4.1-nano",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.2,  # Lower temperature for consistent curation
                        "max_tokens": 200
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    try:
                        parsed_response = json.loads(content)
                        
                        # Extract recommendations from the expected format
                        if isinstance(parsed_response, dict) and "recommendations" in parsed_response:
                            curated_ids = parsed_response["recommendations"]
                        elif isinstance(parsed_response, list):
                            curated_ids = parsed_response
                        elif isinstance(parsed_response, dict):
                            # Try different possible keys as fallback
                            for key in ["ids", "qloo_ids", "approved", "selected", "recommendations"]:
                                if key in parsed_response:
                                    curated_ids = parsed_response[key]
                                    break
                            else:
                                # Take first value if no known key
                                curated_ids = list(parsed_response.values())[0] if parsed_response else []
                        else:
                            curated_ids = []
                        
                        # Ensure it's a list
                        if not isinstance(curated_ids, list):
                            curated_ids = [curated_ids] if curated_ids else []
                            
                    except json.JSONDecodeError as e:
                        print(f"❌ AI curation response parsing failed: {content[:200]}...")
                        print(f"❌ JSON Error: {str(e)}")
                        # Fallback: return first items
                        return food_items[:count]
                    
                    # Filter food items based on AI curation
                    curated = []
                    for food in food_items:
                        if food.get("qloo_id") in curated_ids and len(curated) < count:
                            curated.append(food)
                    
                    print(f"🤖 AI curated {len(curated_ids)} food items: {curated_ids}")
                    return curated
                    
                else:
                    print(f"❌ AI curation API error: {response.status_code}")
                    return food_items[:count]
                    
        except Exception as e:
            print(f"❌ AI curation error: {str(e)}")
            return food_items[:count]
    
    async def _enhance_food_images(self, food_items: List[Dict]) -> List[Dict]:
        """Enhance food items with high-quality images from Unsplash if needed"""
        
        if not self.unsplash_access_key:
            return food_items
        
        enhanced_items = []
        
        for food in food_items:
            # If no image from Qloo, try to get from Unsplash
            if not food.get("image_url") or not food.get("urls", {}).get("regular"):
                try:
                    # Create search query for food image
                    search_query = f"{food.get('name', '')} {food.get('cuisine_type', '')} food"
                    
                    async with httpx.AsyncClient() as client:
                        response = await client.get(
                            "https://api.unsplash.com/search/photos",
                            headers={
                                "Authorization": f"Client-ID {self.unsplash_access_key}"
                            },
                            params={
                                "query": search_query,
                                "per_page": 1,
                                "orientation": "landscape"
                            },
                            timeout=5.0
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            if data.get("results"):
                                image = data["results"][0]
                                food["image_url"] = image["urls"]["regular"]
                                food["urls"] = {
                                    "regular": image["urls"]["regular"],
                                    "small": image["urls"]["small"],
                                    "thumb": image["urls"]["thumb"]
                                }
                                food["height"] = image.get("height", 400)
                                food["width"] = image.get("width", 600)
                                food["alt_description"] = image.get("alt_description", food["alt_description"])
                                food["user"] = {"name": image["user"]["name"]}
                
                except Exception as e:
                    print(f"❌ Unsplash enhancement failed for {food.get('name', '')}: {str(e)}")
            
            enhanced_items.append(food)
        
        return enhanced_items
    
    async def _fallback_food_recommendations(self, event_type: str, location: str, count: int) -> List[Dict]:
        """Fallback food recommendations when Qloo fails"""
        
        print("🔄 Using fallback food recommendations...")
        
        # Basic food recommendations based on event type and location
        fallback_foods = []
        
        if event_type == "wedding":
            fallback_foods = [
                {"name": "Wedding Cake", "cuisine_type": "Desserts", "description": "Traditional wedding celebration cake"},
                {"name": "Elegant Buffet", "cuisine_type": "International", "description": "Sophisticated buffet for wedding celebration"},
                {"name": "Cocktail Appetizers", "cuisine_type": "Appetizers", "description": "Elegant finger foods for wedding reception"}
            ]
        elif "birthday" in event_type:
            fallback_foods = [
                {"name": "Birthday Cake", "cuisine_type": "Desserts", "description": "Celebratory birthday cake"},
                {"name": "Party Snacks", "cuisine_type": "Appetizers", "description": "Fun party food and snacks"},
                {"name": "Festive Buffet", "cuisine_type": "International", "description": "Colorful party buffet"}
            ]
        else:
            fallback_foods = [
                {"name": "Celebration Feast", "cuisine_type": "International", "description": "Special occasion dining"},
                {"name": "Party Catering", "cuisine_type": "Catering", "description": "Professional event catering"},
                {"name": "Cultural Cuisine", "cuisine_type": "Traditional", "description": "Local traditional food"}
            ]
        
        # Add location-specific foods
        if location and "kenya" in location.lower():
            fallback_foods.extend([
                {"name": "Nyama Choma", "cuisine_type": "Kenyan", "description": "Traditional Kenyan grilled meat"},
                {"name": "Pilau Rice", "cuisine_type": "Kenyan", "description": "Spiced rice dish popular in Kenya"},
                {"name": "Samosas", "cuisine_type": "East African", "description": "Popular East African snack"}
            ])
        
        # Convert to proper format
        formatted_foods = []
        for i, food in enumerate(fallback_foods[:count]):
            formatted_food = {
                "id": f"fallback_food_{i}",
                "type": "food_recommendation",
                "platform": "fallback",
                "name": food["name"],
                "cuisine_type": food["cuisine_type"],
                "description": food["description"],
                "cultural_context": "General recommendation",
                "dietary_info": [],
                "price_range": "Moderate",
                "serving_style": "Flexible serving",
                "popularity": 0.5,
                "confidence": 0.3,
                "image_url": "",
                "urls": {"regular": "", "small": "", "thumb": ""},
                "height": 400,
                "width": 600,
                "alt_description": f"{food['name']} for {event_type}",
                "user": {"name": "Fallback Recommendations"}
            }
            formatted_foods.append(formatted_food)
        
        print(f"🎯 Fallback food recommendations: {len(formatted_foods)}")
        return formatted_foods

# Global instance
qloo_food_service = QlooFoodService()