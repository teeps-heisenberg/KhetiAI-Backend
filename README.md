# KhetiAI Backend

Agricultural AI Assistant Backend Service built with FastAPI.

## Features

- **Chat API**: Handle voice and text messages with AI responses
- **Crop Analysis**: Image upload and AI-powered crop health analysis
- **Multi-language Support**: English and Urdu language support
- **RESTful API**: Clean, documented API endpoints
- **CORS Support**: Configured for frontend integration
- **Supabase Ready**: Prepared for future Supabase integration

## Project Structure

```
KhetiAI-Backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── health.py      # Health check endpoints
│   │       │   ├── chat.py        # Chat and conversation endpoints
│   │       │   └── crop_analysis.py # Crop analysis endpoints
│   │       └── api.py             # Main API router
│   ├── core/
│   │   └── config.py              # Application configuration
│   └── services/                  # Business logic services
│       └── openai_service.py      # OpenAI integration service
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── env.example                    # Environment variables template
└── README.md                      # This file
```

## Quick Start

### 1. Install Dependencies

```bash
# Activate your virtual environment first
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp env.example .env

# Edit .env file with your configuration
```

### 3. Run the Application

```bash
# Option 1: Using uvicorn directly (Recommended)
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using python main.py
python main.py

# Option 3: Production mode
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Health Check
- `GET /` - Root endpoint
- `GET /health` - Basic health check
- `GET /api/v1/health/` - Detailed health check

### Chat
- `POST /api/v1/chat/message` - Send text chat message (returns text + optional audio)
- `POST /api/v1/chat/voice` - Send voice message (returns transcript + response + audio)
- `POST /api/v1/chat/conversation` - Create new conversation
- `GET /api/v1/chat/conversations` - Get all conversations
- `GET /api/v1/chat/conversation/{id}` - Get specific conversation

### Crop Analysis
- `POST /api/v1/crop-analysis/analyze` - Analyze crop image directly

## Development

### Adding New Endpoints

1. Create a new file in `app/api/v1/endpoints/`
2. Define your router and endpoints
3. Import and include the router in `app/api/v1/api.py`

### Database Models

Database models will be added in the `app/models/` directory as we implement features.

### Services

Business logic will be implemented in the `app/services/` directory.

## Configuration

The application uses environment variables for configuration. See `env.example` for available options.

## Features Implemented

✅ **OpenAI Integration**: Chat completions with GPT-3.5-turbo
✅ **Voice Processing**: Speech-to-text and text-to-speech
✅ **Multi-language Support**: English and Urdu
✅ **Audio Response**: Base64 encoded audio for voice interactions
✅ **Crop Analysis**: Image upload and mock analysis
✅ **RESTful API**: Clean, documented endpoints

## Next Steps

1. Set up Supabase integration for database and authentication
2. Add OpenAI Vision API for actual crop analysis
3. Add file storage for uploaded images
4. Add comprehensive error handling and logging
5. Implement conversation history persistence with Supabase
6. Add user management and authentication

## License

This project is part of the KhetiAI agricultural assistance platform.
