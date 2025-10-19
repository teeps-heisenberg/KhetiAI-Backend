"""
OpenAI service for chat completions and audio processing
"""

import os
import tempfile
from typing import Optional, Dict, Any
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import base64

from app.core.config import settings

class OpenAIService:
    """Service for OpenAI integration"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def get_chat_completion(
        self, 
        messages: list, 
        language: str = "en",
        temperature: float = 0.7
    ) -> str:
        """
        Get chat completion from OpenAI
        """
        try:
            # Add system message for agricultural context
            system_message = self._get_system_message(language)
            full_messages = [system_message] + messages
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                temperature=temperature,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def _get_system_message(self, language: str) -> Dict[str, str]:
        """Get system message based on language"""
        system_messages = {
            "en": {
                "role": "system",
                "content": """You are KhetiAI, an intelligent agricultural assistant. You help farmers with:
                - Crop health analysis and recommendations
                - Weather-based farming advice
                - Soil management guidance
                - Pest and disease identification
                - Optimal planting and harvesting times
                - Sustainable farming practices
                
                Always provide practical, actionable advice in a friendly, supportive tone. 
                If you don't know something, admit it and suggest consulting local agricultural experts."""
            },
            "ur": {
                "role": "system", 
                "content": """آپ کھیتی اے آئی ہیں، ایک ذہین زرعی معاون۔ آپ کسانوں کی مدد کرتے ہیں:
                - فصل کی صحت کا تجزیہ اور سفارشات
                - موسم کی بنیاد پر کاشتکاری کا مشورہ
                - مٹی کی دیکھ بھال کی رہنمائی
                - کیڑوں اور بیماریوں کی شناخت
                - بہترین بوائی اور کٹائی کے اوقات
                - پائیدار کاشتکاری کے طریقے
                
                ہمیشہ عملی، قابل عمل مشورے دوستانہ اور مددگار انداز میں دیں۔
                اگر آپ کچھ نہیں جانتے تو اس کا اعتراف کریں اور مقامی زرعی ماہرین سے مشورہ کرنے کی تجویز دیں۔"""
            }
        }
        
        return system_messages.get(language, system_messages["en"])
    
    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech using gTTS
        """
        try:
            # Map language codes for gTTS
            lang_map = {
                "en": "en",
                "ur": "ur"
            }
            
            tts_lang = lang_map.get(language, "en")
            
            # Create gTTS object
            tts = gTTS(text=text, lang=tts_lang, slow=False)
            
            # Save to bytes
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            return audio_buffer.getvalue()
            
        except Exception as e:
            raise Exception(f"Text-to-speech error: {str(e)}")
    
    async def speech_to_text(self, audio_file: bytes) -> str:
        """
        Convert speech to text using OpenAI Whisper
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_file)
                temp_file_path = temp_file.name
            
            # Transcribe using OpenAI Whisper
            with open(temp_file_path, "rb") as audio_file_obj:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file_obj
                )
            
            # Clean up temporary file
            os.unlink(temp_file_path)
            
            return transcript.text
            
        except Exception as e:
            raise Exception(f"Speech-to-text error: {str(e)}")
    
    def get_audio_base64(self, audio_bytes: bytes) -> str:
        """
        Convert audio bytes to base64 string for frontend
        """
        return base64.b64encode(audio_bytes).decode('utf-8')
