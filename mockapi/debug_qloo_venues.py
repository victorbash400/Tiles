#!/usr/bin/env python3
"""
Debug Qloo venue image data
"""

import asyncio
import httpx
import json
import os
from dotenv import load_dotenv

load_dotenv()

async def debug_venue_images():
    api_key = os.getenv("QLOO_API_KEY")
    api_url = os.getenv("QLOO_API_URL", "https://hackathon.api.qloo.com/")
    
    print("🔍 Debugging Qloo venue image data...")
    
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{api_url}search",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            params={"query": "birthday party venues Brooklyn", "limit": 3},
            timeout=10.0
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            print(f"Found {len(results)} venues:")
            for i, result in enumerate(results, 1):
                print(f"\n--- Venue {i} ---")
                print(f"Name: {result.get('name', 'N/A')}")
                print(f"Types: {result.get('types', [])}")
                
                properties = result.get("properties", {})
                print(f"Properties keys: {list(properties.keys())}")
                
                # Check for images
                image_data = properties.get("image", {})
                print(f"Image data: {image_data}")
                
                # Check external sources
                external = properties.get("external", {})
                print(f"External sources: {list(external.keys())}")
                
                print(f"Full result: {json.dumps(result, indent=2)}")
                print("-" * 40)
        else:
            print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    asyncio.run(debug_venue_images())