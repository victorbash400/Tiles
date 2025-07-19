from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import asyncio
import os
from dotenv import load_dotenv
# from sqlalchemy.orm import Session

# Import database and models
from dynamodb_database import create_tables, get_db, ChatSession

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

# Create database tables on startup (disabled for Lambda)
# @app.on_event("startup")
# async def startup_event():
#     # Clear database on startup for fresh sessions
#     db_path = "tiles_events.db"
#     if os.path.exists(db_path):
#         os.remove(db_path)
#         print("🗑️ Cleared previous database")
#     
#     create_tables()
#     print("✅ Database tables created")
#     print("🧠 AI-powered plan management system initialized")

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

@app.post("/api/admin/clear-database")
async def clear_database():
    """Clear all database tables - for demo/development use only"""
    try:
        from dynamodb_database import clear_all_tables
        clear_all_tables()
        return {"message": "Database cleared successfully", "status": "success"}
    except Exception as e:
        return {"message": f"Error clearing database: {str(e)}", "status": "error"}

@app.get("/api/admin/database-status")
async def database_status():
    """Check database status and item counts"""
    try:
        from dynamodb_database import dynamodb, USER_MEMORY_TABLE, CHAT_SESSIONS_TABLE, CHAT_MESSAGES_TABLE, PLAN_SESSIONS_TABLE
        
        tables = [
            (USER_MEMORY_TABLE, "user_memory"),
            (CHAT_SESSIONS_TABLE, "chat_sessions"), 
            (CHAT_MESSAGES_TABLE, "chat_messages"),
            (PLAN_SESSIONS_TABLE, "plan_sessions")
        ]
        
        status = {}
        for table_name, friendly_name in tables:
            try:
                table = dynamodb.Table(table_name)
                response = table.scan(Select='COUNT')
                status[friendly_name] = response['Count']
            except Exception as e:
                status[friendly_name] = f"Error: {str(e)}"
        
        return {"status": "success", "tables": status}
    except Exception as e:
        return {"message": f"Error checking database status: {str(e)}", "status": "error"}

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
async def get_all_chats(db = Depends(get_db)):
    """Get all chat sessions"""
    return chat_service.get_all_chats(db)

@app.post("/api/chats", response_model=ChatSessionResponse)
async def create_new_chat(db = Depends(get_db)):
    """Create a new chat session"""
    return chat_service.create_new_chat(db)

@app.get("/api/chats/{chat_id}", response_model=ChatSessionResponse)
async def get_chat_by_id(chat_id: str, db = Depends(get_db)):
    """Get a specific chat session"""
    result = chat_service.get_chat_by_id(chat_id, db)
    if not result:
        raise HTTPException(status_code=404, detail="Chat not found")
    return result

@app.post("/api/chats/{chat_id}/messages", response_model=MessageResponse)
async def send_message_and_get_ai_response(
    chat_id: str, 
    message_data: MessageCreate, 
    db = Depends(get_db)
):
    """Send a message and get AI response with intelligent event planning"""
    
    # Get or create chat session
    session = db.query(ChatSession).filter({'session_id': chat_id}).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat not found")
    
    print(f"🔍 Processing message for chat_id: {chat_id}")
    print(f"🔍 Found session with id: {session.id}, session_id: {session.session_id}")
    
    try:
        # Save user message
        print(f"💾 Saving user message with chat_session_id: {session.id}")
        chat_service.save_user_message(session.id, message_data.content, db)
        
        # Build conversation history
        print(f"📚 Building conversation history for session.id: {session.id}")
        conversation_history = chat_service.build_conversation_history(session, db)
        print(f"📚 Found {len(conversation_history)} messages in history")
        
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
        
        # Debug: Log what's being sent to frontend
        response_data = {
            "image_data": ai_suggestions.get("image_data", []),
            "music_data": ai_suggestions.get("music_data", []),
            "venue_data": ai_suggestions.get("venue_data", []),
            "food_data": ai_suggestions.get("food_data", []),
            "refresh_gallery": ai_suggestions.get("refresh_gallery", False)
        }
        print(f"🚀 Final response to frontend:")
        print(f"   - image_data: {len(response_data['image_data'])} items")
        print(f"   - music_data: {len(response_data['music_data'])} items")
        print(f"   - venue_data: {len(response_data['venue_data'])} items")
        print(f"   - food_data: {len(response_data['food_data'])} items")
        print(f"   - refresh_gallery: {response_data['refresh_gallery']}")
        
        # **FIX**: Sync refresh_gallery from response_data to ai_suggestions
        ai_suggestions["refresh_gallery"] = response_data["refresh_gallery"]
        print(f"🔧 PRESERVED: ai_suggestions.refresh_gallery = {ai_suggestions['refresh_gallery']}")
        
        return MessageResponse(
            id=ai_message.id,
            content=ai_message.content,
            role=ai_message.role,
            timestamp=ai_message.timestamp.strftime("%H:%M"),
            ai_suggestions=ai_suggestions,
            image_data=response_data["image_data"],
            music_data=response_data["music_data"],
            venue_data=response_data["venue_data"],
            food_data=response_data["food_data"]
        )
        
    except Exception as e:
        # db.rollback()  # DynamoDB doesn't need rollback
        print(f"Error processing message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@app.get("/api/ai/memory", response_model=AIMemoryResponse)
async def get_ai_memory(user_session: str = None, db = Depends(get_db)):
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
async def get_gallery_images(chat_session_id: str = None, db = Depends(get_db)):
    """Get gallery content, optionally filtered by chat session"""
    if not gallery_service:
        return GalleryResponse(images=[], message="Gallery service unavailable")
    
    result = await gallery_service.get_gallery_images(db, chat_session_id)
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
    db = Depends(get_db)
):
    """Generate comprehensive event plan PDF"""
    try:
        print(f"🔍 PDF request for chat_id: {chat_id}")
        # Get chat session and plan data
        chat_session = db.query(ChatSession).filter({'session_id': chat_id}).first()
        if not chat_session:
            print(f"❌ No chat session found for ID: {chat_id}")
            # List available sessions for debugging
            available_sessions = db.query(ChatSession).all()
            print(f"🔍 Available sessions: {[s.session_id for s in available_sessions]}")
            raise HTTPException(status_code=404, detail="Chat session not found")
        
        # **NEW**: Get event data from memory store instead of DynamoDB
        from memory_store import memory_store
        
        # Get session summary to check if data exists
        session_summary = memory_store.get_session_summary(chat_id)
        if not session_summary["exists"]:
            print(f"❌ No session data found in memory for chat_id: {chat_id}")
            raise HTTPException(status_code=400, detail="No event data found for this session")
        
        # Get extracted event data from memory
        extracted_data = memory_store.get_extracted_data(chat_id)
        if not extracted_data:
            print(f"❌ No extracted event data found in memory")
            raise HTTPException(status_code=400, detail="No event details collected yet")
        
        print(f"🔍 Memory extracted data: {extracted_data}")
        
        event_data = {
            'event_type': extracted_data.get('event_type', 'Event'),
            'location': extracted_data.get('location', 'Not specified'),
            'guest_count': extracted_data.get('guest_count', 'Not specified'),
            'budget': extracted_data.get('budget', 'Not specified'),
            'meal_type': extracted_data.get('meal_type', 'Not specified'),
            'dietary_restrictions': extracted_data.get('dietary_restrictions', 'None')
        }
        
        # Get generated content from memory
        generated_content = memory_store.get_generated_content(chat_id)
        user_selections = {
            'music': generated_content.get('music', []),
            'venues': generated_content.get('venues', []),
            'food': generated_content.get('food', [])
        }
        
        print(f"🔍 Generated content counts: music={len(user_selections['music'])}, venues={len(user_selections['venues'])}, food={len(user_selections['food'])}")
        
        # Check if we have any content to put in PDF
        total_content = len(user_selections['music']) + len(user_selections['venues']) + len(user_selections['food'])
        if total_content == 0:
            print(f"❌ No generated content found for PDF")
            raise HTTPException(status_code=400, detail="No recommendations generated yet. Please generate content first.")
        
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