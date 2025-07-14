#!/usr/bin/env python3
"""
Investigate the disconnect between AI-generated queries and Qloo search results
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def investigate_search_disconnect():
    """Trace the exact search queries being sent to Qloo"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🔍 INVESTIGATING SEARCH QUERY DISCONNECT")
    print("=" * 60)
    
    # Simulate the exact scenario from the logs
    event_context = {
        "event_type": "wedding",
        "location": "Mombasa, Kenya",
        "guest_count": "50",
        "style": "pink theme"
    }
    
    print(f"📊 Event Context: {event_context}")
    
    # These are the AI-generated queries from the logs
    ai_generated_queries = [
        "Mombasa wedding music collection",
        "upbeat party playlist for 50 guests", 
        "contemporary hits for wedding guests",
        "pink-themed wedding playlist",
        "Kenyan vs international wedding music collection"
    ]
    
    print(f"\n🤖 AI Generated Queries:")
    for i, query in enumerate(ai_generated_queries, 1):
        print(f"   {i}. {query}")
    
    # Test each query individually
    async with httpx.AsyncClient() as client:
        for i, query in enumerate(ai_generated_queries, 1):
            print(f"\n🔍 Testing Query {i}: '{query}'")
            print("-" * 50)
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                    params={"query": query, "limit": 10},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    print(f"📊 Found {len(results)} total results")
                    
                    # Analyze results
                    music_results = []
                    other_results = []
                    
                    for result in results:
                        name = result.get("name", "Unknown")
                        types = result.get("types", [])
                        popularity = result.get("popularity", 0)
                        tags = [tag.get("name", "") for tag in result.get("tags", [])]
                        
                        if any("urn:entity:album" in t for t in types):
                            music_results.append({
                                "name": name,
                                "popularity": popularity,
                                "tags": tags,
                                "types": types
                            })
                        else:
                            other_results.append({
                                "name": name,
                                "types": types
                            })
                    
                    print(f"🎵 Music entities: {len(music_results)}")
                    print(f"🔍 Other entities: {len(other_results)}")
                    
                    # Show top 3 music results
                    if music_results:
                        print(f"\n🎵 Top music results:")
                        for j, album in enumerate(music_results[:3], 1):
                            print(f"   {j}. {album['name']}")
                            print(f"      Popularity: {album['popularity']:.3f}")
                            print(f"      Tags: {album['tags'][:3]}")
                            print(f"      Relevance to '{query}': ???")
                            
                            # Check for Kenya/Mombasa/African relevance
                            kenyan_terms = ["kenya", "kenyan", "mombasa", "african", "swahili", "east africa"]
                            is_kenyan = any(term in album['name'].lower() for term in kenyan_terms)
                            has_kenyan_tags = any(term in " ".join(album['tags']).lower() for term in kenyan_terms)
                            
                            if is_kenyan or has_kenyan_tags:
                                print(f"      🇰🇪 KENYAN RELEVANCE: ✅")
                            else:
                                print(f"      🇰🇪 KENYAN RELEVANCE: ❌ (Why is this here?)")
                            print()
                    else:
                        print("   ❌ No music entities found!")
                    
                    # Show what other entity types were found
                    if other_results:
                        entity_type_counts = {}
                        for result in other_results:
                            for entity_type in result['types']:
                                entity_type_counts[entity_type] = entity_type_counts.get(entity_type, 0) + 1
                        
                        print(f"🔍 Other entity types found:")
                        for entity_type, count in sorted(entity_type_counts.items()):
                            print(f"   {entity_type}: {count}")
                
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 ANALYSIS QUESTIONS:")
    print("1. Why does 'Mombasa wedding music' return 'Julian Lennon Collection'?")
    print("2. Are the AI queries too specific for Qloo's database?")
    print("3. Is Qloo doing fuzzy matching that's too broad?")
    print("4. Should we use simpler, more generic queries?")
    print("5. Does Qloo have any Kenyan/African music in its database?")

async def test_simpler_queries():
    """Test simpler, more generic queries"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("\n🧪 TESTING SIMPLER QUERIES")
    print("=" * 60)
    
    # Test progression from specific to generic
    query_tests = [
        "Mombasa wedding music collection",  # Very specific
        "Kenyan wedding music",              # Country specific  
        "African wedding music",             # Regional
        "wedding music",                     # Generic
        "party music",                       # Very generic
        "music"                             # Ultra generic
    ]
    
    async with httpx.AsyncClient() as client:
        for query in query_tests:
            print(f"\n🔍 Testing: '{query}'")
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key},
                    params={"query": query, "limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    music_count = sum(1 for r in results if "urn:entity:album" in r.get("types", []))
                    print(f"   📊 {len(results)} total, {music_count} music")
                    
                    # Show first music result
                    for result in results:
                        if "urn:entity:album" in result.get("types", []):
                            print(f"   🎵 First result: {result.get('name', 'Unknown')}")
                            break
                
            except Exception as e:
                print(f"   ❌ Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(investigate_search_disconnect())
    asyncio.run(test_simpler_queries())