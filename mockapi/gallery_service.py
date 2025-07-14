from typing import List, Dict, Any
from sqlalchemy.orm import Session
from database import PlanSession
from ai_services import UnsplashService

class GalleryService:
    """Handles gallery content and image operations"""
    
    def __init__(self, unsplash_service: UnsplashService):
        self.unsplash_service = unsplash_service
    
    async def get_gallery_images(self, db: Session) -> Dict[str, Any]:
        """Get gallery content - prioritize AI-generated content, fallback to Unsplash"""
        
        # Get recent AI-generated content from plan sessions
        recent_plans = db.query(PlanSession).filter(
            PlanSession.generated_content.isnot(None)
        ).order_by(PlanSession.last_state_change.desc()).limit(5).all()
        
        ai_generated_images = []
        ai_generated_music = []
        ai_generated_venues = []
        
        for plan in recent_plans:
            if plan.generated_content:
                # Add images
                if plan.generated_content.get("images"):
                    ai_generated_images.extend(plan.generated_content["images"])
                # Add music
                if plan.generated_content.get("music"):
                    ai_generated_music.extend(plan.generated_content["music"])
                # Add venues
                if plan.generated_content.get("venues"):
                    ai_generated_venues.extend(plan.generated_content["venues"])
        
        # If we have AI-generated content, combine images, music, and venues
        if ai_generated_images or ai_generated_music or ai_generated_venues:
            # Mix content types for comprehensive gallery experience
            all_content = ai_generated_images[:8] + ai_generated_music[:4] + ai_generated_venues[:4]
            print(f"📱 Returning {len(ai_generated_images)} images + {len(ai_generated_music)} music + {len(ai_generated_venues)} venues to gallery")
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