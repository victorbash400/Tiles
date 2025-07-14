#!/usr/bin/env python3
"""
Test script for venue filtering improvements
"""

import asyncio
import os
from dotenv import load_dotenv
from ai_services import QlooVenueService

load_dotenv()

async def test_venue_filtering():
    """Test the improved venue filtering"""
    
    print("🏨 Testing Venue Filtering")
    print("=" * 50)
    
    venue_service = QlooVenueService()
    
    # Test with a wedding search that was returning Toyota
    print("🎯 Testing: Catholic Wedding in Nairobi, Kenya")
    print("-" * 40)
    
    venues = await venue_service.get_venue_recommendations(
        event_type="wedding",
        location="Nairobi, Kenya",
        count=5
    )
    
    print(f"\n✅ Found {len(venues)} appropriate venues:")
    for i, venue in enumerate(venues, 1):
        print(f"  {i}. {venue.get('name', 'Unknown')}")
        print(f"     Type: {venue.get('type', 'Unknown')}")
        print(f"     Location: {venue.get('location', 'Unknown')}")
        if venue.get('business_rating'):
            print(f"     Rating: {venue.get('business_rating')}")
        print()

if __name__ == "__main__":
    asyncio.run(test_venue_filtering())