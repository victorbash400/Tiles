# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Tiles** is an AI-powered visual discovery platform built for the **Qloo AI Hackathon**. It showcases the future of intelligent content discovery and personalization by combining cultural intelligence with modern full-stack development.

### Core Components
- **Frontend**: React 19 + Vite application (`tiles-frontend/`) with Pinterest-style gallery and conversational AI interface
- **Backend**: FastAPI server (`mockapi/`) with modular service architecture for AI-powered event planning

### What Makes This Special
This isn't just another gallery app - it's a **smart event planning platform** that:
- Uses **conversational AI** to naturally collect event details (location, guest count, budget, style preferences)
- Leverages **Qloo AI's cultural intelligence** for music and venue recommendations
- Generates **custom event imagery** using Azure DALL-E 3
- Provides **contextual recommendations** based on location, culture, and preferences
- Adapts to user behavior through **intelligent memory systems**

## Development Commands

### Frontend (tiles-frontend/)
```bash
cd tiles-frontend
npm install          # Install dependencies
npm run dev          # Start development server (default: http://localhost:5173)
npm run build        # Build for production
npm run preview      # Preview production build
npm run lint         # Run ESLint
```

### Backend (mockapi/)
```bash
cd mockapi
python main.py       # Start FastAPI server on port 3001
```

Required environment variables for backend:
- `OPENAI_API_KEY`: OpenAI API key for conversational AI and data collection
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key for DALL-E 3 image generation
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint URL
- `QLOO_API_KEY`: Qloo AI API key for cultural intelligence and recommendations
- `QLOO_API_URL`: Qloo API endpoint (default: https://hackathon.api.qloo.com/)
- `YOUTUBE_API_KEY`: YouTube API key for music playlist integration
- `UNSPLASH_ACCESS_KEY`: Unsplash API key for supplementary gallery images

## Architecture

### Frontend Structure
- **App.jsx**: Main application component managing sidebar and chat area state
- **components/sidebar/**: Sidebar navigation for chat history
- **components/chat/**: Chat interface components including MainChatArea (gallery display), modal, and chat bubbles
- **services/MainChatArea-api.js**: API service layer for all backend communication

### Backend Structure (Modular Service Architecture)

#### Core Services
- **AIService** (`ai_services.py`): Conversational AI responses and DALL-E 3 image generation
- **DataCollectionService** (`data_collection_service.py`): Smart event data collection and validation
- **QlooMusicService** (`qloo_music_service.py`): Cultural music recommendations via Qloo + YouTube
- **QlooVenueService** (`qloo_venue_service.py`): Intelligent venue recommendations using Qloo
- **UnsplashService** (`unsplash_service.py`): Supplementary image fetching
- **PromptService** (`prompt_service.py`): Advanced prompt engineering and context analysis

#### Business Logic
- **EventService** (`event_service.py`): Orchestrates event planning workflow and content generation
- **ChatService** (`chat_service.py`): Manages chat sessions and conversation flow
- **GalleryService** (`gallery_service.py`): Handles gallery content and user interactions

#### Data Layer
- **Database** (`database.py`): SQLite with user memory, chat sessions, and plan tracking
- **Models** (`models.py`): Pydantic models for API requests and responses

#### API Endpoints
- **Chat endpoints** (`/api/chats/*`): Conversational AI for event planning
- **Gallery endpoints** (`/api/gallery/*`): AI-generated and curated image content
- **AI endpoints** (`/api/ai/*`): Memory systems and personalization features

### Key Technologies
- **Frontend**: React 19, Vite, TailwindCSS, Framer Motion, Lucide React icons, Axios
- **Backend**: FastAPI, Pydantic, httpx, python-dotenv, SQLite
- **AI Integration**: 
  - OpenAI GPT-3.5-turbo for conversational AI
  - Azure DALL-E 3 for custom image generation
  - Qloo AI for cultural intelligence and recommendations
- **API Integration**: YouTube API, Unsplash API, Qloo Hackathon API

### AI-Powered Event Planning Flow
1. **User Interaction**: User starts conversation about event planning
2. **Data Collection**: DataCollectionService naturally extracts event details through conversation
3. **Content Generation**: When ready, system generates:
   - **Custom Images**: DALL-E 3 creates event-specific imagery
   - **Music Recommendations**: Qloo AI finds culturally relevant music via YouTube
   - **Venue Suggestions**: Qloo AI recommends appropriate venues based on location/event type
4. **Gallery Display**: Generated content appears in Pinterest-style gallery
5. **Memory System**: User preferences learned and stored for future interactions
6. **Iterative Refinement**: User can refine preferences to get better recommendations

### State Management
- **Frontend**: React useState hooks for local component state
- **Backend**: SQLite database with user memory, chat sessions, and plan tracking
- **AI Memory**: Persistent learning of user preferences and behavior patterns
- **Chat Persistence**: Full conversation history maintained across sessions

## Qloo AI Integration Highlights

### Cultural Intelligence
- **Location-Aware Recommendations**: Understands cultural preferences by geography
- **Event-Specific Curation**: Tailors music and venues to event type and cultural context
- **Cross-Domain Intelligence**: Connects insights across music, venues, and cultural trends

### Smart Data Collection
- **Conversational Extraction**: Natural language processing to extract event details
- **Context-Aware Validation**: Ensures data quality and completeness
- **Progressive Enhancement**: Builds detailed event profiles through conversation

### Advanced Features
- **Contextual Search**: Generates smart search queries based on cultural understanding
- **Fallback Strategies**: Robust error handling with multiple recommendation sources
- **Real-time Adaptation**: Adjusts recommendations based on user feedback

## Code Conventions
- **Modular Architecture**: Each service has single responsibility
- **Clean Separation**: Business logic separated from data access and API layers
- **Type Safety**: Pydantic models for data validation and serialization
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Performance**: Async/await patterns for optimal API performance
- **Modern React**: Hooks, functional components, and latest React 19 features
- **Responsive Design**: Mobile-first approach with TailwindCSS utility classes