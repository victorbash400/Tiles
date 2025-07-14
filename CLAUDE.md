# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a full-stack application called "Tiles" that consists of:
- **Frontend**: React + Vite application (`tiles-frontend/`) with a gallery interface and chat functionality
- **Backend**: FastAPI server (`mockapi/main.py`) that serves as a mock API for chat and gallery operations

The app displays a Pinterest-style image gallery with an AI chat interface that can control and interact with the gallery content.

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
- `UNSPLASH_ACCESS_KEY`: Unsplash API key for fetching gallery images

## Architecture

### Frontend Structure
- **App.jsx**: Main application component managing sidebar and chat area state
- **components/sidebar/**: Sidebar navigation for chat history
- **components/chat/**: Chat interface components including MainChatArea (gallery display), modal, and chat bubbles
- **services/MainChatArea-api.js**: API service layer for all backend communication

### Backend Structure
- **FastAPI application** with CORS middleware for frontend communication
- **Chat endpoints** (`/api/chats/*`): CRUD operations for chat sessions and messages
- **Gallery endpoints** (`/api/gallery/*`): Image fetching from Unsplash API with orientation and search filters
- **AI endpoints** (`/api/ai/*`): Mock AI memory and personalization features

### Key Technologies
- **Frontend**: React 19, Vite, TailwindCSS, Framer Motion, Lucide React icons, Axios
- **Backend**: FastAPI, Pydantic, httpx, python-dotenv
- **API Integration**: Unsplash API for image gallery content

### Data Flow
1. MainChatArea fetches images from `/api/gallery/images` on component mount
2. Chat interactions go through `/api/chats/{chat_id}/messages` which returns simulated AI responses
3. Gallery can be filtered by orientation or search query through respective endpoints
4. All API calls use environment variable `VITE_API_URL` (defaults to `http://localhost:3001/api`)

### State Management
- React useState hooks for local component state
- No global state management library used
- Chat state persisted via backend API calls

## Code Conventions
- Uses modern React patterns with hooks
- PropTypes for component prop validation
- ESLint configuration with React-specific rules
- TailwindCSS for styling with utility classes
- Responsive design with mobile-first approach using Tailwind breakpoints