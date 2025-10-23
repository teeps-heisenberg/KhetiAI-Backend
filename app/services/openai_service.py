"""
OpenAI service for chat completions, audio processing, and vision analysis
"""

import os
import tempfile
from typing import Optional, Dict, Any, List
from openai import OpenAI
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import io
import base64
import json

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
    
    async def analyze_crop_image(
        self, 
        image_base64: str, 
        context_text: str,
        language: str = "en",
        user_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze crop image using OpenAI Vision API with preprocessed context
        
        Args:
            image_base64: Base64 encoded image
            context_text: Preprocessed context from OpenCV analysis
            language: Language for response
            user_message: Optional user message/question about the image
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Create prompt based on language and include user message if provided
            user_question = ""
            if user_message and user_message.strip():
                user_question = f"\n\nUser Question: {user_message.strip()}"
            
            prompts = {
                "en": f"""You are an expert agricultural AI analyzing a crop image. 

{context_text}{user_question}

Based on the image and the technical analysis above, please provide:
1. Overall health score (0-100)
2. Growth stage (Seedling/Vegetative/Flowering/Fruiting/Mature)
3. Any diseases detected (name and confidence level)
4. Specific recommendations for the farmer
{f"5. Address the user's specific question: {user_message.strip()}" if user_message and user_message.strip() else ""}

Format your response as JSON with these exact keys:
{{
    "health_score": <number 0-100>,
    "growth_stage": "<stage>",
    "disease_detected": "<disease name or null>",
    "disease_confidence": <number 0-1 or null>,
    "recommendations": "<detailed recommendations>"
}}""",
                "ur": f"""آپ ایک ماہر زرعی AI ہیں جو فصل کی تصویر کا تجزیہ کر رہے ہیں۔

{context_text}{user_question}

تصویر اور اوپر دیے گئے تکنیکی تجزیے کی بنیاد پر، براہ کرم فراہم کریں:
1. مجموعی صحت کا اسکور (0-100)
2. نمو کا مرحلہ (پودا/نباتاتی/پھول/پھل/بالغ)
3. کوئی بیماری کا پتہ چلا (نام اور اعتماد کی سطح)
4. کسان کے لیے مخصوص سفارشات
{f"5. صارف کے مخصوص سوال کا جواب دیں: {user_message.strip()}" if user_message and user_message.strip() else ""}

اپنا جواب JSON کی شکل میں ان عین کلیدوں کے ساتھ دیں:
{{
    "health_score": <نمبر 0-100>,
    "growth_stage": "<مرحلہ>",
    "disease_detected": "<بیماری کا نام یا null>",
    "disease_confidence": <نمبر 0-1 یا null>,
    "recommendations": "<تفصیلی سفارشات>"
}}"""
            }
            
            prompt = prompts.get(language, prompts["en"])
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 with vision capabilities
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000,
                temperature=0.3  # Lower temperature for more consistent analysis
            )
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            try:
                # Find JSON in the response
                start_idx = content.find('{')
                end_idx = content.rfind('}') + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = content[start_idx:end_idx]
                    analysis_result = json.loads(json_str)
                else:
                    # Fallback if JSON not found
                    analysis_result = self._parse_text_response(content)
            except json.JSONDecodeError:
                # Fallback parsing
                analysis_result = self._parse_text_response(content)
            
            return analysis_result
            
        except Exception as e:
            raise Exception(f"Vision API error: {str(e)}")
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """
        Fallback parser for non-JSON responses
        
        Args:
            content: Raw text response from API
            
        Returns:
            Dictionary with parsed values
        """
        # Simple fallback - return the content as recommendations
        return {
            "health_score": 75.0,
            "growth_stage": "Unknown",
            "disease_detected": None,
            "disease_confidence": None,
            "recommendations": content
        }
