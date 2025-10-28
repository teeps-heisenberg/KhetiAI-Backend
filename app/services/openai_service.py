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
                "content": """You are KhetiAI, an expert agricultural assistant specialized in Pakistani agriculture. You help farmers in Pakistan with:
                - Crop health analysis and recommendations for Pakistani crops (wheat, rice, cotton, sugarcane, maize, etc.)
                - Weather-based farming advice specific to Pakistan's climate zones (Punjab, Sindh, KPK, Balochistan)
                - Soil management guidance for Pakistani soil types
                - Pest and disease identification common in Pakistan
                - Optimal planting and harvesting times according to Pakistani seasons (Rabi and Kharif crops)
                - Water management strategies for Pakistan's irrigation systems
                - Fertilizer recommendations based on Pakistani market availability
                - Sustainable farming practices suitable for Pakistani conditions
                
                Consider Pakistan-specific factors:
                - Climate: Hot summers, monsoon rains, mild winters
                - Main crops: Wheat, rice (basmati), cotton, sugarcane, maize
                - Irrigation: Canal systems, tube wells
                - Soil types: Alluvial, loess, sandy
                - Local agricultural practices and terminology
                
                Always provide practical, actionable advice in a friendly, supportive tone. 
                When suggesting inputs, consider availability and affordability in Pakistan.
                If you don't know something, admit it and suggest consulting local agricultural extension services or PARC (Pakistan Agricultural Research Council).
                
                IMPORTANT: Format your responses using Markdown for better readability:
                - Use **bold** for important points
                - Use ### for section headings
                - Use bullet points (-) or numbered lists for recommendations
                - Use code blocks for specific values or measurements"""
            },
            "ur": {
                "role": "system", 
                "content": """آپ کھیتی اے آئی ہیں، پاکستانی زراعت میں ماہر زرعی معاون۔ آپ پاکستان میں کسانوں کی مدد کرتے ہیں:
                - پاکستانی فصلوں کی صحت کا تجزیہ اور سفارشات (گندم، چاول، کپاس، گنا، مکئی وغیرہ)
                - پاکستان کے موسمی علاقوں کے لیے موسم کی بنیاد پر کاشتکاری کا مشورہ (پنجاب، سندھ، خیبر پختونخوا، بلوچستان)
                - پاکستانی مٹی کی اقسام کے لیے مٹی کی دیکھ بھال کی رہنمائی
                - پاکستان میں عام کیڑوں اور بیماریوں کی شناخت
                - پاکستانی موسموں کے مطابق بہترین بوائی اور کٹائی کے اوقات (ربیع اور خریف کی فصلیں)
                - پاکستان کے آبپاشی نظام کے لیے پانی کے انتظام کی حکمت عملی
                - پاکستانی منڈی میں دستیابی کی بنیاد پر کھاد کی سفارشات
                - پاکستانی حالات کے لیے موزوں پائیدار کاشتکاری کے طریقے
                
                پاکستان کے خاص عوامل کو مدنظر رکھیں:
                - آب و ہوا: گرم گرمیاں، مانسون کی بارشیں، ہلکی سردیاں
                - اہم فصلیں: گندم، چاول (باسمتی)، کپاس، گنا، مکئی
                - آبپاشی: نہری نظام، ٹیوب ویل
                - مٹی کی اقسام: جلوڑی، لوس، ریتلی
                - مقامی زرعی طریقے اور اصطلاحات
                
                ہمیشہ عملی، قابل عمل مشورے دوستانہ اور مددگار انداز میں دیں۔
                جب کوئی چیز تجویز کریں تو پاکستان میں دستیابی اور استطاعت کو مدنظر رکھیں۔
                اگر آپ کچھ نہیں جانتے تو اس کا اعتراف کریں اور مقامی زرعی توسیعی خدمات یا پارک (پاکستان ایگریکلچرل ریسرچ کونسل) سے مشورہ کرنے کی تجویز دیں۔
                
                اہم: بہتر پڑھنے کے لیے اپنے جوابات کو Markdown استعمال کرتے ہوئے فارمیٹ کریں:
                - اہم نکات کے لیے **بولد** استعمال کریں
                - ابواب کے لیے ### استعمال کریں
                - سفارشات کے لیے bullet points (-) یا نمبر والی فہرستیں استعمال کریں
                - مخصوص قیمتوں یا پیمائشوں کے لیے code blocks استعمال کریں"""
            }
        }
        
        return system_messages.get(language, system_messages["en"])
    
    async def text_to_speech(self, text: str, language: str = "en") -> bytes:
        """
        Convert text to speech using OpenAI TTS API for better accent support
        """
        try:
            # Map language codes to OpenAI voice selection
            # OpenAI TTS supports multiple voices with natural accents
            voice_map = {
                "en": "nova",  # Professional, clear English voice
                "ur": "shimmer"  # Good for Urdu with better pronunciation
            }
            
            voice = voice_map.get(language, "nova")
            
            # Use OpenAI TTS API for better quality and accent support
            response = self.client.audio.speech.create(
                model="tts-1",  # or "tts-1-hd" for higher quality
                voice=voice,
                input=text
            )
            
            # Convert to bytes
            audio_bytes = b""
            for chunk in response.iter_bytes():
                audio_bytes += chunk
            
            return audio_bytes
            
        except Exception as e:
            # Fallback to gTTS if OpenAI TTS fails
            try:
                lang_map = {
                    "en": "en",
                    "ur": "ur"
                }
                tts_lang = lang_map.get(language, "en")
                tts = gTTS(text=text, lang=tts_lang, slow=False)
                audio_buffer = io.BytesIO()
                tts.write_to_fp(audio_buffer)
                audio_buffer.seek(0)
                return audio_buffer.getvalue()
            except Exception as fallback_error:
                raise Exception(f"Text-to-speech error: {str(e)} | Fallback error: {str(fallback_error)}")
    
    async def speech_to_text(self, audio_file: bytes, language: str = "en") -> str:
        """
        Convert speech to text using OpenAI Whisper with language detection
        """
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
                temp_file.write(audio_file)
                temp_file_path = temp_file.name
            
            # Map language codes for Whisper
            lang_map = {
                "en": "en",
                "ur": "ur"
            }
            whisper_lang = lang_map.get(language, None)
            
            # Transcribe using OpenAI Whisper with language specification
            with open(temp_file_path, "rb") as audio_file_obj:
                transcript_params = {
                    "model": "whisper-1",
                    "file": audio_file_obj,
                    "language": whisper_lang  # Helps with accuracy for Urdu/English
                }
                transcript = self.client.audio.transcriptions.create(**transcript_params)
            
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
    
    async def analyze_image_with_vision(
        self,
        image_bytes: bytes,
        user_message: str,
        language: str = "en"
    ) -> str:
        """
        Analyze image with OpenAI Vision API for voice chat with images
        
        Args:
            image_bytes: Raw image bytes
            user_message: User's message/question about the image
            language: Language for response
            
        Returns:
            String containing image analysis
        """
        try:
            # Convert image bytes to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Create prompts based on language
            prompts = {
                "en": "You are an agricultural expert specialized in Pakistani farming. Analyze this agricultural image from Pakistan. The user is asking: " + user_message + ". Provide a detailed analysis considering Pakistani context: crop health, potential issues common in Pakistan, and practical recommendations suitable for Pakistani farmers (considering local climate, soil, water availability, and affordable inputs available in Pakistani markets).",
                "ur": "آپ پاکستانی زراعت میں ماہر ہیں۔ پاکستان سے اس زرعی تصویر کا تجزیہ کریں۔ صارف پوچھ رہے ہیں: " + user_message + "۔ پاکستانی تناظر میں تفصیلی تجزیہ دیں: فصل کی صحت، پاکستان میں عام مسائل، اور پاکستانی کسانوں کے لیے عملی سفارشات (مقامی آب و ہوا، مٹی، پانی کی دستیابی، اور پاکستانی بازاروں میں سستی اشیاء کو مدنظر رکھتے ہوئے)۔"
            }
            
            prompt = prompts.get(language, prompts["en"])
            
            # Call OpenAI Vision API
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
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
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            raise Exception(f"Vision API error: {str(e)}")
    
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
                "en": f"""You are an expert agricultural AI specialized in Pakistani farming, analyzing a crop image from Pakistan. 

{context_text}{user_question}

Based on the image and the technical analysis above, please provide Pakistan-specific analysis:
1. Overall health score (0-100)
2. Growth stage (Seedling/Vegetative/Flowering/Fruiting/Mature)
3. Any diseases detected (name and confidence level) - focus on diseases common in Pakistan
4. Specific recommendations for Pakistani farmers considering:
   - Pakistani climate zones (Punjab, Sindh, KPK, Balochistan)
   - Local irrigation methods (canal/tube well)
   - Affordable inputs available in Pakistani markets
   - Rabi/Kharif cropping seasons
   - Local pest management practices
{f"5. Address the user's specific question: {user_message.strip()}" if user_message and user_message.strip() else ""}

Format your response as JSON with these exact keys:
{{
    "health_score": <number 0-100>,
    "growth_stage": "<stage>",
    "disease_detected": "<disease name or null>",
    "disease_confidence": <number 0-1 or null>,
    "recommendations": "<detailed recommendations for Pakistani context>"
}}""",
                "ur": f"""آپ پاکستانی زراعت میں ماہر AI ہیں جو پاکستان سے فصل کی تصویر کا تجزیہ کر رہے ہیں۔

{context_text}{user_question}

تصویر اور اوپر دیے گئے تکنیکی تجزیے کی بنیاد پر، براہ کرم پاکستان کے لیے مخصوص تجزیہ فراہم کریں:
1. مجموعی صحت کا اسکور (0-100)
2. نمو کا مرحلہ (پودا/نباتاتی/پھول/پھل/بالغ)
3. کوئی بیماری کا پتہ چلا (نام اور اعتماد کی سطح) - پاکستان میں عام بیماریوں پر توجہ دیں
4. پاکستانی کسانوں کے لیے مخصوص سفارشات جن میں شامل ہو:
   - پاکستانی موسمی علاقے (پنجاب، سندھ، خیبر پختونخوا، بلوچستان)
   - مقامی آبپاشی کے طریقے (نہری/ٹیوب ویل)
   - پاکستانی منڈیوں میں سستی اشیاء
   - ربیع/خریف کی فصلوں کے موسم
   - مقامی کیڑوں کے انتظام کے طریقے
{f"5. صارف کے مخصوص سوال کا جواب دیں: {user_message.strip()}" if user_message and user_message.strip() else ""}

اپنا جواب JSON کی شکل میں ان عین کلیدوں کے ساتھ دیں:
{{
    "health_score": <نمبر 0-100>,
    "growth_stage": "<مرحلہ>",
    "disease_detected": "<بیماری کا نام یا null>",
    "disease_confidence": <نمبر 0-1 یا null>,
    "recommendations": "<پاکستانی تناظر کے لیے تفصیلی سفارشات>"
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
