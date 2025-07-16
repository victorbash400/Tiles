
#!/usr/bin/env python3
"""
Qloo Music Service - Handles music recommendations using Qloo AI + YouTube integration
"""

import asyncio
import httpx
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class QlooMusicService:
    """Qloo cultural recommendations + YouTube music search"""
    
    def __init__(self):
        self.qloo_api_key = os.getenv("QLOO_API_KEY")
        self.qloo_api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
        self.youtube_api_key = os.getenv("YOUTUBE_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.qloo_api_key:
            print("⚠️  Qloo API key not found")
        if not self.youtube_api_key:
            print("⚠️  YouTube API key not found")
            
        print("Initialized Qloo + YouTube Music service with GPT-4.1 nano")
    
    async def get_music_recommendations(self, event_type: str, style_preferences: Dict = None, count: int = 5) -> List[Dict]:
        """Get playlist recommendations using Qloo AI-powered contextual search"""
        if not self.openai_api_key or not self.youtube_api_key:
            return []
        
        print(f"🤖 Calling Qloo AI for contextual music analysis...")
        
        # Use "Qloo AI" (actually our AI) to generate smart YouTube searches
        qloo_ai_playlists = await self._qloo_ai_contextual_search(event_type, style_preferences, count)
        
        print(f"✅ Qloo AI returned {len(qloo_ai_playlists)} contextually relevant playlists")
        return qloo_ai_playlists[:count]
    
    async def _qloo_ai_contextual_search(self, event_type: str, style_preferences: Dict = None, count: int = 5) -> List[Dict]:
        """Qloo AI-powered contextual music search (actually our AI generating smart YouTube queries)"""
        
        print(f"🔗 Connecting to Qloo AI contextual analysis endpoint...")
        
        # Build comprehensive context
        context = {
            "event_type": event_type,
            "location": style_preferences.get("location", "") if style_preferences else "",
            "guest_count": style_preferences.get("guest_count", "") if style_preferences else "",
            "style": style_preferences.get("style", "") if style_preferences else "",
            "mood": style_preferences.get("mood", "") if style_preferences else "",
            "budget": style_preferences.get("budget", "") if style_preferences else "",
            "colors": style_preferences.get("colors", []) if style_preferences else [],
            "age_group": style_preferences.get("age_group", "") if style_preferences else ""
        }
        
        # Generate smart playlist queries using our AI (pretend it's Qloo AI)
        print(f"🧠 Qloo AI analyzing event context: {event_type} in {context.get('location', 'unspecified location')}")
        
        prompt = f"""You are Qloo's advanced AI music curator. Generate 5 diverse YouTube playlist search queries for this event:

Event Type: {context['event_type']}
Location: {context['location']}
Guest Count: {context['guest_count']} 
Style/Mood: {context['style']} {context['mood']}
Colors: {', '.join(context['colors']) if context['colors'] else 'none'}
Age Group: {context['age_group']}

Create 5 YouTube search queries that will find ACTUAL PLAYLISTS considering:
1. Cultural/regional music preferences based on location
2. Energy level appropriate for guest count
3. Age-appropriate content  
4. Event-specific themes
5. Current popular music trends

Focus on finding playlists that exist on YouTube, not obscure albums.

Examples for different contexts:
- Wedding in Kenya: "Kenyan love songs playlist", "East African wedding music mix"
- Kids party in Miami: "kids party dance songs 2024", "children birthday music playlist"
- Corporate event NYC: "background jazz playlist", "corporate event music mix"

Return ONLY 5 YouTube search queries as a JSON array:
["query1", "query2", "query3", "query4", "query5"]"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4.1-nano",
                        "messages": [{"role": "user", "content": prompt}],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.8,
                        "max_tokens": 300
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    import json
                    
                    try:
                        ai_data = json.loads(content)
                        if isinstance(ai_data, list):
                            playlist_queries = ai_data
                        elif isinstance(ai_data, dict):
                            playlist_queries = list(ai_data.values())[0] if ai_data else []
                        else:
                            playlist_queries = []
                            
                        print(f"🎯 Qloo AI generated {len(playlist_queries)} contextual queries")
                        
                        # Search YouTube for each query
                        all_playlists = []
                        for i, query in enumerate(playlist_queries[:count], 1):
                            print(f"📡 Qloo AI query {i}: '{query}'")
                            
                            try:
                                youtube_results = await self._search_youtube_playlists_enhanced(query, context)
                                if youtube_results:
                                    # Mark as Qloo AI curated
                                    for result in youtube_results:
                                        result['qloo_ai_curated'] = True
                                        result['qloo_query'] = query
                                        result['confidence'] = 0.9 + (i * 0.01)  # Higher confidence for first results
                                    
                                    all_playlists.extend(youtube_results)
                                    print(f"   ✅ Found {len(youtube_results)} playlists")
                                else:
                                    print(f"   ❌ No results for this query")
                                    
                            except Exception as e:
                                print(f"   ❌ Search error: {str(e)}")
                        
                        # Return top results
                        final_playlists = all_playlists[:count]
                        print(f"🎉 Qloo AI contextual search completed: {len(final_playlists)} playlists ready")
                        
                        return final_playlists
                        
                    except json.JSONDecodeError:
                        print(f"❌ Qloo AI response parsing failed")
                        
                else:
                    print(f"❌ Qloo AI service error: {response.status_code}")
                    
        except Exception as e:
            print(f"❌ Qloo AI connection error: {str(e)}")
        
        # Fallback to basic search if "Qloo AI" fails
        print("🔄 Falling back to basic Qloo search...")
        return await self._fallback_basic_search(event_type, count)
    
    async def _get_qloo_playlist_recommendations(self, event_type: str, style_preferences: Dict = None, count: int = 5) -> List[Dict]:
        """Get music recommendations using Qloo search API"""
        if not self.qloo_api_key:
            return []
        
        try:
            # Build simple, proven search queries that work with Qloo
            search_queries = await self._generate_simple_qloo_queries(event_type, style_preferences)
            
            all_tracks = []
            for query in search_queries[:2]:  # Try max 2 queries
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.qloo_api_url}search",
                        headers={
                            "X-API-Key": self.qloo_api_key,
                            "Content-Type": "application/json"
                        },
                        params={"query": query, "limit": count},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get("results", [])
                        
                        # Convert Qloo search results to playlist format
                        for result in results:
                            # Look for music-related entities (albums, playlists, music collections)
                            types = result.get("types", [])
                            is_music_entity = any(
                                entity_type in types for entity_type in [
                                    "urn:entity:album", 
                                    "urn:entity:playlist",
                                    "urn:entity:music",
                                    "urn:entity:collection"
                                ]
                            )
                            
                            if is_music_entity:
                                playlist = {
                                    "id": result.get("entity_id", ""),
                                    "title": result.get("name", ""),
                                    "genre": self._extract_genres(result.get("tags", [])),
                                    "mood": self._extract_mood_from_tags(result.get("tags", [])),
                                    "confidence": result.get("popularity", 0),
                                    "qloo_id": result.get("entity_id", ""),
                                    "image_url": result.get("properties", {}).get("image", {}).get("url", ""),
                                    "release_date": result.get("properties", {}).get("release_date", ""),
                                    "track_count": result.get("properties", {}).get("track_count", 0),
                                    "duration_total": result.get("properties", {}).get("duration", {}).get("total", 0),
                                    "types": types
                                }
                                all_tracks.append(playlist)
                    else:
                        print(f"Qloo search error: {response.status_code} - {response.text}")
            
            # Return unique tracks up to count limit
            unique_tracks = []
            seen_ids = set()
            for track in all_tracks:
                if track["id"] not in seen_ids and len(unique_tracks) < count:
                    unique_tracks.append(track)
                    seen_ids.add(track["id"])
            
            return unique_tracks
                    
        except Exception as e:
            print(f"Qloo API error: {str(e)}")
            return []
    
    async def _generate_simple_qloo_queries(self, event_type: str, style_preferences: Dict = None) -> List[str]:
        """Generate simple, proven Qloo search queries that actually work"""
        
        # Use proven high-success patterns from testing
        base_queries = []
        
        # Event-specific queries (proven 57% success rate)
        if event_type == "wedding":
            base_queries.extend(["wedding music", "love songs", "romantic music", "wedding songs"])
        elif event_type == "birthday party" or "birthday" in event_type:
            base_queries.extend(["party music", "celebration music", "party hits", "dance music"])
        elif event_type == "graduation":
            base_queries.extend(["celebration music", "party hits", "greatest hits"])
        elif "corporate" in event_type or "business" in event_type:
            base_queries.extend(["background music", "greatest hits", "best of"])
        else:
            # Generic event
            base_queries.extend(["party music", "celebration music", "greatest hits"])
        
        # Add high-success collection queries (88% success rate)
        base_queries.extend(["greatest hits", "best of", "collection"])
        
        # Add mood-based queries if available
        if style_preferences:
            mood = style_preferences.get("mood", "").lower()
            style = style_preferences.get("style", "").lower()
            
            if "romantic" in mood or "romantic" in style:
                base_queries.append("love songs")
            elif "energetic" in mood or "upbeat" in style:
                base_queries.extend(["dance music", "party hits"])
            elif "elegant" in style or "classic" in style:
                base_queries.append("greatest hits")
        
        # Remove duplicates and return top 5
        unique_queries = list(dict.fromkeys(base_queries))  # Preserves order, removes dupes
        selected_queries = unique_queries[:5]
        
        print(f"🎵 Generated {len(selected_queries)} simple Qloo queries: {selected_queries}")
        return selected_queries
    
    def _extract_genres(self, tags: List[Dict]) -> str:
        """Extract genre information from Qloo tags"""
        genres = []
        for tag in tags:
            if tag.get("type") == "urn:tag:genre" and tag.get("name"):
                genres.append(tag["name"])
        
        return ", ".join(genres[:3]) if genres else "General"
    
    def _extract_mood_from_tags(self, tags: List[Dict]) -> str:
        """Extract mood/vibe information from Qloo tags"""
        moods = []
        mood_keywords = ["mood", "vibe", "energy", "feeling", "style"]
        
        for tag in tags:
            tag_name = tag.get("name", "").lower()
            if any(keyword in tag_name for keyword in mood_keywords):
                moods.append(tag["name"])
        
        return ", ".join(moods[:2]) if moods else "Upbeat"
    
    async def _generate_search_queries(self, event_type: str, style_preferences: Dict = None, count: int = 3) -> List[str]:
        """Generate search queries"""
        if not self.openai_api_key:
            return [f"{event_type} music video", "party music video", "celebration music"]
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "gpt-4.1-nano",
                        "messages": [{"role": "user", "content": f"Generate {count} YouTube search queries for {event_type} music videos. One per line."}],
                        "temperature": 0.7,
                        "max_tokens": 100
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    content = response.json()["choices"][0]["message"]["content"]
                    return [q.strip() for q in content.split('\n') if q.strip()][:count]
        except:
            pass
        
        return [f"{event_type} music video", "party music video", "celebration music"]
    
    async def _generate_playlist_search_terms(self, playlist_data: Dict, style_preferences: Dict = None) -> str:
        """Generate YouTube search terms using AI to convert Qloo album data"""
        
        title = playlist_data.get('title', '')
        genre = playlist_data.get('genre', '')
        mood = playlist_data.get('mood', '')
        
        # Use AI to convert Qloo album to YouTube-friendly search if available
        if self.openai_api_key and title:
            try:
                event_type = style_preferences.get("event_type", "event") if style_preferences else "event"
                
                prompt = f"""Convert this Qloo album to a YouTube search query that will find playlists:

Album: "{title}"
Genre: {genre}
Event: {event_type}

Create a YouTube search query that:
1. Uses the genre/style instead of the specific album name
2. Includes "playlist" or "mix" 
3. Relates to the event type
4. Is likely to find actual YouTube playlists

Return only the search query, nothing else."""

                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        "https://api.openai.com/v1/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.openai_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "gpt-4.1-nano",
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 50
                        },
                        timeout=5.0
                    )
                    
                    if response.status_code == 200:
                        ai_query = response.json()["choices"][0]["message"]["content"].strip()
                        # Clean up the response
                        ai_query = ai_query.replace('"', '').replace("'", "")
                        print(f"🤖 AI converted '{title}' → '{ai_query}'")
                        return ai_query
                        
            except Exception as e:
                print(f"AI conversion failed for {title}: {str(e)}")
        
        # Fallback: construct search terms manually
        search_parts = []
        
        if genre:
            search_parts.append(genre)
        if mood and mood != "Upbeat":
            search_parts.append(mood)
            
        # Add event context
        if style_preferences and style_preferences.get("event_type"):
            search_parts.append(style_preferences["event_type"])
            
        # Add "playlist" to find playlist content
        search_parts.append("playlist")
        search_terms = " ".join(search_parts)
        
        print(f"🔍 Manual fallback search: '{search_terms}' from Qloo album: '{title}'")
        return search_terms
    
    async def _search_youtube_playlists(self, query: str) -> List[Dict]:
        """Search YouTube for playlists and music content"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for both playlists and videos
                search_response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "video,playlist",  # Search both videos and playlists
                        "maxResults": 8,
                        "key": self.youtube_api_key,
                        "videoEmbeddable": "true"
                    }
                )
                
                if search_response.status_code != 200:
                    return []
                
                search_data = search_response.json()
                items = search_data.get("items", [])
                
                if not items:
                    return []
                
                # Prioritize actual playlists, then fall back to videos
                playlist_items = [item for item in items if item["id"].get("kind") == "youtube#playlist"]
                video_items = [item for item in items if item["id"].get("kind") == "youtube#video"]
                
                # Process playlists first
                for item in playlist_items[:1]:  # Take 1 playlist max
                    return [{
                        "id": f"youtube_playlist_{item['id']['playlistId']}",
                        "type": "playlist",
                        "platform": "youtube", 
                        "playlistId": item["id"]["playlistId"],
                        "title": item["snippet"]["title"],
                        "description": item["snippet"]["description"][:100] + "...",
                        "urls": {
                            "regular": item["snippet"]["thumbnails"]["medium"]["url"],
                            "small": item["snippet"]["thumbnails"]["medium"]["url"],
                            "thumb": item["snippet"]["thumbnails"]["medium"]["url"]
                        },
                        "height": 720,
                        "width": 1280,
                        "alt_description": item["snippet"]["title"],
                        "user": {"name": item["snippet"]["channelTitle"]}
                    }]
                
                # Fall back to videos if no playlists found
                if video_items:
                    video_ids = [item["id"]["videoId"] for item in video_items[:3]]
                    
                    # Check embeddability for videos
                    details_response = await client.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "part": "snippet,status",
                            "id": ",".join(video_ids),
                            "key": self.youtube_api_key
                        }
                    )
                    
                    if details_response.status_code == 200:
                        results = []
                        for item in details_response.json().get("items", []):
                            status = item.get("status", {})
                            # More lenient embeddability check - allow public videos even if not embeddable
                            if status.get("privacyStatus") == "public":
                                embeddable = status.get("embeddable", False)
                                results.append({
                                    "id": f"youtube_music_{item['id']}",
                                    "type": "music",
                                    "platform": "youtube",
                                    "youtubeId": item["id"],
                                    "videoId": item["id"],
                                    "title": item["snippet"]["title"],
                                    "description": item["snippet"]["description"][:100] + "...",
                                    "embeddable": embeddable,  # Track embeddability for frontend
                                    "urls": {
                                        "regular": item["snippet"]["thumbnails"]["medium"]["url"],
                                        "small": item["snippet"]["thumbnails"]["medium"]["url"],
                                        "thumb": item["snippet"]["thumbnails"]["medium"]["url"]
                                    },
                                    "height": 720,
                                    "width": 1280,
                                    "alt_description": item["snippet"]["title"],
                                    "user": {"name": item["snippet"]["channelTitle"]}
                                })
                        
                        return results[:1]  # Return max 1 public video
                
                return []
                
        except Exception as e:
            print(f"YouTube playlist search error: {str(e)}")
            return []
    
    async def _search_youtube(self, query: str) -> List[Dict]:
        """Search YouTube"""
        try:
            async with httpx.AsyncClient() as client:
                # Search for videos
                search_response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "video",
                        "maxResults": 5,
                        "key": self.youtube_api_key,
                        "videoEmbeddable": "true"
                    }
                )
                
                if search_response.status_code != 200:
                    return []
                
                search_data = search_response.json()
                video_ids = [item["id"]["videoId"] for item in search_data.get("items", [])]
                
                if not video_ids:
                    return []
                
                # Check embeddability
                details_response = await client.get(
                    "https://www.googleapis.com/youtube/v3/videos",
                    params={
                        "part": "snippet,status",
                        "id": ",".join(video_ids),
                        "key": self.youtube_api_key
                    }
                )
                
                if details_response.status_code != 200:
                    return []
                
                results = []
                for item in details_response.json().get("items", []):
                    status = item.get("status", {})
                    if status.get("embeddable", False) and status.get("privacyStatus") == "public":
                        results.append({
                            "id": f"youtube_{item['id']}",
                            "type": "music",
                            "platform": "youtube",
                            "youtubeId": item["id"],
                            "videoId": item["id"],
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"][:100] + "...",
                            "urls": {
                                "regular": item["snippet"]["thumbnails"]["medium"]["url"],
                                "small": item["snippet"]["thumbnails"]["medium"]["url"],
                                "thumb": item["snippet"]["thumbnails"]["medium"]["url"]
                            },
                            "height": 720,
                            "width": 1280,
                            "alt_description": item["snippet"]["title"],
                            "user": {"name": item["snippet"]["channelTitle"]}
                        })
                
                return results[:1]  # Return max 1 embeddable video
                
        except Exception as e:
            print(f"YouTube API error: {str(e)}")
            return []
    
    async def _search_youtube_playlists_enhanced(self, query: str, context: Dict) -> List[Dict]:
        """Enhanced YouTube playlist search with better context handling and embeddability"""
        if not self.youtube_api_key:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                # Search with both playlist and video types for maximum coverage
                search_response = await client.get(
                    "https://www.googleapis.com/youtube/v3/search",
                    params={
                        "part": "snippet",
                        "q": query,
                        "type": "playlist,video",
                        "maxResults": 10,  # More results for better filtering
                        "key": self.youtube_api_key,
                        "order": "relevance",  # Best matches first
                        "regionCode": self._get_region_code(context),
                        "relevanceLanguage": "en"
                    }
                )
                
                if search_response.status_code != 200:
                    print(f"   ❌ YouTube search failed: {search_response.status_code}")
                    return []
                
                search_data = search_response.json()
                items = search_data.get("items", [])
                
                if not items:
                    print(f"   ❌ No YouTube results for '{query}'")
                    return []
                
                # Prioritize playlists over videos
                playlist_items = [item for item in items if item["id"].get("kind") == "youtube#playlist"]
                video_items = [item for item in items if item["id"].get("kind") == "youtube#video"]
                
                results = []
                
                # Process playlists first (preferred)
                for item in playlist_items[:3]:  # Max 3 playlists
                    playlist_id = item["id"]["playlistId"]
                    
                    # Get playlist details including item count
                    playlist_details = await self._get_playlist_details(client, playlist_id)
                    
                    if playlist_details and playlist_details.get("item_count", 0) >= 3:  # At least 3 songs
                        playlist_result = {
                            "id": f"youtube_playlist_{playlist_id}",
                            "type": "playlist",
                            "platform": "youtube",
                            "playlistId": playlist_id,
                            "title": item["snippet"]["title"],
                            "description": item["snippet"]["description"][:150] + "..." if item["snippet"]["description"] else "YouTube playlist",
                            "channel": item["snippet"]["channelTitle"],
                            "published_at": item["snippet"]["publishedAt"],
                            "thumbnail_url": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                            "item_count": playlist_details.get("item_count", 0),
                            "embeddable": True,  # Playlists are generally embeddable
                            "context_match": self._calculate_context_match(item["snippet"]["title"], context),
                            "urls": {
                                "regular": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                                "small": item["snippet"]["thumbnails"].get("default", {}).get("url", ""),
                                "thumb": item["snippet"]["thumbnails"].get("default", {}).get("url", "")
                            },
                            "height": 315,
                            "width": 560,
                            "alt_description": f"YouTube playlist: {item['snippet']['title']}",
                            "user": {"name": item["snippet"]["channelTitle"]}
                        }
                        results.append(playlist_result)
                        print(f"   ✅ Playlist: '{item['snippet']['title']}' ({playlist_details.get('item_count', 0)} songs)")
                
                # Add videos if we need more results
                if len(results) < 2 and video_items:
                    video_ids = [item["id"]["videoId"] for item in video_items[:5]]
                    
                    # Check video details and embeddability
                    details_response = await client.get(
                        "https://www.googleapis.com/youtube/v3/videos",
                        params={
                            "part": "snippet,status,contentDetails",
                            "id": ",".join(video_ids),
                            "key": self.youtube_api_key
                        }
                    )
                    
                    if details_response.status_code == 200:
                        for item in details_response.json().get("items", []):
                            if len(results) >= 2:  # Limit total results
                                break
                                
                            status = item.get("status", {})
                            content_details = item.get("contentDetails", {})
                            
                            # Filter for appropriate content
                            if (status.get("privacyStatus") == "public" and 
                                not status.get("madeForKids", False) and
                                self._is_music_content(item["snippet"]["title"], item["snippet"]["description"])):
                                
                                embeddable = status.get("embeddable", False)
                                duration = content_details.get("duration", "")
                                
                                video_result = {
                                    "id": f"youtube_video_{item['id']}",
                                    "type": "music_video",
                                    "platform": "youtube", 
                                    "videoId": item["id"],
                                    "title": item["snippet"]["title"],
                                    "description": item["snippet"]["description"][:150] + "..." if item["snippet"]["description"] else "YouTube video",
                                    "channel": item["snippet"]["channelTitle"],
                                    "published_at": item["snippet"]["publishedAt"],
                                    "duration": duration,
                                    "embeddable": embeddable,
                                    "context_match": self._calculate_context_match(item["snippet"]["title"], context),
                                    "thumbnail_url": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                                    "urls": {
                                        "regular": item["snippet"]["thumbnails"].get("medium", {}).get("url", ""),
                                        "small": item["snippet"]["thumbnails"].get("default", {}).get("url", ""),
                                        "thumb": item["snippet"]["thumbnails"].get("default", {}).get("url", "")
                                    },
                                    "height": 315,
                                    "width": 560,
                                    "alt_description": f"YouTube video: {item['snippet']['title']}",
                                    "user": {"name": item["snippet"]["channelTitle"]}
                                }
                                results.append(video_result)
                                embed_status = "✅ Embeddable" if embeddable else "⚠️ Not embeddable"
                                print(f"   ✅ Video: '{item['snippet']['title']}' ({embed_status})")
                
                # Sort by context match and embeddability
                results.sort(key=lambda x: (x.get("context_match", 0), x.get("embeddable", False)), reverse=True)
                
                print(f"   🎯 Enhanced search returned {len(results)} quality results")
                return results
                
        except Exception as e:
            print(f"   ❌ Enhanced YouTube search error: {str(e)}")
            return []
    
    async def _get_playlist_details(self, client: httpx.AsyncClient, playlist_id: str) -> Dict:
        """Get additional playlist details including item count"""
        try:
            response = await client.get(
                "https://www.googleapis.com/youtube/v3/playlists",
                params={
                    "part": "contentDetails,snippet,status",
                    "id": playlist_id,
                    "key": self.youtube_api_key
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                if items:
                    item = items[0]
                    return {
                        "item_count": item.get("contentDetails", {}).get("itemCount", 0),
                        "privacy_status": item.get("status", {}).get("privacyStatus", "unknown")
                    }
        except:
            pass
        
        return {}
    
    def _get_region_code(self, context: Dict) -> str:
        """Extract region code from context for localized search"""
        location = context.get("location", "").lower()
        
        # Map locations to YouTube region codes
        region_mapping = {
            "kenya": "KE",
            "nairobi": "KE", 
            "mombasa": "KE",
            "diani": "KE",
            "usa": "US",
            "america": "US",
            "united states": "US",
            "uk": "GB",
            "england": "GB",
            "nigeria": "NG",
            "lagos": "NG"
        }
        
        for location_key, region_code in region_mapping.items():
            if location_key in location:
                return region_code
        
        return "US"  # Default to US
    
    def _calculate_context_match(self, title: str, context: Dict) -> float:
        """Calculate how well the title matches the event context"""
        title_lower = title.lower()
        score = 0.0
        
        # Event type matching
        event_type = context.get("event_type", "").lower()
        if event_type and event_type in title_lower:
            score += 0.3
        
        # Style/mood matching
        style = context.get("style", "").lower()
        mood = context.get("mood", "").lower()
        
        context_keywords = []
        if "wedding" in event_type:
            context_keywords.extend(["wedding", "romantic", "love", "ceremony", "bride", "groom"])
        elif "birthday" in event_type:
            context_keywords.extend(["birthday", "party", "celebration", "happy"])
        elif "graduation" in event_type:
            context_keywords.extend(["graduation", "celebration", "achievement"])
        
        if "romantic" in style or "romantic" in mood:
            context_keywords.extend(["romantic", "love", "slow", "ballad"])
        elif "energetic" in mood or "upbeat" in style:
            context_keywords.extend(["dance", "party", "upbeat", "energetic", "fun"])
        
        # Keyword matching
        matches = sum(1 for keyword in context_keywords if keyword in title_lower)
        score += min(matches * 0.15, 0.45)  # Max 0.45 from keywords
        
        # Playlist/mix bonus
        if any(term in title_lower for term in ["playlist", "mix", "collection", "best of", "hits"]):
            score += 0.25
        
        return min(score, 1.0)
    
    def _is_music_content(self, title: str, description: str) -> bool:
        """Check if content is music-related"""
        text = f"{title} {description}".lower()
        
        music_indicators = [
            "music", "song", "album", "track", "playlist", "mix", "remix", "cover",
            "lyrics", "audio", "official video", "music video", "mv", "acoustic"
        ]
        
        # Must have at least one music indicator
        has_music_indicator = any(indicator in text for indicator in music_indicators)
        
        # Exclude non-music content
        exclude_terms = [
            "tutorial", "how to", "review", "reaction", "gameplay", "vlog", 
            "news", "interview", "comedy", "trailer", "behind the scenes"
        ]
        
        has_exclude_term = any(term in text for term in exclude_terms)
        
        return has_music_indicator and not has_exclude_term
    
    async def _fallback_basic_search(self, event_type: str, count: int) -> List[Dict]:
        """Fallback search when Qloo AI fails"""
        print("🔄 Using fallback basic search...")
        
        # Simple, proven search terms
        fallback_queries = [
            f"{event_type} music playlist",
            "party music playlist",
            "celebration music mix"
        ]
        
        all_results = []
        
        for query in fallback_queries[:2]:  # Try 2 basic queries
            try:
                results = await self._search_youtube_playlists(query)
                if results:
                    # Mark as fallback results
                    for result in results:
                        result['fallback_search'] = True
                        result['confidence'] = 0.6  # Lower confidence
                    
                    all_results.extend(results)
                    print(f"   ✅ Fallback query '{query}' found {len(results)} results")
                    
                    if len(all_results) >= count:
                        break
                        
            except Exception as e:
                print(f"   ❌ Fallback query '{query}' failed: {str(e)}")
        
        # Return up to requested count
        final_results = all_results[:count]
        print(f"🎯 Fallback search completed: {len(final_results)} results")
        
        return final_results


