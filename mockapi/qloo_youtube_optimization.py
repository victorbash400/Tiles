#!/usr/bin/env python3
"""
Optimized Qloo → AI → YouTube flow for music recommendations
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_optimized_music_flow():
    """Test the optimized Qloo → AI → YouTube flow"""
    
    qloo_api_key = os.getenv("QLOO_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    qloo_api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🎵 OPTIMIZED QLOO → AI → YOUTUBE FLOW TEST")
    print("=" * 60)
    
    # Step 1: Get curated albums from Qloo
    event_context = "wedding in Mombasa Kenya for 50 guests"
    search_terms = ["wedding songs", "love songs playlist", "romantic music"]
    
    qloo_albums = []
    
    async with httpx.AsyncClient() as client:
        for search_term in search_terms:
            print(f"\n🔍 Qloo search: '{search_term}'")
            
            try:
                response = await client.get(
                    f"{qloo_api_url}search",
                    headers={"X-API-Key": qloo_api_key},
                    params={"query": search_term, "limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    for result in results:
                        if "urn:entity:album" in result.get("types", []):
                            album = {
                                "name": result.get("name", ""),
                                "popularity": result.get("popularity", 0),
                                "tags": [tag.get("name", "") for tag in result.get("tags", [])],
                                "entity_id": result.get("entity_id", "")
                            }
                            qloo_albums.append(album)
                            
                    print(f"   Found {len([r for r in results if 'urn:entity:album' in r.get('types', [])])} albums")
                
            except Exception as e:
                print(f"   Error: {str(e)}")
    
    # Remove duplicates and get top albums
    unique_albums = []
    seen_names = set()
    for album in sorted(qloo_albums, key=lambda x: x['popularity'], reverse=True):
        if album['name'] not in seen_names and len(unique_albums) < 5:
            unique_albums.append(album)
            seen_names.add(album['name'])
    
    print(f"\n📀 Top {len(unique_albums)} unique albums from Qloo:")
    for i, album in enumerate(unique_albums, 1):
        print(f"   {i}. {album['name']}")
        print(f"      Popularity: {album['popularity']:.3f}")
        print(f"      Tags: {album['tags'][:3]}")
        print()
    
    # Step 2: Use AI to convert albums to YouTube-optimized queries
    if openai_api_key and unique_albums:
        print("🤖 Converting albums to YouTube-optimized queries...")
        
        album_data = [{"name": a["name"], "tags": a["tags"][:3]} for a in unique_albums]
        
        prompt = f"""Convert these Qloo album recommendations into YouTube search queries that will find actual playlists.

Event context: {event_context}
Qloo albums: {album_data}

For each album, generate a YouTube search query that:
1. Uses the genre/style from tags
2. Focuses on "playlist" or "mix" instead of specific album names
3. Includes event context (wedding, romantic, etc.)
4. Uses current/popular terms

Return 5 YouTube search queries as a JSON array.
Example: ["romantic love songs playlist 2024", "wedding reception music mix", "indie pop wedding songs playlist"]"""

        try:
            async with httpx.AsyncClient() as ai_client:
                ai_response = await ai_client.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {openai_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": prompt}],
                    "response_format": {"type": "json_object"},
                    "temperature": 0.7,
                    "max_tokens": 200
                },
                timeout=10.0
            )
            
            if ai_response.status_code == 200:
                content = ai_response.json()["choices"][0]["message"]["content"]
                
                try:
                    # Parse the JSON response
                    ai_data = json.loads(content)
                    
                    # Extract queries (handle different response formats)
                    if isinstance(ai_data, list):
                        youtube_queries = ai_data
                    elif isinstance(ai_data, dict):
                        youtube_queries = list(ai_data.values())[0] if ai_data else []
                    else:
                        youtube_queries = []
                    
                    print(f"🎯 AI generated {len(youtube_queries)} YouTube queries:")
                    for i, query in enumerate(youtube_queries, 1):
                        print(f"   {i}. {query}")
                    
                    print("\n📊 COMPARISON:")
                    print("❌ Original Qloo album names (won't work on YouTube):")
                    for album in unique_albums[:3]:
                        print(f"   - {album['name']}")
                    
                    print("\n✅ AI-optimized YouTube queries (will find playlists):")
                    for query in youtube_queries[:3]:
                        print(f"   - {query}")
                    
                    return youtube_queries
                    
                except json.JSONDecodeError as e:
                    print(f"❌ Failed to parse AI response: {content}")
                    
            else:
                print(f"❌ AI API error: {ai_response.status_code}")
                
        except Exception as e:
            print(f"❌ AI processing error: {str(e)}")
    
    # Step 3: Simulate YouTube search (you can implement actual YouTube API call)
    print("\n🎬 Next step: Use these optimized queries with YouTube API")
    print("This approach will find actual YouTube playlists instead of obscure albums!")

if __name__ == "__main__":
    asyncio.run(test_optimized_music_flow())