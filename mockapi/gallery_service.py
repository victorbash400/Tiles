from typing import List, Dict, Any
# from sqlalchemy.orm import Session
from dynamodb_database import PlanSession
from unsplash_service import UnsplashService
from memory_store import memory_store

class GalleryService:
    """Handles gallery content and image operations"""
    
    def __init__(self, unsplash_service: UnsplashService):
        self.unsplash_service = unsplash_service
    
    async def get_gallery_images(self, db, chat_session_id: str = None) -> Dict[str, Any]:
        """Get gallery content - prioritize AI-generated content from memory, fallback to Unsplash"""
        
        print(f"🖼️ Gallery service: Starting image fetch for session: {chat_session_id}")
        
        ai_generated_images = []
        ai_generated_music = []
        ai_generated_venues = []
        ai_generated_food = []
        
        # **NEW**: Get AI-generated content from memory store instead of DynamoDB
        if chat_session_id:
            print(f"🧠 Checking memory store for session: {chat_session_id}")
            try:
                # Get session summary to check if content exists
                session_summary = memory_store.get_session_summary(chat_session_id)
                
                if session_summary["exists"] and session_summary["generated_content_counts"]:
                    print(f"💾 Found memory content: {session_summary['generated_content_counts']}")
                    
                    # Get generated content from memory
                    generated_content = memory_store.get_generated_content(chat_session_id)
                    
                    ai_generated_images = generated_content.get("images", [])
                    ai_generated_music = generated_content.get("music", [])
                    ai_generated_venues = generated_content.get("venues", [])
                    ai_generated_food = generated_content.get("food", [])
                    
                    print(f"🎨 Memory content loaded: {len(ai_generated_images)} images, {len(ai_generated_music)} music, {len(ai_generated_venues)} venues, {len(ai_generated_food)} food")
                else:
                    print(f"📭 No generated content found in memory for session {chat_session_id}")
                    
            except Exception as e:
                print(f"❌ Error accessing memory store: {str(e)}")
        else:
            print(f"📋 No chat_session_id provided, will show startup gallery")
        
        # If we have AI-generated content, combine images, music, venues, and food
        if ai_generated_images or ai_generated_music or ai_generated_venues or ai_generated_food:
            # Mix content types for comprehensive gallery experience
            all_content = ai_generated_images[:8] + ai_generated_music[:4] + ai_generated_venues[:4] + ai_generated_food[:4]
            print(f"📱 Returning {len(ai_generated_images)} images + {len(ai_generated_music)} music + {len(ai_generated_venues)} venues + {len(ai_generated_food)} food to gallery")
            return {"images": all_content}
        
        # Fallback to Unsplash images for startup gallery
        if self.unsplash_service:
            try:
                print("📸 Fetching Unsplash images for startup gallery...")
                images = await self.unsplash_service.get_gallery_images(
                    "event party celebration inspiration decorations",
                    count=12
                )
                if images:
                    print(f"✅ Fetched {len(images)} Unsplash images for startup gallery")
                    return {"images": images}
            except Exception as e:
                print(f"Error fetching Unsplash gallery images: {str(e)}")
        
        return {"images": [], "message": "Gallery services unavailable"}
    
    async def search_by_style(self, style: str, count: int = 12) -> Dict[str, Any]:
        """Search images by style using Unsplash"""
        if self.unsplash_service:
            try:
                print(f"📸 Searching Unsplash for {style} style images...")
                images = await self.unsplash_service.search_by_style(style, count)
                print(f"✅ Found {len(images)} {style} style images")
                return {"images": images, "style": style}
            except Exception as e:
                print(f"Error searching by style: {str(e)}")
        
        return {"images": [], "style": style, "message": "Gallery services unavailable"}

def create_gallery_service(unsplash_service: UnsplashService) -> GalleryService:
    """Factory function to create gallery service"""
    return GalleryService(unsplash_service)