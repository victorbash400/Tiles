# AI Services Migration

This document describes the migration from Gemini to GPT-4.1 nano and GetImg.ai Absolute Reality v1.8.1.

## Changes Made

### 1. Text Generation: Gemini → GPT-4.1 nano

**Before:**
- Used Google Gemini 1.5 Flash model
- Multiple API keys with rotation
- `google-generativeai` library

**After:**
- Uses OpenAI GPT-4.1 nano model
- Single API key
- Direct HTTP requests to OpenAI API

### 2. Image Generation: Unsplash API → GetImg.ai Absolute Reality v1.8.1

**Before:**
- Fetched real photos from Unsplash
- Search-based image retrieval
- Limited to existing photographs

**After:**
- Generates AI images using stable diffusion
- Absolute Reality v1.8.1 model for photorealistic results
- Custom prompts for event-specific imagery
- Generates 10 images per request (no Unsplash fallback)

### 3. Updated Files

- `ai_services.py` - Complete rewrite with new AI services
- `main_enhanced.py` - Updated to use new service classes
- `requirements.txt` - Replaced `google-generativeai` with `openai`

## Environment Variables

Update your `.env` file with:

```bash
# Required for GPT-4.1 nano
OPENAI_API_KEY=your_openai_api_key_here

# Required for GetImg.ai Absolute Reality v1.8.1 (fallback provided)
GETIMG_API_KEY=your_getimg_api_key_here

# Optional: Keep Unsplash keys for backup
UNSPLASH_ACCESS_KEY_1=your_unsplash_key_1
UNSPLASH_ACCESS_KEY_2=your_unsplash_key_2

# Music service (unchanged)
QLOO_API_KEY=your_qloo_api_key_here
```

## API Endpoints Used

### GPT-4.1 nano
- **Endpoint:** `https://api.openai.com/v1/chat/completions`
- **Model:** `gpt-4.1-nano`
- **Features:** Fast response, low cost, high quality

### GetImg.ai Absolute Reality v1.8.1
- **Endpoint:** `https://api.getimg.ai/v1/stable-diffusion/text-to-image`
- **Model:** `absolute-reality-v1-8-1`
- **Settings:**
  - Width: 512px
  - Height: 512px
  - Steps: 4
  - Guidance: 1.0
  - Count: 10 images per generation

## Testing

Run the test script to verify everything works:

```bash
cd mockapi
python test_new_ai.py
```

## Migration Benefits

1. **Better Text Quality:** GPT-4.1 nano provides more coherent and contextual responses
2. **Photorealistic Image Generation:** Absolute Reality v1.8.1 creates highly realistic event imagery
3. **Faster Processing:** GPT-4.1 nano is optimized for speed
4. **Better Event Matching:** Generated images match exact event requirements
5. **More Images:** 10 high-quality AI images per generation (no stock photos)

## Installation

1. Install new dependencies:
```bash
pip install -r requirements.txt
```

2. Update environment variables in `.env`

3. Test the services:
```bash
python test_new_ai.py
```

4. Start the server:
```bash
python main_enhanced.py
```

## API Response Format

The new services maintain the same response format as before for compatibility, but now include:

- **Generated Images:** Base64-encoded PNG images from stable diffusion
- **AI Metadata:** Includes seed, cost, and generation prompt
- **Type Indicators:** Images marked as "generated" vs "photo"
- **Fallback Handling:** Automatic fallback to Unsplash if needed