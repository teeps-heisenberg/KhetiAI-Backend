"""
Image processing service using OpenCV for crop analysis
"""

import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import base64
from io import BytesIO
from PIL import Image


class ImageProcessingService:
    """Service for image preprocessing and feature extraction"""
    
    def __init__(self):
        pass
    
    def extract_crop_context(self, image_bytes: bytes) -> Dict[str, Any]:
        """
        Extract structured context from crop image for LLM analysis
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary containing extracted features and context
        """
        try:
            # Convert bytes to OpenCV image
            nparr = np.frombuffer(image_bytes, np.uint8)
            image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if image is None:
                raise ValueError("Failed to decode image")
            
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Extract color statistics
            mean_color = np.mean(image, axis=(0, 1))
            std_color = np.std(image, axis=(0, 1))
            
            # Analyze leaf health indicators - Green channel analysis (chlorophyll)
            green_channel = image[:, :, 1]
            green_mean = np.mean(green_channel)
            green_std = np.std(green_channel)
            green_percentage = (green_mean / 255.0) * 100
            
            # Detect potential disease spots using edge detection
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            spot_count = len(contours)
            
            # Calculate average spot size
            spot_sizes = [cv2.contourArea(c) for c in contours if cv2.contourArea(c) > 10]
            avg_spot_size = np.mean(spot_sizes) if spot_sizes else 0
            
            # Texture analysis (sharpness indicator)
            texture_variance = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Brightness and contrast analysis
            brightness = float(np.mean(gray))
            contrast = float(np.std(gray))
            
            # Color distribution in HSV
            hue_mean = float(np.mean(hsv[:, :, 0]))
            saturation_mean = float(np.mean(hsv[:, :, 1]))
            value_mean = float(np.mean(hsv[:, :, 2]))
            
            # Detect brown/yellow areas (potential disease indicators)
            brown_yellow_mask = cv2.inRange(hsv, np.array([10, 50, 50]), np.array([40, 255, 255]))
            brown_yellow_percentage = (np.sum(brown_yellow_mask > 0) / brown_yellow_mask.size) * 100
            
            # Detect dark spots (potential disease)
            dark_spots_mask = cv2.inRange(gray, 0, 80)
            dark_spots_percentage = (np.sum(dark_spots_mask > 0) / dark_spots_mask.size) * 100
            
            # Extract dominant colors
            dominant_colors = self._extract_dominant_colors(image, k=5)
            
            # Create structured context
            context = {
                "image_dimensions": {
                    "width": int(image.shape[1]),
                    "height": int(image.shape[0]),
                    "total_pixels": int(image.shape[0] * image.shape[1])
                },
                "color_statistics": {
                    "mean_bgr": [float(x) for x in mean_color],
                    "std_bgr": [float(x) for x in std_color],
                    "green_channel_mean": float(green_mean),
                    "green_channel_std": float(green_std),
                    "green_percentage": float(green_percentage)
                },
                "health_indicators": {
                    "potential_spots_count": int(spot_count),
                    "average_spot_size": float(avg_spot_size),
                    "texture_variance": float(texture_variance),
                    "brightness": float(brightness),
                    "contrast": float(contrast),
                    "brown_yellow_percentage": float(brown_yellow_percentage),
                    "dark_spots_percentage": float(dark_spots_percentage)
                },
                "color_analysis": {
                    "hue_mean": float(hue_mean),
                    "saturation_mean": float(saturation_mean),
                    "value_mean": float(value_mean),
                    "dominant_colors_bgr": dominant_colors
                },
                "quality_metrics": {
                    "sharpness_score": float(texture_variance),
                    "overall_brightness": "good" if 50 < brightness < 200 else "poor",
                    "color_richness": "good" if saturation_mean > 50 else "low"
                }
            }
            
            return context
            
        except Exception as e:
            raise Exception(f"Error extracting crop context: {str(e)}")
    
    def _extract_dominant_colors(self, image: np.ndarray, k: int = 5) -> List[List[int]]:
        """
        Extract dominant colors using K-means clustering
        
        Args:
            image: OpenCV image (BGR format)
            k: Number of dominant colors to extract
            
        Returns:
            List of dominant colors in BGR format
        """
        try:
            # Reshape image to be a list of pixels
            data = image.reshape((-1, 3))
            data = np.float32(data)
            
            # Define criteria and apply K-means
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 1.0)
            _, labels, centers = cv2.kmeans(
                data, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS
            )
            
            # Convert centers to integer values
            centers = centers.astype(int)
            
            return centers.tolist()
            
        except Exception as e:
            return []
    
    def format_context_for_llm(self, context: Dict[str, Any]) -> str:
        """
        Format extracted context into a readable string for LLM
        
        Args:
            context: Dictionary containing extracted features
            
        Returns:
            Formatted string describing the image context
        """
        health = context["health_indicators"]
        color = context["color_statistics"]
        quality = context["quality_metrics"]
        
        context_text = f"""
Image Analysis Context:
- Image size: {context['image_dimensions']['width']}x{context['image_dimensions']['height']} pixels
- Green content: {color['green_percentage']:.1f}% (chlorophyll indicator)
- Brightness: {health['brightness']:.1f}/255 ({quality['overall_brightness']})
- Contrast: {health['contrast']:.1f}
- Sharpness: {quality['sharpness_score']:.1f}

Health Indicators:
- Potential spots detected: {health['potential_spots_count']}
- Average spot size: {health['average_spot_size']:.1f} pixels
- Brown/yellow areas: {health['brown_yellow_percentage']:.1f}% (possible disease/stress)
- Dark spots: {health['dark_spots_percentage']:.1f}% (possible necrosis)

Color Analysis:
- Saturation: {context['color_analysis']['saturation_mean']:.1f}/255 ({quality['color_richness']})
- Hue mean: {context['color_analysis']['hue_mean']:.1f}

Based on these technical measurements, please analyze the crop health, identify any diseases or issues, and provide recommendations.
"""
        return context_text
    
    def preprocess_image_for_vision_api(
        self, 
        image_bytes: bytes, 
        max_size: Tuple[int, int] = (1024, 1024)
    ) -> str:
        """
        Preprocess and encode image for Vision API
        
        Args:
            image_bytes: Raw image bytes
            max_size: Maximum dimensions (width, height)
            
        Returns:
            Base64 encoded image string
        """
        try:
            # Load image with PIL
            image = Image.open(BytesIO(image_bytes))
            
            # Resize if necessary while maintaining aspect ratio
            image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Save to bytes
            buffer = BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            buffer.seek(0)
            
            # Encode to base64
            image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            return image_base64
            
        except Exception as e:
            raise Exception(f"Error preprocessing image: {str(e)}")


# Create singleton instance
image_processing_service = ImageProcessingService()

