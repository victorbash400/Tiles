#!/usr/bin/env python3
"""
Test simple, generic Qloo music queries to find what actually works
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def test_simple_music_patterns():
    """Test different simple query patterns to see what works best"""
    
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🎵 TESTING SIMPLE QLOO MUSIC QUERY PATTERNS")
    print("=" * 60)
    
    # Test different patterns from very simple to slightly more complex
    test_patterns = [
        # Ultra simple - single words
        {"category": "Single Words", "queries": [
            "wedding",
            "party", 
            "love",
            "dance",
            "romantic"
        ]},
        
        # Simple two-word combinations
        {"category": "Two Words", "queries": [
            "wedding music",
            "party music",
            "love songs",
            "dance music", 
            "romantic music"
        ]},
        
        # Three words with adjectives
        {"category": "Three Words + Adjectives", "queries": [
            "best wedding music",
            "top party songs",
            "beautiful love songs",
            "upbeat dance music",
            "classic romantic songs"
        ]},
        
        # Genre-specific
        {"category": "Genre-Specific", "queries": [
            "pop music",
            "rock music",
            "jazz music",
            "r&b music",
            "hip hop music"
        ]},
        
        # Collection/compilation terms
        {"category": "Collections", "queries": [
            "greatest hits",
            "best of",
            "collection",
            "anthology",
            "compilation"
        ]},
        
        # Event-specific but simple
        {"category": "Event Types", "queries": [
            "celebration music",
            "party hits",
            "wedding songs",
            "dinner music",
            "background music"
        ]}
    ]
    
    async with httpx.AsyncClient() as client:
        for pattern_group in test_patterns:
            category = pattern_group["category"]
            queries = pattern_group["queries"]
            
            print(f"\n📊 TESTING: {category}")
            print("-" * 40)
            
            pattern_results = []
            
            for query in queries:
                try:
                    response = await client.get(
                        f"{api_url}search",
                        headers={"X-API-Key": api_key},
                        params={"query": query, "limit": 10},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        # Count music entities
                        music_count = sum(1 for r in results if "urn:entity:album" in r.get("types", []))
                        total_count = len(results)
                        
                        # Get top music result quality
                        top_music = None
                        for result in results:
                            if "urn:entity:album" in result.get("types", []):
                                top_music = {
                                    "name": result.get("name", ""),
                                    "popularity": result.get("popularity", 0),
                                    "tags": [tag.get("name", "") for tag in result.get("tags", [])]
                                }
                                break
                        
                        pattern_results.append({
                            "query": query,
                            "total": total_count,
                            "music": music_count,
                            "music_ratio": music_count / total_count if total_count > 0 else 0,
                            "top_result": top_music
                        })
                        
                        print(f"🔍 '{query}': {music_count}/{total_count} music")
                        if top_music:
                            print(f"   Top: {top_music['name']} (pop: {top_music['popularity']:.3f})")
                            if top_music['tags']:
                                print(f"   Tags: {top_music['tags'][:3]}")
                        print()
                        
                except Exception as e:
                    print(f"❌ '{query}': Error - {str(e)}")
            
            # Analyze pattern effectiveness
            if pattern_results:
                avg_music_ratio = sum(r['music_ratio'] for r in pattern_results) / len(pattern_results)
                avg_total = sum(r['total'] for r in pattern_results) / len(pattern_results)
                
                print(f"📈 {category} Summary:")
                print(f"   Average music ratio: {avg_music_ratio:.2%}")
                print(f"   Average total results: {avg_total:.1f}")
                
                # Find best query in this category
                best_query = max(pattern_results, key=lambda x: x['music_ratio'])
                print(f"   Best query: '{best_query['query']}' ({best_query['music_ratio']:.2%} music)")

async def test_optimal_wedding_queries():
    """Test the most promising patterns specifically for wedding events"""
    
    api_key = os.getenv("QLOO_API_KEY") 
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("\n💒 TESTING OPTIMAL WEDDING MUSIC QUERIES")
    print("=" * 60)
    
    # Based on initial testing, these should be the most effective
    wedding_queries = [
        "wedding music",
        "love songs", 
        "romantic music",
        "wedding songs",
        "celebration music",
        "party music",
        "dance music"
    ]
    
    print("Testing wedding-optimized queries for a Kenyan wedding...")
    
    async with httpx.AsyncClient() as client:
        all_albums = []
        
        for query in wedding_queries:
            print(f"\n🔍 Query: '{query}'")
            
            try:
                response = await client.get(
                    f"{api_url}search",
                    headers={"X-API-Key": api_key},
                    params={"query": query, "limit": 8},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    
                    query_albums = []
                    for result in results:
                        if "urn:entity:album" in result.get("types", []):
                            album = {
                                "name": result.get("name", ""),
                                "popularity": result.get("popularity", 0),
                                "tags": [tag.get("name", "") for tag in result.get("tags", [])],
                                "query_source": query
                            }
                            query_albums.append(album)
                            all_albums.append(album)
                    
                    print(f"   Found {len(query_albums)} albums")
                    if query_albums:
                        best = max(query_albums, key=lambda x: x['popularity'])
                        print(f"   Best: {best['name']} (tags: {best['tags'][:2]})")
                
            except Exception as e:
                print(f"   Error: {str(e)}")
        
        # Deduplicate and rank all albums
        print(f"\n🎯 FINAL ALBUM COLLECTION")
        print("-" * 40)
        
        unique_albums = []
        seen_names = set()
        
        for album in sorted(all_albums, key=lambda x: x['popularity'], reverse=True):
            if album['name'] not in seen_names:
                unique_albums.append(album)
                seen_names.add(album['name'])
        
        print(f"Found {len(unique_albums)} unique albums from {len(wedding_queries)} queries")
        
        # Show top 10 wedding music albums from Qloo
        print(f"\n🏆 TOP 10 WEDDING ALBUMS FROM QLOO:")
        for i, album in enumerate(unique_albums[:10], 1):
            print(f"   {i}. {album['name']}")
            print(f"      Source query: '{album['query_source']}'")
            print(f"      Popularity: {album['popularity']:.3f}")
            print(f"      Tags: {album['tags'][:3]}")
            print()
        
        return unique_albums[:5]  # Return top 5 for YouTube conversion

async def test_youtube_conversion():
    """Test converting the best Qloo albums to YouTube search terms"""
    
    print("\n🎬 TESTING YOUTUBE CONVERSION")
    print("=" * 60)
    
    # Get best albums from previous test
    albums = await test_optimal_wedding_queries()
    
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("❌ No OpenAI API key for YouTube conversion test")
        return
    
    # Convert to YouTube-friendly queries using AI
    album_data = [{"name": a["name"], "tags": a["tags"][:3]} for a in albums]
    
    prompt = f"""Convert these Qloo wedding music albums into YouTube search queries that will find actual playlists:

Albums: {album_data}
Event: Wedding in Kenya for 50 guests

Create 5 YouTube search queries that:
1. Use genre/style from the album tags
2. Focus on finding playlists, not specific albums
3. Include wedding context
4. Are likely to have results on YouTube

Return as JSON array: ["query1", "query2", "query3", "query4", "query5"]"""

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
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
                    "max_tokens": 300
                },
                timeout=10.0
            )
            
            if response.status_code == 200:
                content = response.json()["choices"][0]["message"]["content"]
                youtube_queries = json.loads(content)
                
                if isinstance(youtube_queries, dict):
                    youtube_queries = list(youtube_queries.values())[0]
                
                print("🎯 YOUTUBE-OPTIMIZED QUERIES:")
                for i, query in enumerate(youtube_queries, 1):
                    print(f"   {i}. {query}")
                
                print("\n✅ SUCCESS! This approach:")
                print("   1. Uses Qloo's curated music discovery")
                print("   2. Gets genre tags and popularity data")
                print("   3. Converts to YouTube-searchable terms")
                print("   4. Should find actual playlists instead of obscure albums")
                
                return youtube_queries
                
    except Exception as e:
        print(f"❌ YouTube conversion error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_simple_music_patterns())
    asyncio.run(test_youtube_conversion())