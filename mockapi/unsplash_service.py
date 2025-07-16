#!/usr/bin/env python3
"""
Unsplash Service - Handles image fetching from Unsplash API
"""

import os
import httpx
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()

class UnsplashService:
    """Simple Unsplash image search for startup gallery"""
    
    def __init__(self):
        self.api_keys = [
            os.getenv("UNSPLASH_ACCESS_KEY_1"),
            os.getenv("UNSPLASH_ACCESS_KEY_2")
        ]
        self.api_keys = [key for key in self.api_keys if key]
        self.base_url = "https://api.unsplash.com"
        print(f"Initialized Unsplash service with {len(self.api_keys)} API keys")
    
    async def get_gallery_images(self, query: str = "event party celebration", count: int = 12) -> List[Dict]:
        """Get images from Unsplash"""
        if not self.api_keys:
            return []
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    params={"query": query, "per_page": count, "order_by": "relevant"},
                    headers={"Authorization": f"Client-ID {self.api_keys[0]}"}
                )
                
                if response.status_code == 200:
                    return response.json().get("results", [])
                return []
        except Exception as e:
            print(f"Unsplash error: {str(e)}")
            return []
    
    async def search_by_style(self, style: str, count: int = 12) -> List[Dict]:
        """Search by style with optimized queries"""
        # Style-specific query optimization for better Unsplash results
        style_queries = {
            "minimalist": "minimalist modern clean simple aesthetic",
            "wedding": "wedding bridal elegant romantic ceremony",
            "birthday party": "birthday celebration cake party colorful",
            "graduation": "graduation ceremony achievement academic success",
            "holiday party": "holiday celebration festive christmas winter",
            "summer vibes": "summer beach tropical vacation sunset",
            "music festival": "music festival concert stage lights crowd",
            "wine tasting": "wine tasting vineyard elegant sophisticated",
            "date night": "romantic dinner candles intimate evening",
            "vibrant": "colorful vibrant bright energetic dynamic",
            "bohemian": "bohemian boho rustic natural earthy",
            "luxury": "luxury elegant gold sophisticated premium",
            "romantic": "romantic soft pink flowers intimate",
            "energetic": "energetic dynamic action bright colorful"
        }
        
        query = style_queries.get(style.lower(), f"{style} aesthetic beautiful")
        return await self.get_gallery_images(query, count)