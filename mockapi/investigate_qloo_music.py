#!/usr/bin/env python3
"""
Deep investigation of Qloo API to understand how to find actual playlists
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def investigate_qloo_music():
    """Comprehensive investigation of Qloo music capabilities"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🔍 QLOO MUSIC INVESTIGATION")
    print("=" * 60)
    
    if not api_key:
        print("❌ No Qloo API key found")
        return
    
    # Test different music-related search terms
    music_search_terms = [
        "wedding playlist",
        "party music",
        "wedding songs",
        "dance music",
        "romantic music",
        "celebration playlist",
        "music playlist",
        "spotify playlist",
        "wedding music collection",
        "party hits",
        "love songs playlist",
        "wedding reception music"
    ]
    
    async with httpx.AsyncClient() as client:
        for search_term in music_search_terms:
            print(f"\n🎵 Testing search: '{search_term}'")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key, "Content-Type": "application/json"},
                    params={"query": search_term, "limit": 10},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    print(f"📊 Found {len(results)} results")
                    
                    # Analyze entity types
                    entity_types = {}
                    music_entities = []
                    
                    for result in results:
                        types = result.get("types", [])
                        name = result.get("name", "Unknown")
                        
                        # Count entity types
                        for entity_type in types:
                            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
                        
                        # Look for music-related entities
                        is_music = any(
                            music_type in types for music_type in [
                                "urn:entity:album",
                                "urn:entity:song", 
                                "urn:entity:artist",
                                "urn:entity:playlist",
                                "urn:entity:music",
                                "urn:entity:track"
                            ]
                        )
                        
                        if is_music:
                            music_entities.append({
                                "name": name,
                                "types": types,
                                "popularity": result.get("popularity", 0),
                                "entity_id": result.get("entity_id", ""),
                                "tags": [tag.get("name", "") for tag in result.get("tags", [])],
                                "properties": result.get("properties", {})
                            })
                    
                    print(f"🎼 Music entities found: {len(music_entities)}")
                    
                    # Show entity type breakdown
                    print("📈 Entity types:")
                    for entity_type, count in sorted(entity_types.items()):
                        print(f"   {entity_type}: {count}")
                    
                    # Show music entities in detail
                    if music_entities:
                        print(f"\n🎵 Music entities details:")
                        for i, entity in enumerate(music_entities[:3], 1):  # Show top 3
                            print(f"   {i}. {entity['name']}")
                            print(f"      Types: {entity['types']}")
                            print(f"      Popularity: {entity['popularity']}")
                            print(f"      Tags: {entity['tags'][:3]}...")  # First 3 tags
                            
                            # Check for external links
                            external = entity['properties'].get('external', {})
                            if external:
                                print(f"      External links: {list(external.keys())}")
                            
                            # Check for image
                            image = entity['properties'].get('image', {})
                            if image:
                                print(f"      Has image: ✅")
                            
                            print()
                    else:
                        print("   ❌ No music entities found")
                
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    print("\n" + "=" * 60)
    print("🎯 INVESTIGATION SUMMARY:")
    print("This investigation will help us understand:")
    print("1. What entity types Qloo returns for music searches")
    print("2. Whether Qloo has actual playlists vs just albums/songs")
    print("3. What properties are available for music entities")
    print("4. External links (Spotify, Apple Music, etc.)")
    print("5. How to construct better search queries")

async def investigate_qloo_recommendations():
    """Investigate Qloo recommendations API if available"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("\n🔗 QLOO RECOMMENDATIONS INVESTIGATION")
    print("=" * 60)
    
    # Try different endpoints that might exist
    endpoints_to_test = [
        "recommendations",
        "suggest", 
        "similar",
        "recommend",
        "related"
    ]
    
    async with httpx.AsyncClient() as client:
        for endpoint in endpoints_to_test:
            print(f"\n🧪 Testing endpoint: /{endpoint}")
            
            try:
                response = await client.get(
                    f"{api_url}{endpoint}",
                    headers={"X-API-Key": api_key},
                    timeout=5.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code != 404:
                    print(f"   Response: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"   Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(investigate_qloo_music())
    asyncio.run(investigate_qloo_recommendations())