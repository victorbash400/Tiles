#!/usr/bin/env python3
"""
Test AI venue filtering for Diani, Kenya (the problematic case)
"""

import asyncio
import os
from dotenv import load_dotenv
from ai_services import QlooVenueService

load_dotenv()

async def test_diani_filtering():
    """Test AI filtering for Diani, Kenya"""
    
    print("🏖️ Testing AI Venue Filtering for Diani, Kenya")
    print("=" * 60)
    
    venue_service = QlooVenueService()
    
    print("🎯 Testing: Wedding in Diani (should recognize as Kenya)")
    print("-" * 50)
    
    venues = await venue_service.get_venue_recommendations(
        event_type="wedding",
        location="Diani",  # Just "Diani" like the problematic case
        count=5
    )
    
    print(f"\n✅ AI filtered to {len(venues)} venues for Diani:")
    for i, venue in enumerate(venues, 1):
        print(f"  {i}. {venue.get('name', 'Unknown')}")
        print(f"     Address: {venue.get('address', 'No address')}")
        print(f"     Location: {venue.get('location', 'Unknown')}")
        if venue.get('business_rating'):
            print(f"     Rating: {venue.get('business_rating')}")
        print()

if __name__ == "__main__":
    asyncio.run(test_diani_filtering())