from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import os
from dotenv import load_dotenv
from sqlalchemy.orm import Session

# Import database and models
try:
    from database import create_tables, get_db, ChatSession
except ImportError as e:
    print(f"Database import error: {e}")
    def create_tables(): pass
    def get_db(): return None

# Import services and models
from ai_services import AIService
from unsplash_service import UnsplashService
from models import (
    MessageCreate, MessageResponse, ChatSessionResponse, 
    AIMemoryResponse, GalleryResponse, ServiceStatusResponse
)
from chat_service import chat_service
from event_service import create_event_service
from gallery_service import create_gallery_service
from pdf_service import pdf_service

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Tiles AI Event Planning API", version="2.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
try:
    ai_service = AIService()
    unsplash_service = UnsplashService()
    event_service = create_event_service(ai_service)
    gallery_service = create_gallery_service(unsplash_service)
    print("✅ All services initialized successfully")
except Exception as e:
    print(f"❌ Error initializing services: {str(e)}")
    ai_service = None
    unsplash_service = None
    event_service = None
    gallery_service = None

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    # Clear database on startup for fresh sessions
    db_path = "tiles_events.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Cleared previous database")
    
    create_tables()
    print("✅ Database tables created")
    print("🧠 AI-powered plan management system initialized")

# API Endpoints

@app.get("/", response_model=ServiceStatusResponse)
async def root():
    """Health check endpoint"""
    return ServiceStatusResponse(
        message="Tiles AI Event Planning API is running",
        services={
            "ai": ai_service is not None,
            "unsplash": unsplash_service is not None,
            "event": event_service is not None,
            "gallery": gallery_service is not None
        }
    )

@app.get("/test-ai")
async def test_ai():
    """Test AI service with GPT-4.1 nano"""
    if not ai_service:
        return {"error": "AI service not available"}
    
    try:
        result = await asyncio.wait_for(
            ai_service.generate_event_response(
                "test party",
                {},
                [],
                {}
            ),
            timeout=5.0
        )
        return {"success": True, "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/test-azure-dalle")
async def test_azure_dalle():
    """Test Azure DALL-E 3 image generation"""
    if not ai_service:
        return {"error": "AI service not available"}
    
    try:
        result = await asyncio.wait_for(
            ai_service.generate_event_images(
                "simple birthday party with balloons",
                {"colors": ["blue", "red"], "style": "modern"}
            ),
            timeout=60.0
        )
        return {"success": True, "images_generated": len(result), "result": result}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.get("/api/chats", response_model=List[ChatSessionResponse])
async def get_all_chats(db: Session = Depends(get_db)):
    """Get all chat sessions"""
    return chat_service.get_all_chats(db)

@app.post("/api/chats", response_model=ChatSessionResponse)
async def create_new_chat(db: Session = Depends(get_db)):
    """Create a new chat session"""
    return chat_service.create_new_chat(db)

@app.get("/api/chats/{chat_id}", response_model=ChatSessionResponse)
async def get_chat_by_id(chat_id: str, db: Session = Depends(get_db)):
    """Get a specific chat session"""
    result = chat_service.get_chat_by_id(chat_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Chat not found")
    return result

@app.post("/api/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message_and_get_ai_response(
    chat_id: str, 
    message_data: MessageCreate, 
    db: Session = Depends(get_db)
):
    """Send a message and get AI response with intelligent event planning"""
    
    # Get or create chat session
    session = db.query(ChatSession).filter(ChatSession.session_id == chat_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    try:
        # Save user message
        chat_service.save_user_message(session.id, message_data.content, db)
        
        # Build conversation history
        conversation_history = chat_service.build_conversation_history(session)
        
        # Add current message to conversation history
        conversation_history.append({
            "role": "user", 
            "content": message_data.content
        })
        
        # Process message and generate response using event service
        if not event_service:
            raise HTTPException(status_code=500, detail="Event service not available")
            
        result = await event_service.process_message_and_generate_response(
            chat_id, message_data.content, session, conversation_history, db
        )
        
        ai_response = result["ai_response"]
        ai_suggestions = result["ai_suggestions"]
        
        # Save AI message
        ai_message = chat_service.save_ai_message(
            session.id,
            ai_response.get("message", "I'm here to help with your event planning!"),
            ai_suggestions,
            db
        )
        
        # Update session context
        chat_service.update_session_context(session, ai_response, db)
        
        return MessageResponse(
            id=ai_message.id,
            content=ai_message.content,
            role=ai_message.role,
            timestamp=ai_message.timestamp.strftime("%H:%M"),
            ai_suggestions=ai_suggestions,
            image_data=ai_suggestions.get("image_data", []),
            music_data=ai_suggestions.get("music_data", []),
            venue_data=ai_suggestions.get("venue_data", [])
        )
        
    except Exception as e:
        db.rollback()
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/ai/memory", response_model=AIMemoryResponse)
async def get_ai_memory(user_session: str = None, db: Session = Depends(get_db)):
    """Get AI memory/personalization data for a user"""
    if not event_service:
        return AIMemoryResponse(
            summary="Event service not available",
            active_monitoring=[],
            plan_status="unknown"
        )
    
    if not user_session:
        return AIMemoryResponse(
            summary="No user session provided",
            active_monitoring=[],
            plan_status="unknown"
        )
    
    memory_data = event_service.get_ai_memory(user_session, db)
    return AIMemoryResponse(**memory_data)

@app.get("/api/gallery/images", response_model=GalleryResponse)
async def get_gallery_images(db: Session = Depends(get_db)):
    """Get gallery content"""
    if not gallery_service:
        return GalleryResponse(images=[], message="Gallery service unavailable")
    
    result = await gallery_service.get_gallery_images(db)
    return GalleryResponse(**result)

@app.get("/api/gallery/search-style/{style}", response_model=GalleryResponse)
async def search_by_style(style: str, count: int = 12):
    """Search images by style using Unsplash"""
    if not gallery_service:
        return GalleryResponse(images=[], style=style, message="Gallery service unavailable")
    
    result = await gallery_service.search_by_style(style, count)
    return GalleryResponse(**result)

@app.post("/api/generate-pdf/{chat_id}")
async def generate_event_plan_pdf(
    chat_id: str,
    db: Session = Depends(get_db)
):
    """Generate comprehensive event plan PDF"""
    try:
        # Get chat session and plan data
        chat_session = db.query(ChatSession).filter(ChatSession.session_id == chat_id).first()
        if not chat_session:
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # Get event data from plan sessions
        from database import PlanSession
        plan_session = db.query(PlanSession).filter(PlanSession.user_session == chat_session.user_session).first()
        
        if not plan_session or not plan_session.generated_content:
            raise HTTPException(status_code=400, detail="No generated content found for this event")
        
        # Extract event data
        event_data = {
            'event_type': plan_session.event_context.get('event_type', 'Event'),
            'location': plan_session.event_context.get('location', 'Not specified'),
            'guest_count': plan_session.event_context.get('guest_count', 'Not specified'),
            'budget': plan_session.event_context.get('budget', 'Not specified'),
            'meal_type': plan_session.event_context.get('meal_type', 'Not specified'),
            'dietary_restrictions': plan_session.event_context.get('dietary_restrictions', 'None')
        }
        
        # Extract user selections (generated content)
        user_selections = {
            'music': plan_session.generated_content.get('music', []),
            'venues': plan_session.generated_content.get('venues', []),
            'food': plan_session.generated_content.get('food', [])
        }
        
        # Generate PDF
        pdf_bytes = await pdf_service.generate_event_plan_pdf(event_data, user_selections)
        
        # Return PDF as response
        from fastapi.responses import Response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=event_plan_{chat_id}.pdf"
            }
        )
        
    except Exception as e:
        print(f"Error generating PDF: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error generating PDF: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3001)