#!/usr/bin/env python3
"""
Qloo Venue Service - Streamlined venue recommendations with better AI filtering
"""

import asyncio
import httpx
import json
import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class QlooVenueService:
    """Streamlined Qloo venue recommendations with robust AI filtering"""
    
    def __init__(self):
        self.qloo_api_key = os.getenv("QLOO_API_KEY")
        self.qloo_api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.qloo_api_key:
            raise ValueError("Qloo API key is required")
        if not self.openai_api_key:
            print("⚠️ OpenAI API key not found - AI filtering disabled")
        
        print("✅ Initialized Streamlined Qloo Venue Service")
    
    async def get_venue_recommendations(
        self, 
        event_type: str, 
        location: str = None, 
        budget: str = None, 
        guest_count: int = None,
        count: int = 6
    ) -> List[Dict]:
        """Get AI-filtered venue recommendations"""
        
        # Validate location
        if not location or len(location) < 3:
            print("❌ Invalid location for venue search")
            return []
        
        try:
            # Generate search queries
            queries = self._generate_search_queries(event_type, location, budget)
            
            # Fetch venues from Qloo
            raw_venues = await self._fetch_venues_from_qloo(queries, count * 3)
            
            if not raw_venues:
                print("❌ No venues found from Qloo API")
                return []
            
            # AI filter the venues
            filtered_venues = await self._ai_filter_venues(
                raw_venues, event_type, location, guest_count, count
            )
            
            print(f"✅ Returning {len(filtered_venues)} venues")
            return filtered_venues
            
        except Exception as e:
            print(f"❌ Venue service error: {str(e)}")
            return []
    
    def _generate_search_queries(self, event_type: str, location: str, budget: str = None) -> List[str]:
        """Generate targeted search queries"""
        
        # Map event types to venue keywords
        event_venue_map = {
            "wedding": ["wedding venues", "wedding reception halls", "banquet halls"],
            "birthday": ["party venues", "event spaces", "restaurants with private dining"],
            "corporate": ["conference centers", "business event venues", "hotels with meeting rooms"],
            "graduation": ["celebration venues", "event halls", "restaurant party rooms"],
            "baby shower": ["intimate venues", "cafe private rooms", "small event spaces"]
        }
        
        # Get venue keywords for event type
        venue_keywords = event_venue_map.get(event_type.lower(), ["event venues", "party spaces"])
        
        # Build queries with location
        queries = []
        for keyword in venue_keywords[:2]:  # Max 2 queries
            queries.append(f"{keyword} {location}")
        
        return queries
    
    async def _fetch_venues_from_qloo(self, queries: List[str], limit: int) -> List[Dict]:
        """Fetch raw venues from Qloo API"""
        
        all_venues = []
        seen_ids = set()
        
        async with httpx.AsyncClient() as client:
            for query in queries:
                try:
                    print(f"🔍 Searching: '{query}'")
                    
                    response = await client.get(
                        f"{self.qloo_api_url}search",
                        headers={
                            "X-API-Key": self.qloo_api_key,
                            "Content-Type": "application/json"
                        },
                        params={"query": query, "limit": limit},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        # Process results
                        for result in results:
                            # Check if it's a place entity
                            types = result.get("types", [])
                            if not self._is_venue_entity(types):
                                continue
                            
                            entity_id = result.get("entity_id", "")
                            if entity_id in seen_ids:
                                continue
                            
                            seen_ids.add(entity_id)
                            
                            # Extract venue data
                            venue = self._extract_venue_data(result)
                            if venue:
                                all_venues.append(venue)
                        
                        print(f"  ✅ Found {len([r for r in results if self._is_venue_entity(r.get('types', []))])} venues")
                    else:
                        print(f"  ❌ API error: {response.status_code}")
                        
                except Exception as e:
                    print(f"  ❌ Query error: {str(e)}")
        
        return all_venues
    
    def _is_venue_entity(self, types: List[str]) -> bool:
        """Allow all entities - let AI do the real filtering"""
        return True  # Let AI handle all filtering logic
    
    def _extract_venue_data(self, result: Dict) -> Optional[Dict]:
        """Extract and format venue data from Qloo result"""
        
        try:
            props = result.get("properties", {})
            
            # Basic validation
            name = result.get("name", "").strip()
            if not name:
                return None
            
            # Extract address
            address = props.get("address", "")
            if not address:
                address = props.get("location", "")
            
            # Build venue object
            return {
                "id": f"qloo_{result.get('entity_id', '')}",
                "qloo_id": result.get("entity_id", ""),
                "name": name,
                "address": address,
                "location": address,
                "type": "venue",  # Frontend card type
                "venue_type": self._determine_venue_type(result),  # Specific venue category
                "business_rating": props.get("business_rating", 0),
                "rating": props.get("business_rating", 0),
                "price_level": props.get("price_level", 0),
                "phone": props.get("phone", ""),
                "website": props.get("website", ""),
                "is_open": not props.get("is_closed", False),
                "image": props.get("image", {}).get("url", ""),
                "tags": [tag.get("name", "") for tag in result.get("tags", [])],
                "cuisine": self._extract_cuisine(result.get("tags", [])),
                "platform": "qloo"
            }
            
        except Exception as e:
            print(f"❌ Error extracting venue data: {str(e)}")
            return None
    
    def _determine_venue_type(self, result: Dict) -> str:
        """Determine venue type from result data"""
        
        tags = [tag.get("name", "").lower() for tag in result.get("tags", [])]
        types = [str(t).lower() for t in result.get("types", [])]
        all_text = " ".join(tags + types)
        
        if "restaurant" in all_text or "dining" in all_text:
            return "restaurant"
        elif "hotel" in all_text:
            return "hotel"
        elif "hall" in all_text or "center" in all_text:
            return "event_space"
        else:
            return "venue"
    
    def _extract_cuisine(self, tags: List[Dict]) -> str:
        """Extract cuisine from tags"""
        
        cuisines = []
        for tag in tags:
            name = tag.get("name", "").lower()
            if "cuisine" in name or "food" in name:
                cuisines.append(tag.get("name", ""))
        
        return ", ".join(cuisines[:2]) if cuisines else ""
    
    async def _ai_filter_venues(
        self, 
        venues: List[Dict], 
        event_type: str, 
        location: str,
        guest_count: Optional[int],
        count: int
    ) -> List[Dict]:
        """Use AI to filter venues for relevance and suitability"""
        
        if not self.openai_api_key or not venues:
            return venues[:count]
        
        # Prepare venue summary for AI with more context
        venue_summaries = []
        for v in venues:
            summary = {
                "id": v["qloo_id"],
                "name": v["name"],
                "address": v["address"],
                "type": v["type"],
                "tags": v["tags"],
                "cuisine": v.get("cuisine", ""),
                "rating": v.get("rating", 0),
                "price_level": v.get("price_level", 0)
            }
            venue_summaries.append(summary)
        
        prompt = f"""You are an expert event planner. Filter venues for a {event_type} in {location}.

STRICT REQUIREMENTS:
1. Must be suitable for hosting {event_type} events with guests
2. Must be in or near {location}
3. EXCLUDE ALL: gas stations, petrol stations, fuel stations, convenience stores, retail shops, supermarkets, hospitals, clinics, offices, banks, ATMs, auto repair shops, car dealerships, mechanics, tire shops, pharmacies, medical facilities, government buildings, schools, churches (unless specifically event venues)
4. ONLY INCLUDE: restaurants, hotels, resorts, banquet halls, event centers, wedding venues, party venues, conference centers, ballrooms, garden venues, cafes with event spaces, lounges, bars, clubs with event hosting capability
5. {f'Should accommodate {guest_count} guests' if guest_count else ''}

Venues to evaluate:
{json.dumps(venue_summaries, indent=2)}

BE VERY STRICT. If there's ANY doubt about whether a venue is suitable for hosting {event_type} events, EXCLUDE it. Gas stations, shops, and service businesses are NEVER suitable venues.

Return a JSON object with EXACTLY this structure:
{{
    "venues": [
        {{
            "id": "venue_id_here",
            "reason": "why suitable for {event_type}"
        }}
    ]
}}

Select up to {count} ONLY the most suitable venues."""

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
                        "temperature": 0.3,
                        "max_tokens": 500
                    },
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    
                    try:
                        ai_result = json.loads(content)
                        approved_venues = ai_result.get("venues", [])
                        
                        # Map approved IDs to original venues
                        approved_ids = [v["id"] for v in approved_venues if "id" in v]
                        
                        filtered = []
                        for venue in venues:
                            if venue["qloo_id"] in approved_ids:
                                # Add AI's reasoning
                                for approved in approved_venues:
                                    if approved["id"] == venue["qloo_id"]:
                                        venue["ai_reason"] = approved.get("reason", "")
                                        break
                                filtered.append(venue)
                        
                        print(f"🤖 AI approved {len(filtered)} venues")
                        return filtered[:count]
                        
                    except json.JSONDecodeError:
                        print(f"❌ Failed to parse AI response: {content[:100]}...")
                        return venues[:count]
                else:
                    print(f"❌ AI API error: {response.status_code}")
                    return venues[:count]
                    
        except Exception as e:
            print(f"❌ AI filtering error: {str(e)}")
            return venues[:count]

# Global instance
qloo_venue_service = QlooVenueService()