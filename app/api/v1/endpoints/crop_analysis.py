"""
Crop analysis endpoints for image processing and AI analysis
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid
import time

from app.services.image_processing import image_processing_service
from app.services.openai_service import OpenAIService

router = APIRouter()
openai_service = OpenAIService()

# Pydantic models for request/response
class CropAnalysisResponse(BaseModel):
    id: str
    analysis_type: str
    health_score: Optional[float] = None
    disease_detected: Optional[str] = None
    disease_confidence: Optional[float] = None
    growth_stage: Optional[str] = None
    recommendations: str
    language: str
    created_at: datetime
    processing_time: float

class ImageUploadResponse(BaseModel):
    image_id: str
    filename: str
    size: int
    content_type: str
    upload_time: datetime

@router.post("/analyze", response_model=CropAnalysisResponse)
async def analyze_crop(
    file: UploadFile = File(...),
    language: str = Form("en"),
    user_message: Optional[str] = Form(None)
):
    """
    Analyze crop image using OpenCV preprocessing and OpenAI Vision API
    """
    start_time = time.time()
    
    try:
        # Validate file type
        allowed_types = ["image/jpeg", "image/png", "image/webp"]
        if file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"File type {file.content_type} not allowed. Allowed types: {allowed_types}"
            )
        
        # Validate file size (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"File too large. Maximum size: {max_size} bytes"
            )
        
        # Step 1: Extract context using OpenCV preprocessing
        context = image_processing_service.extract_crop_context(content)
        context_text = image_processing_service.format_context_for_llm(context)
        
        # Step 2: Preprocess image for Vision API
        image_base64 = image_processing_service.preprocess_image_for_vision_api(content)
        
        # Step 3: Analyze with OpenAI Vision API (including user message if provided)
        analysis_result = await openai_service.analyze_crop_image(
            image_base64=image_base64,
            context_text=context_text,
            language=language,
            user_message=user_message
        )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Extract results from analysis
        health_score = analysis_result.get("health_score")
        growth_stage = analysis_result.get("growth_stage")
        disease_detected = analysis_result.get("disease_detected")
        disease_confidence = analysis_result.get("disease_confidence")
        recommendations = analysis_result.get("recommendations", "")
        
        return CropAnalysisResponse(
            id=str(uuid.uuid4()),
            analysis_type="health",
            health_score=health_score,
            disease_detected=disease_detected,
            disease_confidence=disease_confidence,
            growth_stage=growth_stage,
            recommendations=recommendations,
            language=language,
            created_at=datetime.now(),
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing crop: {str(e)}")
