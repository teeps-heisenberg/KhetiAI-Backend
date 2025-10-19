"""
Chat endpoints for voice and text communication
"""

from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import uuid

from app.services.openai_service import OpenAIService

router = APIRouter()
openai_service = OpenAIService()

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    message_type: str = "text"  # text, voice
    language: str = "en"  # en, ur
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    message_id: str
    timestamp: datetime
    language: str
    audio_response: Optional[str] = None  # Base64 encoded audio

class VoiceChatRequest(BaseModel):
    language: str = "en"
    conversation_id: Optional[str] = None

class VoiceChatResponse(BaseModel):
    transcript: str
    response: str
    message_id: str
    timestamp: datetime
    language: str
    audio_response: str  # Base64 encoded audio

class ConversationCreate(BaseModel):
    title: Optional[str] = None
    language: str = "en"

class ConversationResponse(BaseModel):
    id: str
    title: Optional[str]
    language: str
    created_at: datetime
    message_count: int = 0

@router.post("/message", response_model=ChatResponse)
async def send_message(message: ChatMessage):
    """
    Send a chat message (text or voice transcript)
    """
    try:
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "user",
                "content": message.message
            }
        ]
        
        # Get AI response
        response_text = await openai_service.get_chat_completion(
            messages=messages,
            language=message.language
        )
        
        # Generate audio response for voice messages
        audio_response = None
        if message.message_type == "voice":
            audio_bytes = await openai_service.text_to_speech(
                text=response_text,
                language=message.language
            )
            audio_response = openai_service.get_audio_base64(audio_bytes)
        
        return ChatResponse(
            response=response_text,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            language=message.language,
            audio_response=audio_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/voice", response_model=VoiceChatResponse)
async def process_voice_input(
    audio_file: UploadFile = File(...),
    language: str = "en",
    conversation_id: Optional[str] = None
):
    """
    Process voice input and return both transcript and AI response with audio
    """
    try:
        # Validate file type
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(
                status_code=400,
                detail="File must be an audio file"
            )
        
        # Read audio file
        audio_bytes = await audio_file.read()
        
        # Convert speech to text
        transcript = await openai_service.speech_to_text(audio_bytes)
        
        if not transcript.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not transcribe audio. Please try again."
            )
        
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "user",
                "content": transcript
            }
        ]
        
        # Get AI response
        response_text = await openai_service.get_chat_completion(
            messages=messages,
            language=language
        )
        
        # Generate audio response
        audio_bytes = await openai_service.text_to_speech(
            text=response_text,
            language=language
        )
        audio_response = openai_service.get_audio_base64(audio_bytes)
        
        return VoiceChatResponse(
            transcript=transcript,
            response=response_text,
            message_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            language=language,
            audio_response=audio_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing voice input: {str(e)}")

@router.post("/conversation", response_model=ConversationResponse)
async def create_conversation(conversation: ConversationCreate):
    """
    Create a new conversation
    """
    try:
        conversation_id = str(uuid.uuid4())
        
        return ConversationResponse(
            id=conversation_id,
            title=conversation.title or f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            language=conversation.language,
            created_at=datetime.now(),
            message_count=0
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating conversation: {str(e)}")

@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations():
    """
    Get all conversations for the current user
    """
    try:
        # TODO: Implement actual conversation retrieval with database
        return []
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversations: {str(e)}")

@router.get("/conversation/{conversation_id}")
async def get_conversation(conversation_id: str):
    """
    Get a specific conversation with its messages
    """
    try:
        # TODO: Implement actual conversation retrieval with database
        return {
            "id": conversation_id,
            "title": "Sample Conversation",
            "language": "en",
            "created_at": datetime.now(),
            "messages": []
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving conversation: {str(e)}")
