#!/usr/bin/env python3
"""
Prompt Engineering Service - Generates targeted prompts for different services
"""

import os
from typing import Dict, List, Any
from dotenv import load_dotenv

load_dotenv()

class PromptEngineeringService:
    """
    Analyzes event context and generates targeted prompts for:
    - Image generation (multiple angles)
    - Music search queries 
    - Venue search queries
    """
    
    def __init__(self):
        print("Initialized Prompt Engineering Service")
    
    def generate_image_prompts(self, event_context: Dict, suggestions: Dict) -> List[str]:
        """Generate 3 different image prompts for same event"""
        
        # Extract context
        event_type = event_context.get("event_type", "party")
        guest_count = self._extract_guest_count(event_context)
        location = event_context.get("location", "")
        
        # Extract style preferences
        colors = suggestions.get("colors", [])
        style = suggestions.get("style", "celebration")
        mood = suggestions.get("mood", "joyful")
        
        # Build base context
        color_text = f", {', '.join(colors)} colors" if colors else ""
        guest_text = f" for {guest_count} guests" if guest_count else ""
        location_text = f" in {location}" if location else ""
        
        # Generate 3 different perspectives
        prompts = [
            # 1. Overall Setup/Venue View
            f"Beautiful {event_type} venue setup{guest_text}{location_text}, {style} style{color_text}, elegant decorations, party atmosphere, wide venue shot, professional event photography",
            
            # 2. Details/Decorations Focus  
            f"{event_type.title()} decorations and details{color_text}, {style} theme, centerpieces, table settings, balloons, floral arrangements, close-up detail shots",
            
            # 3. Key Elements (cake, food, activities)
            f"{event_type.title()} highlights and activities{guest_text}, celebration cake, food presentation, party elements, {mood} atmosphere, festive moments"
        ]
        
        return prompts
    
    def generate_music_queries(self, event_context: Dict, suggestions: Dict) -> List[str]:
        """Generate targeted music search queries"""
        
        event_type = event_context.get("event_type", "party")
        guest_count = self._extract_guest_count(event_context)
        age_info = self._extract_age_info(event_context)
        
        style = suggestions.get("style", "")
        mood = suggestions.get("mood", "")
        
        queries = []
        
        # Base event query
        if age_info:
            queries.append(f"{age_info} {event_type} music")
        else:
            queries.append(f"{event_type} celebration music")
        
        # Mood-based query
        if mood:
            queries.append(f"{mood} {event_type} songs")
        
        # Style-based query  
        if style:
            queries.append(f"{style} party music")
        
        # Guest size appropriate music
        if guest_count and guest_count > 15:
            queries.append("upbeat party dance music")
        elif guest_count and guest_count < 8:
            queries.append("intimate celebration music")
        
        # Fallback queries
        if len(queries) < 3:
            queries.extend([
                f"popular {event_type} playlist",
                "celebration party songs",
                "event background music"
            ])
        
        return queries[:3]
    
    def generate_venue_queries(self, event_context: Dict, suggestions: Dict) -> List[str]:
        """Generate targeted venue search queries with location priority"""
        
        event_type = event_context.get("event_type", "party")
        location = event_context.get("location", "")
        guest_count = self._extract_guest_count(event_context)
        budget = suggestions.get("budget", "")
        style = suggestions.get("style", "")
        
        queries = []
        
        # Priority 1: Specific location + event type combinations
        if location:
            # Wedding-specific venue types
            if "wedding" in event_type.lower():
                if "beach" in location.lower() or "hawaii" in location.lower():
                    queries.append(f"beach wedding venues {location}")
                    queries.append(f"oceanfront wedding locations {location}")
                else:
                    queries.append(f"wedding venues {location}")
                    queries.append(f"wedding reception halls {location}")
            else:
                queries.append(f"{event_type} venues {location}")
                queries.append(f"event venues {location}")
        
        # Priority 2: Location + capacity-based search
        if location and guest_count:
            if guest_count > 50:
                queries.append(f"large event venues {location}")
            elif guest_count > 20:
                queries.append(f"medium event spaces {location}")
            else:
                queries.append(f"small private venues {location}")
        
        # Priority 3: Event-specific without location (if no location found)
        if not location:
            if "wedding" in event_type.lower():
                queries.extend([
                    "wedding venues",
                    "wedding reception halls",
                    "bridal venues"
                ])
            elif "birthday" in event_type.lower():
                queries.extend([
                    "birthday party venues",
                    "party halls",
                    "celebration venues"
                ])
            else:
                queries.extend([
                    f"{event_type} venues",
                    "event spaces",
                    "party venues"
                ])
        
        # Remove duplicates and limit to 3
        unique_queries = []
        for query in queries:
            if query not in unique_queries:
                unique_queries.append(query)
        
        print(f"🔍 Generated venue search queries: {unique_queries[:3]}")
        return unique_queries[:3]
    
    def _extract_guest_count(self, event_context: Dict) -> int:
        """Extract guest count from event context or messages"""
        
        # Check direct field
        if "guest_count" in event_context:
            return event_context["guest_count"]
        
        # Parse from conversation text
        conversation_text = str(event_context).lower()
        
        # Look for patterns like "20 guests", "15 people", etc.
        import re
        patterns = [
            r'(\d+)\s*guests?',
            r'(\d+)\s*people',
            r'(\d+)\s*persons?',
            r'we\s+will\s+be\s+(\d+)',
            r'about\s+(\d+)',
            r'around\s+(\d+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, conversation_text)
            if match:
                try:
                    return int(match.group(1))
                except:
                    continue
        
        return None
    
    def _extract_age_info(self, event_context: Dict) -> str:
        """Extract age-related information"""
        
        conversation_text = str(event_context).lower()
        
        # Look for age patterns
        import re
        age_patterns = [
            (r'(\d+)(?:st|nd|rd|th)?\s*birthday', 'birthday'),
            (r'sweet\s*16', '16th birthday'),
            (r'21st', '21st birthday'),
            (r'(\d+)\s*years?\s*old', 'birthday')
        ]
        
        for pattern, event_type in age_patterns:
            match = re.search(pattern, conversation_text)
            if match:
                if event_type == 'birthday':
                    age = match.group(1)
                    return f"{age}th birthday"
                else:
                    return event_type
        
        # Check for general age groups
        if any(word in conversation_text for word in ['kid', 'child', 'children']):
            return "kids"
        elif any(word in conversation_text for word in ['teen', 'teenager']):
            return "teen"
        elif any(word in conversation_text for word in ['adult', 'grown']):
            return "adult"
        
        return ""
    
    def analyze_conversation_context(self, conversation_history: List[Dict], user_message: str) -> Dict:
        """Analyze full conversation to extract event context"""
        
        # Combine all messages
        all_text = " ".join([msg.get("content", "") for msg in conversation_history])
        all_text += " " + user_message
        all_text = all_text.lower()
        
        context = {}
        
        # Extract guest count
        guest_count = self._extract_guest_count({"text": all_text})
        if guest_count:
            context["guest_count"] = guest_count
        
        # Extract location mentions with improved patterns - prioritize specific places
        import re
        
        # Step 1: Look for specific geographic location patterns first (highest priority)
        specific_location_patterns = [
            r'in\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',  # "in Hawaii and", "in Hawaii,"
            r'at\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',  # "at Miami,"
            r'at\s+the\s+([a-z]+)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',  # "at the beach"
            r'from\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?)(?:\s+and|\s+with|\s+for|\s*,|\s*$|\s*!|\s*\?)',  # "from Chicago,"
            r'(?:^|\s)([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z]{2}|[A-Z][a-z]+)',  # "Brooklyn, NY" or "Miami, Florida"
        ]
        
        # Known geographic places to prioritize (with common misspellings)
        known_places = [
            'hawaii', 'hawwai', 'hawai', 'california', 'florida', 'new york', 'texas', 'chicago', 'miami', 'los angeles', 
            'brooklyn', 'manhattan', 'boston', 'seattle', 'denver', 'atlanta', 'vegas', 'las vegas',
            'san francisco', 'san diego', 'philadelphia', 'washington', 'dc', 'maryland', 'virginia'
        ]
        
        # Map common misspellings to correct names
        location_corrections = {
            'hawwai': 'Hawaii',
            'hawai': 'Hawaii',
            'californa': 'California',
            'flordia': 'Florida',
            'chigago': 'Chicago'
        }
        
        extracted_location = None
        
        # First pass: Look for specific geographic locations
        for pattern in specific_location_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    location = match[0].strip()  # Take first group from tuple
                else:
                    location = match.strip()
                
                if 2 < len(location) < 30:
                    location_lower = location.lower()
                    # Prioritize known geographic places
                    if any(place in location_lower for place in known_places):
                        # Apply corrections for common misspellings
                        corrected_location = location_corrections.get(location_lower, location.title())
                        extracted_location = corrected_location
                        print(f"🌍 Found specific location: '{extracted_location}' (from '{location}')")
                        break
            if extracted_location:
                break
        
        # Second pass: Generic location patterns (lower priority)
        if not extracted_location:
            generic_patterns = [
                r'near\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)',  # "near the beach"
                r'around\s+([a-zA-Z\s]+?)(?:\s|$|,|\.|!|\?)',  # "around downtown"
            ]
            
            # Generic terms that are NOT good locations
            generic_terms = ['beach', 'downtown', 'park', 'area', 'venue', 'space', 'place', 'location', 
                           'indoor', 'outdoor', 'inside', 'outside', 'somewhere', 'anywhere']
            
            for pattern in generic_patterns:
                match = re.search(pattern, all_text, re.IGNORECASE)
                if match:
                    location = match.group(1).strip()
                    if 2 < len(location) < 30:
                        location_lower = location.lower()
                        # Skip generic terms and common words
                        skip_terms = generic_terms + ['the', 'a', 'an', 'some', 'any', 'this', 'that', 'my', 'our', 'their', 'his', 'her']
                        if not any(term == location_lower for term in skip_terms):
                            extracted_location = location.title()
                            print(f"🗺️ Found generic location: '{extracted_location}'")
                            break
        
        # Third pass: Direct keyword search for known places (including misspellings)
        if not extracted_location:
            for place in known_places:
                if place in all_text.lower():
                    # Apply corrections for misspellings
                    corrected_location = location_corrections.get(place, place.title())
                    extracted_location = corrected_location
                    print(f"🎯 Found location by direct keyword: '{extracted_location}' (from '{place}')")
                    break
        
        if extracted_location:
            context["location"] = extracted_location
        else:
            print("⚠️ No valid location found in conversation")
        
        # Extract food preferences
        food_keywords = ['food', 'catering', 'dinner', 'lunch', 'buffet', 'restaurant']
        if any(word in all_text for word in food_keywords):
            context["has_food_preference"] = True
        
        return context

# Global instance
prompt_service = PromptEngineeringService()