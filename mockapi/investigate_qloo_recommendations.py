#!/usr/bin/env python3
"""
Investigate Qloo recommendations endpoint and Spotify integration
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def investigate_qloo_recommendations():
    """Test Qloo recommendations endpoint with different parameters"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🔍 QLOO RECOMMENDATIONS ENDPOINT INVESTIGATION")
    print("=" * 60)
    
    # Test different recommendation parameters
    test_params = [
        {"type": "album"},
        {"type": "music"},
        {"type": "playlist"},
        {"type": "song"},
        {"category": "music"},
        {"entity_type": "album"},
        {"content_type": "music"},
        {"q": "wedding music", "type": "album"},
        {"query": "party music", "type": "album"},
        {"input": "wedding", "type": "music"},
    ]
    
    async with httpx.AsyncClient() as client:
        for params in test_params:
            print(f"\n🧪 Testing params: {params}")
            
            try:
                response = await client.get(
                    f"{api_url}recommendations",
                    headers={"X-API-Key": api_key},
                    params=params,
                    timeout=10.0
                )
                
                print(f"   Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    print(f"   Success! Results: {len(data.get('results', []))}")
                    print(f"   Response: {json.dumps(data, indent=2)[:300]}...")
                else:
                    print(f"   Error: {response.text}")
                    
            except Exception as e:
                print(f"   Exception: {str(e)}")

async def investigate_spotify_links():
    """Investigate how to extract Spotify links from Qloo albums"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("\n🎵 SPOTIFY LINKS INVESTIGATION")
    print("=" * 60)
    
    # Get some wedding albums and examine their Spotify links
    search_terms = ["wedding songs", "party hits", "love songs playlist"]
    
    async with httpx.AsyncClient() as client:
        for search_term in search_terms:
            print(f"\n🔍 Examining Spotify links for: '{search_term}'")
            print("-" * 40)
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key},
                    params={"query": search_term, "limit": 3},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    for result in results:
                        if "urn:entity:album" in result.get("types", []):
                            name = result.get("name", "Unknown")
                            external = result.get("properties", {}).get("external", {})
                            
                            print(f"\n📀 Album: {name}")
                            
                            if "spotify" in external:
                                spotify_data = external["spotify"]
                                print(f"   🎵 Spotify: {spotify_data}")
                                
                                # Try to extract usable Spotify info
                                if isinstance(spotify_data, dict):
                                    for key, value in spotify_data.items():
                                        print(f"      {key}: {value}")
                                elif isinstance(spotify_data, str):
                                    print(f"      URL/ID: {spotify_data}")
                            
                            if "lastfm" in external:
                                print(f"   🎶 Last.fm: {external['lastfm']}")
                            
                            if "musicbrainz" in external:
                                print(f"   🎼 MusicBrainz: {external['musicbrainz']}")
                            
                            # Check other properties
                            props = result.get("properties", {})
                            if "image" in props:
                                print(f"   🖼️  Image: Available")
                            
                            tags = [tag.get("name", "") for tag in result.get("tags", [])]
                            if tags:
                                print(f"   🏷️  Tags: {tags[:3]}")
                            
                            print()
                            
            except Exception as e:
                print(f"❌ Error: {str(e)}")

async def test_qloo_entity_details():
    """Get detailed information about specific Qloo music entities"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("\n📝 QLOO ENTITY DETAILS INVESTIGATION")
    print("=" * 60)
    
    # First, get some entity IDs
    async with httpx.AsyncClient() as client:
        # Search for popular wedding music
        response = await client.get(
            f"{api_url}search",
            headers={"X-API-Key": api_key},
            params={"query": "wedding songs", "limit": 2},
            timeout=10.0
        )
        
        if response.status_code == 200:
            results = response.json().get("results", [])
            
            for result in results:
                if "urn:entity:album" in result.get("types", []):
                    entity_id = result.get("entity_id")
                    name = result.get("name")
                    
                    print(f"\n🔍 Detailed info for: {name}")
                    print(f"   Entity ID: {entity_id}")
                    
                    # Test if we can get more details about this entity
                    detail_endpoints = [
                        f"entity/{entity_id}",
                        f"entities/{entity_id}",
                        f"details/{entity_id}",
                        f"search/{entity_id}"
                    ]
                    
                    for endpoint in detail_endpoints:
                        try:
                            detail_response = await client.get(
                                f"{api_url}{endpoint}",
                                headers={"X-API-Key": api_key},
                                timeout=5.0
                            )
                            
                            print(f"   📡 /{endpoint}: {detail_response.status_code}")
                            if detail_response.status_code == 200:
                                detail_data = detail_response.json()
                                print(f"      Success! Keys: {list(detail_data.keys())}")
                                
                        except Exception as e:
                            print(f"   📡 /{endpoint}: Error - {str(e)}")

if __name__ == "__main__":
    asyncio.run(investigate_qloo_recommendations())
    asyncio.run(investigate_spotify_links())
    asyncio.run(test_qloo_entity_details())