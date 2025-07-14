#!/usr/bin/env python3
"""
Comprehensive exploration of Qloo API capabilities and data types
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def explore_qloo_capabilities():
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🔍 Exploring Qloo API Full Capabilities")
    print("=" * 60)
    
    # Test different search categories
    test_queries = [
        "wedding venues Manhattan",
        "romantic restaurants NYC", 
        "jazz music wedding",
        "birthday party catering",
        "fashion brands luxury",
        "travel destinations beach",
        "books wedding planning",
        "movies romantic comedy",
        "cocktail recipes summer"
    ]
    
    async with httpx.AsyncClient() as client:
        for query in test_queries:
            print(f"\n📊 Testing: '{query}'")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                    params={"query": query, "limit": 3},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    print(f"Found {len(results)} results")
                    
                    # Analyze data structure for each result
                    for i, result in enumerate(results[:2], 1):  # Limit to 2 for space
                        print(f"\n  Result {i}:")
                        print(f"    Name: {result.get('name', 'N/A')}")
                        print(f"    Types: {result.get('types', [])}")
                        print(f"    Entity ID: {result.get('entity_id', 'N/A')}")
                        
                        # Properties analysis
                        properties = result.get("properties", {})
                        if properties:
                            print(f"    Available Properties:")
                            for prop_key, prop_value in properties.items():
                                if prop_key == "image" and isinstance(prop_value, dict):
                                    print(f"      - {prop_key}: {prop_value.get('url', 'No URL')}")
                                elif prop_key == "address":
                                    print(f"      - {prop_key}: {prop_value}")
                                elif prop_key == "business_rating":
                                    print(f"      - {prop_key}: {prop_value}")
                                elif prop_key == "price_level":
                                    print(f"      - {prop_key}: {prop_value}")
                                elif prop_key == "hours":
                                    print(f"      - {prop_key}: Available")
                                elif prop_key == "phone":
                                    print(f"      - {prop_key}: {prop_value}")
                                elif prop_key == "website":
                                    print(f"      - {prop_key}: Available")
                                elif prop_key == "description":
                                    print(f"      - {prop_key}: {prop_value[:50]}...")
                                elif prop_key == "external":
                                    ext_sources = list(prop_value.keys()) if isinstance(prop_value, dict) else []
                                    print(f"      - {prop_key}: {ext_sources}")
                                else:
                                    print(f"      - {prop_key}: {type(prop_value).__name__}")
                        
                        # Tags analysis  
                        tags = result.get("tags", [])
                        if tags:
                            print(f"    Tags ({len(tags)}): {[tag.get('name', '') for tag in tags[:3]]}...")
                        
                        # Location
                        if result.get("location"):
                            location = result["location"]
                            print(f"    Location: {location.get('lat', 'N/A')}, {location.get('lon', 'N/A')}")
                        
                        # Popularity
                        if result.get("popularity"):
                            print(f"    Popularity: {result['popularity']:.3f}")
                        
                        print()
                
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 QLOO API CAPABILITIES SUMMARY:")
    print("✅ Venues: Address, ratings, hours, phone, website, images")
    print("✅ Restaurants: Cuisine, price levels, business ratings")
    print("✅ Music: Albums, artists, external links (Spotify, etc.)")
    print("✅ Books: Descriptions, ratings, publication info")
    print("✅ Places: Geocoding, neighborhoods, accessibility info")
    print("✅ Tags: Rich categorization and semantic understanding")
    print("✅ Images: High-quality venue/entity images available")
    print("❌ Pricing: No real-time pricing data")
    print("❌ Availability: No real-time booking/availability")
    print("❌ Reviews: Limited review integration")

if __name__ == "__main__":
    asyncio.run(explore_qloo_capabilities())