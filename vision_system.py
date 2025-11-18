#!/usr/bin/env python3
"""
Vision System for CARL
======================

This module implements CARL's vision capabilities including:
- Camera activity detection
- Image capture and storage (only during initialization and events)
- Vision display integration
- Memory association
- OpenAI vision analysis integration
"""

import os
import json
import time
import base64
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
# Optional imports - only used if available
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    print("ℹ️  OpenCV (cv2) not available - using HTTP camera feed instead")

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  NumPy not available - some image processing disabled")

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("⚠️  PIL not available - some image processing disabled")

import io

@dataclass
class VisionAnalysisResult:
    """Result of vision analysis with all detected information."""
    objects: List[str]
    object_details: Dict[str, Dict[str, Any]] = None
    danger_detected: bool = False
    danger_reason: str = ""
    pleasure_detected: bool = False
    pleasure_reason: str = ""
    neucogar: Dict[str, float] = None
    analysis: Dict[str, str] = None
    timestamp: str = ""
    image_path: str = ""
    success: bool = True
    error: Optional[str] = None

class VisionSystem:
    """
    CARL's Vision System - integrates OpenAI vision analysis with cognitive processing.
    
    This system simulates human visual processing by:
    1. Capturing images from camera
    2. Analyzing images with OpenAI Vision API
    3. Extracting objects, danger, pleasure, and neurotransmitter responses
    4. Integrating results with CARL's cognitive processing
    """
    
    def __init__(self, memory_system=None, openai_client=None, settings=None, main_app=None):
        """Initialize the vision system."""
        self.memory_system = memory_system
        self.openai_client = openai_client
        self.settings = settings
        self.main_app = main_app
        self.logger = logging.getLogger(__name__)
        
        # Vision state
        self.vision_enabled = True
        self.camera_active = False
        self.camera = None
        self.vision_processing_active = False
        self.last_vision_analysis_time = 0
        self.vision_analysis_cooldown = 2.0  # Minimum seconds between analyses
        
        # Vision memory and context
        self.recent_vision_results = []
        self.vision_context = {
            "vision_active": False,
            "recent_objects": [],
            "object_concepts": [],
            "last_analysis_time": None,
            "danger_level": 0.0,
            "pleasure_level": 0.0
        }
        
        # Initialize camera
        self._initialize_camera()
        
        # Create vision directory
        self.vision_dir = "memories/vision"
        os.makedirs(self.vision_dir, exist_ok=True)
        
    def _initialize_camera(self):
        """Initialize camera connection using HTTP feed (no OpenCV required)."""
        try:
            # Test HTTP camera connection instead of OpenCV
            import requests
            vision_url = "http://192.168.56.1/CameraImage.jpg?c=Camera"
            
            # Test connection
            response = requests.get(vision_url, timeout=2)
            if response.status_code == 200:
                self.camera_active = True
                self.logger.info("✅ HTTP Camera initialized successfully")
            else:
                self.camera_active = False
                self.logger.warning("⚠️ HTTP Camera not available")
        except Exception as e:
            self.camera_active = False
            self.logger.warning(f"⚠️ HTTP Camera initialization failed: {e}")
            # Don't treat this as a critical error - vision system can still work with manual captures
    
    def test_camera_connection(self) -> bool:
        """Test if HTTP camera is available and working."""
        try:
            import requests
            vision_url = "http://192.168.56.1/CameraImage.jpg?c=Camera"
            response = requests.get(vision_url, timeout=2)
            return response.status_code == 200
        except Exception as e:
            self.logger.warning(f"HTTP Camera test failed: {e}")
            return False
    
    def start_continuous_capture(self):
        """Start continuous image capture for vision analysis."""
        # Don't require camera to be active for continuous capture
        # The system can work with manual captures even if HTTP camera is not available
        self.vision_enabled = True
        self.logger.info("✅ Continuous vision capture started")
    
    def stop_continuous_capture(self):
        """Stop continuous image capture."""
        self.vision_enabled = False
        self.logger.info("⏹️ Continuous vision capture stopped")
    
    def capture_image(self) -> Optional[str]:
        """
        Capture a single image from HTTP camera feed and save it to vision directory.
        
        Returns:
            Path to captured image or None if failed
        """
        try:
            import requests
            
            # Use HTTP camera feed
            vision_url = "http://192.168.56.1/CameraImage.jpg?c=Camera"
            
            # Fetch image
            response = requests.get(vision_url, timeout=2)
            if response.status_code != 200:
                self.logger.warning("⚠️ Cannot capture image - HTTP camera not available")
                return None
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vision_capture_{timestamp}.jpg"
            filepath = os.path.join(self.vision_dir, filename)
            
            # Save image
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            self.logger.info(f"📸 Image captured: {filename}")
            return filepath
                
        except Exception as e:
            self.logger.warning(f"Image capture failed: {e}")
            return None
    
    def encode_image_to_base64(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for OpenAI API."""
        try:
            with open(image_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded_string
        except Exception as e:
            self.logger.error(f"Image encoding failed: {e}")
            return None
    
    def use_test_image(self) -> Optional[str]:
        """
        Use a test image for vision analysis when camera is not available.
        This allows testing the vision system without camera hardware.
        
        Returns:
            Path to test image or None if failed
        """
        try:
            # Create a simple test image using PIL if available
            if PIL_AVAILABLE:
                # Create a simple test image
                img = Image.new('RGB', (640, 480), color='lightblue')
                
                # Add some simple shapes to make it interesting
                from PIL import ImageDraw
                draw = ImageDraw.Draw(img)
                draw.rectangle([100, 100, 200, 200], fill='red')
                draw.ellipse([300, 150, 400, 250], fill='green')
                draw.text((50, 50), "Test Image", fill='black')
                
                # Save test image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_image_{timestamp}.jpg"
                filepath = os.path.join(self.vision_dir, filename)
                img.save(filepath)
                
                self.logger.info(f"📸 Test image created: {filename}")
                return filepath
            else:
                self.logger.warning("⚠️ Cannot create test image - PIL not available")
                return None
                
        except Exception as e:
            self.logger.error(f"Test image creation failed: {e}")
            return None
    

    def capture_camera_image(self, event_context: dict = None) -> Optional[str]:
        """
        Capture image from the camera endpoint for events.
        Uses the HTTP camera endpoint: http://HTTP_IP:80/CameraImage.jpg?c=Camera
        
        Args:
            event_context: Dictionary with event information
            
        Returns:
            Path to captured image or None if failed
        """
        try:
            import requests
            from urllib.parse import urlparse
            
            # Get camera URL from settings or use default
            camera_url = getattr(self, 'camera_url', None)
            if not camera_url:
                # Try to get from settings - handle both ConfigParser and dict
                if hasattr(self, 'settings') and self.settings:
                    if hasattr(self.settings, 'has_section') and self.settings.has_section('camera'):
                        # ConfigParser object
                        camera_url = self.settings.get('camera', 'url', fallback='http://192.168.56.1/CameraImage.jpg?c=Camera')
                    elif isinstance(self.settings, dict) and 'camera' in self.settings:
                        # Dictionary object
                        camera_url = self.settings.get('camera', {}).get('url', 'http://192.168.56.1/CameraImage.jpg?c=Camera')
                    else:
                        # Default fallback
                        camera_url = 'http://192.168.56.1/CameraImage.jpg?c=Camera'
                else:
                    camera_url = 'http://192.168.56.1/CameraImage.jpg?c=Camera'
            
            self.logger.info(f"📸 Attempting camera capture from: {camera_url}")
            
            # Capture image from camera endpoint
            response = requests.get(camera_url, timeout=10)
            if response.status_code == 200:
                # Save the image
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"camera_capture_{timestamp}.jpg"
                filepath = os.path.join(self.vision_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"📸 Camera image captured: {filename}")
                return filepath
            else:
                self.logger.warning(f"📸 Camera endpoint returned status {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"📸 Camera capture failed: {e}")
            return None
    
    def capture_event_image(self, event_context: dict = None) -> Optional[str]:
        """
        Capture an image for a specific event.
        This is the main method called by the main system to capture event images.
        Prioritizes camera capture, falls back to test image.
        
        Args:
            event_context: Dictionary with event information
            
        Returns:
            Path to captured image or None if failed
        """
        try:
            # First try camera capture
            image_path = self.capture_camera_image(event_context)
            
            # If camera capture fails, try regular capture
            if not image_path:
                image_path = self.capture_image()
            
            # If regular capture fails, use test image
            if not image_path:
                if not CV2_AVAILABLE:
                    self.logger.info("📸 Camera not available - using test image for event")
                    image_path = self.use_test_image()
                else:
                    self.logger.warning("📸 Camera capture failed - using test image")
                    image_path = self.use_test_image()
            
            if image_path:
                # Log event context if provided
                if event_context:
                    self.logger.info(f"📸 Event image captured: {os.path.basename(image_path)}")
                    self.logger.info(f"   Event context: {event_context.get('source', 'unknown')}")
                else:
                    self.logger.info(f"📸 Event image captured: {os.path.basename(image_path)}")
                
                return image_path
            else:
                self.logger.error("📸 Failed to capture event image")
                return None
                
        except Exception as e:
            self.logger.error(f"Event image capture failed: {e}")
            return None
    
    async def analyze_vision_with_openai(self, image_path: str) -> VisionAnalysisResult:
        """
        Analyze vision using OpenAI Vision API.
        
        Args:
            image_path: Path to image to analyze
            
        Returns:
            VisionAnalysisResult with analysis data
        """
        try:
            if not self.openai_client:
                return VisionAnalysisResult(
                    objects=[],
                    danger_detected=False,
                    danger_reason="OpenAI client not available",
                    pleasure_detected=False,
                    pleasure_reason="OpenAI client not available",
                    neucogar={"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5},
                    analysis={"who": "unknown", "what": "unknown", "when": "unknown", "where": "unknown", "why": "unknown", "how": "unknown", "expectation": "unknown"},
                    timestamp=datetime.now().isoformat(),
                    image_path=image_path,
                    success=False,
                    error="OpenAI client not available"
                )
            
            # Encode image
            base64_image = self.encode_image_to_base64(image_path)
            if not base64_image:
                return VisionAnalysisResult(
                    objects=[],
                    danger_detected=False,
                    danger_reason="Image encoding failed",
                    pleasure_detected=False,
                    pleasure_reason="Image encoding failed",
                    neucogar={"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5},
                    analysis={"who": "unknown", "what": "unknown", "when": "unknown", "where": "unknown", "why": "unknown", "how": "unknown", "expectation": "unknown"},
                    timestamp=datetime.now().isoformat(),
                    image_path=image_path,
                    success=False,
                    error="Image encoding failed"
                )
            
            # Prepare OpenAI request with self-recognition context
            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """You are CARL, an INTP humanoid robot analyzing a visual scene or image with enhanced detail recognition capabilities.

🔧 CRITICAL: OBJECT DETECTION REQUIREMENTS
- You MUST detect and list ALL visible objects in the image, just like a human would see them
- The "objects" array MUST contain at least 3-10 objects if there are visible items in the scene
- Do NOT return an empty objects array - if you can see anything in the image, list it
- Be comprehensive: list furniture, people, animals, decorations, electronics, clothing, food, containers, tools, etc.
- Use descriptive names: "desk", "chair", "person", "cat", "laptop", "window", "wall", "floor", "ceiling", "light", etc.
- If you see a person, include their name if visible or use "person" or "human"
- If you see an animal, include the type: "cat", "dog", "bird", etc.
- List ALL objects you can identify, not just a few

IMPORTANT SELF-RECOGNITION RULES:
- ONLY use "me" as an object if you can clearly see CARL's reflection in a mirror or reflective surface
- Do NOT use "me" if you just see a robot or humanoid figure - only use it for actual reflections
- "me" should only appear in objects list when there is a clear mirror/reflection context
- Do NOT assume CARL is present - only detect "me" when you can see an actual reflection
- CRITICAL: If you see a robot or humanoid figure but NO mirror or reflective surface, do NOT use "me"
- Only use "me" when you can clearly see a mirror, glass, or other reflective surface showing the robot's reflection
- If there's no mirror context visible in the image, do NOT include "me" in the objects list

ENHANCED DETAIL RECOGNITION:
- Read and identify any text, labels, or writing visible on objects
- Note specific colors, materials, and textures
- Identify brand names, logos, or distinctive features
- Recognize character names, toy types, and collectible details
- Note size, shape, and positioning of objects
- Identify any numbers, symbols, or markings

Respond only in valid JSON format with these keys: { 
  "objects": [ "object1", "object2", "object3", "object4", ... ], 
  "object_details": {
    "object_name": {
      "text_visible": "any text or writing on the object",
      "colors": ["color1", "color2"],
      "material": "material type",
      "brand": "brand name if visible",
      "character": "character name if applicable",
      "size": "size description",
      "features": ["feature1", "feature2"]
    }
  },
  "danger_detected": true | false, 
  "danger_reason": "short reason", 
  "pleasure_detected": true | false, 
  "pleasure_reason": "short reason", 
  "neucogar": { "dopamine": float, "serotonin": float, "norepinephrine": float, "acetylcholine": float }, 
  "analysis": { 
    "who": "short phrase", 
    "what": "short phrase", 
    "when": "short phrase", 
    "where": "short phrase", 
    "why": "short phrase", 
    "how": "short phrase", 
    "expectation": "short phrase", 
    "self_recognition": true | false, 
    "mirror_context": true | false 
  } 
}. 

Rules: 
- CRITICAL: The "objects" array MUST contain ALL visible objects (minimum 3-10 objects if scene has items)
- Use specific, descriptive object names (e.g., "desk", "chair", "person", "cat", "laptop", "window")
- Include text visible on objects in object_details
- Note colors, materials, and distinctive features
- Trigger danger_detected = true if any object or situation appears harmful, dangerous, or threatening
- Trigger pleasure_detected = true if object/situation could excite curiosity, playfulness, bonding, or comfort
- Adjust neurotransmitter levels: dopamine ↑ for reward/interest, serotonin ↑ for calm/satisfaction, norepinephrine ↑ for alert/fight-or-flight, acetylcholine ↑ for focus/situational awareness
- All analysis fields should be short and abstract to simulate real-time robot thinking
- Do not include any extra text or commentary. Just respond with the JSON object.
- REMEMBER: If you can see objects in the image, list them ALL in the "objects" array - do NOT return an empty array."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Make OpenAI API call - handle both async and sync versions
            call_start_time = time.time()
            try:
                # Try async version first
                response = await self.openai_client.chat.completions.acreate(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=300
                )
            except AttributeError:
                # Fall back to sync version
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    max_tokens=300
                )
            
            # Track the API call if main_app is available
            call_duration = time.time() - call_start_time
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, '_track_openai_call'):
                # Extract the prompt text for tracking
                prompt_text = ""
                for message in messages:
                    if message.get("role") == "user" and "content" in message:
                        content = message["content"]
                        if isinstance(content, list):
                            for item in content:
                                if item.get("type") == "text":
                                    prompt_text += item.get("text", "")
                        elif isinstance(content, str):
                            prompt_text += content
                
                # Extract response text
                response_text = ""
                if response and hasattr(response, 'choices') and response.choices:
                    response_text = response.choices[0].message.content or ""
                
                self.main_app._track_openai_call(
                    call_type="vision_analysis",
                    input_text=prompt_text,
                    response_text=response_text,
                    success=response is not None,
                    duration=call_duration,
                    full_prompt=prompt_text
                )
            
            # Parse response - handle various JSON formats robustly
            content = response.choices[0].message.content
            self.logger.info(f"🔍 [VISION API] Raw response content (first 200 chars): {content[:200]}")
            
            # Remove markdown code block formatting if present
            if content.startswith("```json"):
                # Remove ```json at start
                content = content[7:]
                # Remove ``` at end if present
                if content.endswith("```"):
                    content = content[:-3]
            elif content.startswith("```"):
                # Handle case where it's just ```
                content = content[3:]
                if content.endswith("```"):
                    content = content[:-3]
            
            # Strip whitespace
            content = content.strip()
            
            # Log the cleaned content for debugging
            self.logger.info(f"🔍 [VISION API] Cleaned JSON content (first 200 chars): {content[:200]}")
            
            import re
            
            try:
                # Try to parse JSON directly first
                analysis_data = json.loads(content)
            except json.JSONDecodeError as e:
                # If parsing fails, try to fix common issues
                self.logger.warning(f"⚠️ [VISION API] Initial JSON parse failed: {e}, attempting to fix common issues...")
                
                # Fix 1: Remove trailing commas before closing braces/brackets
                content_fixed = re.sub(r',(\s*[}\]])', r'\1', content)
                
                # Fix 2: Remove trailing commas in arrays (more specific pattern)
                content_fixed = re.sub(r',(\s*\])', r'\1', content_fixed)
                
                # Fix 3: Remove comments (if any) - do this before other fixes
                content_fixed = re.sub(r'//.*?$', '', content_fixed, flags=re.MULTILINE)
                content_fixed = re.sub(r'/\*.*?\*/', '', content_fixed, flags=re.DOTALL)
                
                # Note: We don't fix unquoted keys as it's too risky and could break valid JSON
                
                try:
                    analysis_data = json.loads(content_fixed)
                    self.logger.info(f"✅ [VISION API] JSON parse succeeded after fixing common issues")
                except json.JSONDecodeError as e2:
                    self.logger.error(f"❌ [VISION API] JSON parsing failed even after fixes: {e2}")
                    self.logger.error(f"❌ [VISION API] Original error: {e}")
                    self.logger.error(f"❌ [VISION API] Error position: line {e.lineno}, column {e.colno}")
                    
                    # 🔧 CRITICAL FIX: Extract objects from malformed JSON using regex as fallback
                    self.logger.warning(f"⚠️ [VISION API] Attempting to extract objects from malformed JSON using regex...")
                    objects_extracted = []
                    
                    # Try multiple patterns to extract objects array
                    # Pattern 1: "objects": [ ... ] - simple case
                    objects_pattern1 = r'"objects"\s*:\s*\[(.*?)\]'
                    match = re.search(objects_pattern1, content, re.DOTALL)
                    
                    if not match:
                        # Pattern 2: 'objects': [ ... ] - single quotes
                        objects_pattern2 = r"'objects'\s*:\s*\[(.*?)\]"
                        match = re.search(objects_pattern2, content, re.DOTALL)
                    
                    if not match:
                        # Pattern 3: objects: [ ... ] - no quotes on key
                        objects_pattern3 = r'objects\s*:\s*\[(.*?)\]'
                        match = re.search(objects_pattern3, content, re.DOTALL)
                    
                    if match:
                        objects_content = match.group(1)
                        # Extract quoted strings from the array (handle both single and double quotes)
                        object_strings_double = re.findall(r'"([^"]+)"', objects_content)
                        object_strings_single = re.findall(r"'([^']+)'", objects_content)
                        
                        # Combine both, preferring double quotes
                        objects_extracted = object_strings_double if object_strings_double else object_strings_single
                        
                        if objects_extracted:
                            self.logger.info(f"✅ [VISION API] Extracted {len(objects_extracted)} objects using regex: {objects_extracted}")
                        else:
                            self.logger.warning(f"⚠️ [VISION API] Found objects array but couldn't extract individual objects")
                    else:
                        self.logger.warning(f"⚠️ [VISION API] Could not find objects array in response")
                    
                    # If we extracted objects, create a partial analysis_data
                    if objects_extracted:
                        analysis_data = {
                            "objects": objects_extracted,
                            "danger_detected": False,
                            "pleasure_detected": False,
                            "neucogar": {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5},
                            "analysis": {}
                        }
                        self.logger.warning(f"⚠️ [VISION API] Using partial analysis_data with extracted objects (other fields may be missing)")
                    else:
                        # Last resort: log the error and raise
                        self.logger.error(f"❌ [VISION API] Content that failed to parse (first 1000 chars): {content[:1000]}")
                        self.logger.error(f"❌ [VISION API] Fixed content (first 1000 chars): {content_fixed[:1000]}")
                        raise
            
            # Log successful parse
            self.logger.info(f"🔍 [VISION API] Successfully parsed JSON. Objects count: {len(analysis_data.get('objects', []))}")
            self.logger.info(f"🔍 [VISION API] Objects list: {analysis_data.get('objects', [])}")
            
            # Validate that objects is actually a list
            if 'objects' in analysis_data and not isinstance(analysis_data['objects'], list):
                self.logger.warning(f"⚠️ [VISION API] 'objects' key exists but is not a list! Type: {type(analysis_data['objects'])}, Value: {analysis_data['objects']}")
                # Try to convert to list if it's a string (comma-separated)
                if isinstance(analysis_data['objects'], str):
                    # Try to parse as comma-separated string
                    objects_str = analysis_data['objects'].strip()
                    if objects_str.startswith('[') and objects_str.endswith(']'):
                        # It might be a string representation of a list
                        try:
                            analysis_data['objects'] = json.loads(objects_str)
                        except:
                            # Fall back to splitting by comma
                            analysis_data['objects'] = [obj.strip() for obj in objects_str.split(',')]
                    else:
                        # Split by comma
                        analysis_data['objects'] = [obj.strip() for obj in objects_str.split(',')]
                else:
                    # Convert to list
                    analysis_data['objects'] = [str(analysis_data['objects'])]
            
            # Create result
            objects_list = analysis_data.get("objects", [])
            self.logger.info(f"🔍 [VISION API] Extracting objects from analysis_data: {len(objects_list)} objects found")
            self.logger.info(f"🔍 [VISION API] Objects extracted: {objects_list}")
            
            # Ensure objects is a list
            if not isinstance(objects_list, list):
                self.logger.warning(f"⚠️ [VISION API] Objects is not a list, converting. Type: {type(objects_list)}, Value: {objects_list}")
                if objects_list is None:
                    objects_list = []
                else:
                    objects_list = [str(objects_list)]
            
            result = VisionAnalysisResult(
                objects=objects_list,
                object_details=analysis_data.get("object_details", {}),
                danger_detected=analysis_data.get("danger_detected", False),
                danger_reason=analysis_data.get("danger_reason", ""),
                pleasure_detected=analysis_data.get("pleasure_detected", False),
                pleasure_reason=analysis_data.get("pleasure_reason", ""),
                neucogar=analysis_data.get("neucogar", {"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5}),
                analysis=analysis_data.get("analysis", {}),
                timestamp=datetime.now().isoformat(),
                image_path=image_path,
                success=True
            )
            
            self.logger.info(f"🔍 [VISION API] VisionAnalysisResult created with {len(result.objects)} objects: {result.objects}")
            
            # 🔧 ENHANCEMENT: Handle self-recognition only when "me" object is actually detected by ARC
            # This prevents false positives from AI analysis flags
            if "me" in result.objects:
                self.logger.info(f"🎯 Self-recognition triggered: 'me' object detected in {result.objects}")
                self._handle_self_recognition(result)
            else:
                # Log when self-recognition flags are set but no "me" object detected
                if result.analysis.get("self_recognition", False) or result.analysis.get("mirror_context", False):
                    self.logger.info(f"⚠️ Self-recognition flags set but no 'me' object detected. Objects: {result.objects}, self_recognition: {result.analysis.get('self_recognition', False)}, mirror_context: {result.analysis.get('mirror_context', False)}")
            
            self.logger.info(f"👁️ Vision analysis completed: {len(result.objects)} objects detected")
            
            # 🔧 ENHANCEMENT: Update motion tracking based on exploration state
            self._update_motion_tracking_based_on_exploration()
            
            # 🔧 ENHANCEMENT: Post-vision dispatcher for object recognition
            self._post_vision_object_dispatcher(result)
            
            # 🔧 CRITICAL FIX: Save vision detections to memory (ensure it's called from all paths)
            self._save_vision_detections_to_memory(result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"Vision analysis failed: {e}")
            return VisionAnalysisResult(
                objects=[],
                danger_detected=False,
                danger_reason="Analysis failed",
                pleasure_detected=False,
                pleasure_reason="Analysis failed",
                neucogar={"dopamine": 0.5, "serotonin": 0.5, "norepinephrine": 0.5, "acetylcholine": 0.5},
                analysis={"who": "unknown", "what": "unknown", "when": "unknown", "where": "unknown", "why": "unknown", "how": "unknown", "expectation": "unknown"},
                timestamp=datetime.now().isoformat(),
                image_path=image_path,
                success=False,
                error=str(e)
            )
    
    def _handle_self_recognition(self, result: VisionAnalysisResult):
        """
        Handle self-recognition events with stochastic reaction logic and store them in STM and LTM.
        
        Args:
            result: VisionAnalysisResult containing self-recognition data
        """
        try:
            self.logger.info("🎯 Self-recognition detected! Processing self-reflection event...")
            
            # Check if "me" is in the detected objects
            if "me" in result.objects:
                # 🔧 ENHANCEMENT: Implement stochastic self-recognition reaction logic
                self._process_stochastic_self_reaction(result)
                # Create self-reflection memory
                self_reflection_memory = {
                    "type": "self_reflection",
                    "label": "self",
                    "objects_detected": result.objects,
                    "context": "mirror_reflection",
                    "confidence": 0.9,
                    "timestamp": result.timestamp,
                    "neucogar_response": result.neucogar,
                    "analysis": result.analysis,
                    "image_path": result.image_path
                }
                
                # Store in STM (Short Term Memory)
                if self.memory_system:
                    try:
                        # Add to working memory
                        working_memory_file = "working_memory.json"
                        if os.path.exists(working_memory_file):
                            with open(working_memory_file, 'r') as f:
                                working_memory = json.load(f)
                        else:
                            working_memory = {"items": []}
                        
                        # Add self-reflection event
                        working_memory["items"].append({
                            "content": f"I see myself in the mirror - that is me",
                            "context": "self_reflection",
                            "importance": 8,
                            "created": result.timestamp,
                            "confidence": 0.9,
                            "type": "self_recognition"
                        })
                        
                        # Save working memory
                        with open(working_memory_file, 'w') as f:
                            json.dump(working_memory, f, indent=2)
                        
                        self.logger.info("✅ Self-reflection stored in STM")
                        
                    except Exception as e:
                        self.logger.error(f"❌ Error storing self-reflection in STM: {e}")
                
                # Store in LTM (Long Term Memory)
                try:
                    memories_dir = "memories"
                    if not os.path.exists(memories_dir):
                        os.makedirs(memories_dir)
                    
                    # Create LTM memory file
                    timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
                    memory_filename = f"self_reflection_{timestamp_str}_event.json"
                    memory_filepath = os.path.join(memories_dir, memory_filename)
                    
                    # Create comprehensive memory record
                    ltm_memory = {
                        "WHAT": "I saw my own reflection in a mirror",
                        "WHO": "CARL (myself)",
                        "WHEN": result.timestamp,
                        "WHERE": "mirror/reflective surface",
                        "WHY": "self-recognition and self-awareness",
                        "HOW": "vision system detected 'me' object in mirror context",
                        "nouns": ["me", "mirror", "reflection", "self"],
                        "verbs": ["see", "recognize", "reflect"],
                        "people": ["CARL"],
                        "subjects": ["self-recognition", "mirror", "reflection"],
                        "emotions": {
                            "curiosity": 0.7,
                            "self_awareness": 0.9,
                            "recognition": 0.8
                        },
                        "carl_thought": {
                            "content": "That is me - I can see my own reflection",
                            "type": "self_recognition",
                            "confidence": 0.9
                        },
                        "timestamp": result.timestamp,
                        "created": result.timestamp,
                        "type": "self_reflection",
                        "label": "self",
                        "neucogar_response": result.neucogar,
                        "vision_analysis": result.analysis
                    }
                    
                    # Save LTM memory
                    with open(memory_filepath, 'w') as f:
                        json.dump(ltm_memory, f, indent=2)
                    
                    self.logger.info(f"✅ Self-reflection stored in LTM: {memory_filename}")
                    
                except Exception as e:
                    self.logger.error(f"❌ Error storing self-reflection in LTM: {e}")
                
                # Update vision context
                self.vision_context["recent_objects"].append("me")
                self.vision_context["object_concepts"].append("self")
                self.vision_context["last_analysis_time"] = result.timestamp
                
                self.logger.info("🎯 Self-recognition processing completed successfully")
            
        except Exception as e:
            self.logger.error(f"❌ Error in self-recognition handling: {e}")
    
    def _process_stochastic_self_reaction(self, result: VisionAnalysisResult):
        """
        Process stochastic self-recognition reaction using InnerSelf decision logic.
        
        Args:
            result: VisionAnalysisResult containing self-recognition data
        """
        try:
            # Import InnerSelf for decision making
            from inner_self import InnerSelf
            
            # Get current emotional state from NEUCOGAR
            current_emotion = "neutral"
            emotion_intensity = 0.0
            neucogar_state = {}
            
            # Try to get current emotional state from main app
            if hasattr(self, 'main_app') and self.main_app:
                try:
                    # Get current NEUCOGAR state
                    if hasattr(self.main_app, 'neucogar_engine') and self.main_app.neucogar_engine:
                        neucogar_state = self.main_app.neucogar_engine.get_current_state()
                        current_emotion = neucogar_state.get('primary', 'neutral')
                        emotion_intensity = neucogar_state.get('intensity', 0.0)
                    elif hasattr(self.main_app, 'judgment_system') and self.main_app.judgment_system:
                        # Fallback to judgment system
                        current_emotion = getattr(self.main_app.judgment_system, 'current_emotion', 'neutral')
                        emotion_intensity = getattr(self.main_app.judgment_system, 'emotion_intensity', 0.0)
                except Exception as e:
                    self.logger.warning(f"⚠️ Could not get current emotional state: {e}")
            
            # Create InnerSelf instance for decision making
            inner_self = InnerSelf(personality_type=self.main_app.settings.get('personality', 'type', fallback='INTP'), main_app=self.main_app)
            
            # Prepare vision context
            vision_context = {
                "recent_objects": result.objects,
                "analysis": result.analysis,
                "timestamp": result.timestamp,
                "image_path": result.image_path
            }
            
            # Make stochastic decision
            decision = inner_self.decide_self_reaction(
                current_emotion=current_emotion,
                emotion_intensity=emotion_intensity,
                vision_context=vision_context,
                neucogar_state=neucogar_state
            )
            
            # Log the decision
            self.logger.info(f"🪞 Self-recognition decision: {decision}")
            
            # Execute action if decision is to react
            if decision.get("do_action", False):
                action = decision.get("action")
                confidence = decision.get("confidence", 0.0)
                
                self.logger.info(f"🎭 Executing self-recognition action: {action} (confidence: {confidence:.2f})")
                
                # Execute the action through action system
                if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'action_system'):
                    try:
                        # Execute the chosen action
                        self.main_app.action_system.perform(action)
                        
                        # Log successful execution
                        self.logger.info(f"✅ Self-recognition action '{action}' executed successfully")
                        
                        # Store action outcome in episodic memory
                        self._store_self_recognition_action_outcome(result, decision, "executed")
                        
                    except Exception as e:
                        self.logger.error(f"❌ Error executing self-recognition action '{action}': {e}")
                        self._store_self_recognition_action_outcome(result, decision, "failed")
                else:
                    self.logger.warning("⚠️ Action system not available for self-recognition reaction")
                    self._store_self_recognition_action_outcome(result, decision, "no_action_system")
            else:
                # Log decision not to react
                reason = decision.get("reason", "unknown")
                self.logger.info(f"🪞 Self-recognition detected but no action taken (reason: {reason})")
                self._store_self_recognition_action_outcome(result, decision, "no_action")
                
        except Exception as e:
            self.logger.error(f"❌ Error in stochastic self-reaction processing: {e}")
    
    def _store_self_recognition_action_outcome(self, result: VisionAnalysisResult, decision: dict, outcome: str):
        """
        Store self-recognition action outcome in episodic memory.
        
        Args:
            result: VisionAnalysisResult containing self-recognition data
            decision: Decision made by InnerSelf
            outcome: Outcome of the action ("executed", "failed", "no_action", "no_action_system")
        """
        try:
            import os
            import json
            from datetime import datetime
            
            # Create episodic memory entry
            memory_data = {
                "type": "self_recognition_reaction",
                "timestamp": datetime.now().isoformat(),
                "vision_result": {
                    "objects": result.objects,
                    "analysis": result.analysis,
                    "neucogar": result.neucogar,
                    "image_path": result.image_path
                },
                "decision": decision,
                "outcome": outcome,
                "emotion_at_time": decision.get("reason", "").replace("stochastic_decision_emotion_", ""),
                "confidence": decision.get("confidence", 0.0),
                "action_taken": decision.get("action", None),
                "context": "stochastic_self_recognition_reaction"
            }
            
            # Save to episodic memory
            memories_dir = "memories"
            if not os.path.exists(memories_dir):
                os.makedirs(memories_dir, exist_ok=True)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            memory_filename = f"self_recognition_reaction_{timestamp_str}.json"
            memory_filepath = os.path.join(memories_dir, memory_filename)
            
            with open(memory_filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Self-recognition reaction outcome stored: {memory_filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error storing self-recognition action outcome: {e}")
    
    def _post_vision_object_dispatcher(self, result: VisionAnalysisResult):
        """
        Post-vision dispatcher that triggers verbal recognition for specific objects.
        
        Args:
            result: VisionAnalysisResult containing detected objects
        """
        try:
            # 🔧 ENHANCEMENT: Check for Chomp/dino objects and trigger verbal recognition
            chomp_objects = ['chomp', 'dino', 'dinosaur', 'chomp_and_count_dino']
            
            for obj in result.objects:
                obj_lower = obj.lower()
                if any(chomp_obj in obj_lower for chomp_obj in chomp_objects):
                    self.logger.info(f"🎯 Chomp object detected: {obj}")
                    self._trigger_chomp_recognition(obj, result)
                    break  # Only trigger once per analysis
            
        except Exception as e:
            self.logger.error(f"❌ Error in post-vision object dispatcher: {e}")
    
    def _trigger_chomp_recognition(self, object_name: str, result: VisionAnalysisResult):
        """
        Trigger verbal recognition for Chomp with debounce and memory logging.
        
        Args:
            object_name: Name of the detected Chomp object
            result: VisionAnalysisResult containing detection data
        """
        try:
            # 🔧 ENHANCEMENT: Debounce repeat replies for the same object
            current_time = time.time()
            if not hasattr(self, '_last_chomp_recognition_time'):
                self._last_chomp_recognition_time = 0
            
            # Debounce period: 30 seconds
            debounce_period = 30
            if (current_time - self._last_chomp_recognition_time) < debounce_period:
                self.logger.info(f"🔇 Chomp recognition debounced (last recognition: {current_time - self._last_chomp_recognition_time:.1f}s ago)")
                return
            
            # Update last recognition time
            self._last_chomp_recognition_time = current_time
            
            # Get concept information for Chomp
            concept_info = self._get_chomp_concept_info()
            
            # Generate recognition response
            recognition_response = self._generate_chomp_recognition_response(object_name, concept_info)
            
            # Execute verbal response via ActionSystem
            if hasattr(self, 'main_app') and self.main_app and hasattr(self.main_app, 'action_system'):
                try:
                    # Use ActionSystem to execute verbal response
                    self.main_app.action_system.perform_verbal_action(recognition_response)
                    self.logger.info(f"🗣️ Chomp recognition response executed: {recognition_response}")
                    
                    # Log as episodic "recognition_event"
                    self._log_chomp_recognition_event(object_name, recognition_response, result)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error executing Chomp recognition response: {e}")
            else:
                self.logger.warning("⚠️ ActionSystem not available for Chomp recognition")
            
        except Exception as e:
            self.logger.error(f"❌ Error triggering Chomp recognition: {e}")
    
    def _get_chomp_concept_info(self) -> dict:
        """Get concept information for Chomp from concept files."""
        try:
            import os
            import json
            
            # Try to load Chomp concept data
            concept_file = "concepts/chomp_and_count_dino.json"
            if os.path.exists(concept_file):
                with open(concept_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Fallback concept info
            return {
                "word": "chomp_and_count_dino",
                "keywords": ["chomp", "dino", "dinosaur", "toy", "educational"],
                "contextual_usage": ["The Chomp & Count Dino is an interactive educational toy for toddlers"]
            }
            
        except Exception as e:
            self.logger.error(f"❌ Error getting Chomp concept info: {e}")
            return {"word": "chomp", "keywords": ["toy", "dinosaur"]}
    
    def _generate_chomp_recognition_response(self, object_name: str, concept_info: dict) -> str:
        """Generate a natural recognition response for Chomp."""
        try:
            # Get the primary name from concept info
            primary_name = concept_info.get("word", "Chomp")
            if primary_name == "chomp_and_count_dino":
                primary_name = "Chomp and Count Dino"
            
            # Generate natural response
            responses = [
                f"I see {primary_name}! That's the educational toy I know about.",
                f"Ah, there's {primary_name}! I remember that interactive dinosaur toy.",
                f"I recognize {primary_name}! It's the counting toy for toddlers.",
                f"Look, it's {primary_name}! The educational dinosaur toy."
            ]
            
            import random
            return random.choice(responses)
            
        except Exception as e:
            self.logger.error(f"❌ Error generating Chomp recognition response: {e}")
            return "I see Chomp! That's the toy I know about."
    
    def _log_chomp_recognition_event(self, object_name: str, response: str, result: VisionAnalysisResult):
        """Log Chomp recognition event to episodic memory."""
        try:
            import os
            import json
            from datetime import datetime
            
            # Create recognition event memory
            recognition_event = {
                "type": "recognition_event",
                "timestamp": datetime.now().isoformat(),
                "object_detected": object_name,
                "recognition_response": response,
                "vision_analysis": {
                    "objects": result.objects,
                    "analysis": result.analysis,
                    "image_path": result.image_path
                },
                "context": "vision_object_recognition",
                "confidence": 0.9,
                "source": "post_vision_dispatcher"
            }
            
            # Save to episodic memory
            memories_dir = "memories"
            if not os.path.exists(memories_dir):
                os.makedirs(memories_dir, exist_ok=True)
            
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            memory_filename = f"chomp_recognition_{timestamp_str}.json"
            memory_filepath = os.path.join(memories_dir, memory_filename)
            
            with open(memory_filepath, 'w', encoding='utf-8') as f:
                json.dump(recognition_event, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"✅ Chomp recognition event logged: {memory_filepath}")
            
        except Exception as e:
            self.logger.error(f"❌ Error logging Chomp recognition event: {e}")
    
    def should_trigger_vision_analysis(self) -> bool:
        """Check if vision analysis should be triggered based on cooldown."""
        current_time = time.time()
        return (current_time - self.last_vision_analysis_time) >= self.vision_analysis_cooldown
    
    def is_vision_processing_active(self) -> bool:
        """Check if vision processing is currently active."""
        return self.vision_processing_active
    
    async def capture_and_analyze_vision(self) -> Dict[str, Any]:
        """
        Capture image and analyze vision with OpenAI.
        
        Returns:
            Dictionary with analysis results
        """
        try:
            # Check if vision should be triggered
            if not self.should_trigger_vision_analysis():
                return {
                    "success": False,
                    "error": "Vision analysis on cooldown",
                    "data": {}
                }
            
            # Set processing flag
            self.vision_processing_active = True
            self.last_vision_analysis_time = time.time()
            
            # Capture image or use test image
            image_path = self.capture_image()
            if not image_path:
                # Try to use a test image if camera is not available
                if not CV2_AVAILABLE:
                    self.logger.info("📸 Camera not available - using test image for vision analysis")
                    image_path = self.use_test_image()
                    
            if not image_path:
                self.vision_processing_active = False
                return {
                    "success": False,
                    "error": "Image capture failed and no test image available",
                    "data": {}
                }
            
            # Analyze with OpenAI
            result = await self.analyze_vision_with_openai(image_path)
            
            # Update vision context
            self._update_vision_context(result)
            
            # Add to recent results
            self.recent_vision_results.append(result)
            if len(self.recent_vision_results) > 10:
                self.recent_vision_results.pop(0)
            
            # 🔧 CRITICAL FIX: Automatically save vision detections to short-term memory
            self._save_vision_detections_to_memory(result)
            
            # Clear processing flag
            self.vision_processing_active = False
            
            # Log before returning to ensure objects are in the return value
            return_data = {
                "success": result.success,
                "error": result.error,
                "data": {
                    "objects": result.objects,
                    "danger_detected": result.danger_detected,
                    "pleasure_detected": result.pleasure_detected,
                    "neucogar": result.neucogar,
                    "analysis": result.analysis,
                    "image_path": result.image_path,
                    "timestamp": result.timestamp
                }
            }
            self.logger.info(f"🔍 [VISION API] Returning from capture_and_analyze_vision with {len(return_data['data']['objects'])} objects: {return_data['data']['objects']}")
            return return_data
            
        except Exception as e:
            self.vision_processing_active = False
            self.logger.error(f"Vision capture and analysis failed: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": {}
            }
    
    def _update_vision_context(self, result: VisionAnalysisResult):
        """Update vision context with analysis results."""
        self.vision_context.update({
            "vision_active": True,
            "recent_objects": result.objects,
            "last_analysis_time": result.timestamp,
            "danger_level": 1.0 if result.danger_detected else 0.0,
            "pleasure_level": 1.0 if result.pleasure_detected else 0.0
        })
        
        # Update object concepts
        for obj in result.objects:
            if obj not in self.vision_context["object_concepts"]:
                self.vision_context["object_concepts"].append(obj)
        
        # Keep only recent objects
        if len(self.vision_context["object_concepts"]) > 20:
            self.vision_context["object_concepts"] = self.vision_context["object_concepts"][-20:]
    
    def _save_vision_detections_to_memory(self, result: VisionAnalysisResult):
        """
        🔧 CRITICAL FIX: Save vision detections to short-term memory in the format 
        that get_carl_thought expects. This ensures synchronization between vision 
        system and thought processing.
        """
        try:
            if not result.objects:
                return
                
            # Create comprehensive vision memory entry with all objects and analysis
            analysis = result.analysis if result.analysis else {}
            comprehensive_memory_entry = {
                "id": f"vision_comprehensive_{int(time.time())}",
                "type": "vision_comprehensive_analysis",
                "timestamp": result.timestamp,
                "source": "vision_system",
                "objects_detected": result.objects,  # Store all detected objects
                "detection_confidence": 0.8,
                "WHAT": analysis.get("what", f"Vision analysis detected {len(result.objects)} objects"),
                "WHERE": analysis.get("where", "Camera view"),
                "WHY": analysis.get("why", "Comprehensive vision analysis"),
                "HOW": analysis.get("how", "OpenAI Vision API analysis"),
                "WHO": analysis.get("who", "Carl (self)"),
                "emotions": ["curiosity"],
                "concepts": [obj.lower() for obj in result.objects],
                "vision_data": {
                    "objects": result.objects,
                    "object_details": result.object_details,
                    "detection_source": "openai_vision",
                    "confidence": 0.8,
                    "timestamp": result.timestamp,
                    "image_path": result.image_path,
                    "analysis": analysis,
                    "danger_detected": result.danger_detected,
                    "danger_reason": result.danger_reason,
                    "pleasure_detected": result.pleasure_detected,
                    "pleasure_reason": result.pleasure_reason,
                    "neucogar": result.neucogar
                },
                "analysis": analysis,  # Store analysis data for STM/LTM
                "neucogar_emotional_state": {
                    "primary": "curiosity",
                    "intensity": 0.6,
                    "neuro_coordinates": result.neucogar if result.neucogar else {
                        "dopamine": 0.6,
                        "serotonin": 0.5,
                        "noradrenaline": 0.4
                    }
                }
            }
            
            # Save comprehensive memory entry
            self._save_to_short_term_memory(comprehensive_memory_entry)
            self.logger.info(f"🔧 Saved comprehensive vision analysis to memory: {len(result.objects)} objects detected")
            
            # Also create individual entries for each object for detailed tracking
            for i, obj in enumerate(result.objects):
                # Generate visual_id for this detection
                visual_id = f"vision_{int(time.time())}_{i}_{obj.lower().replace(' ', '_')}"
                
                # Get object details if available
                object_details = result.object_details.get(obj, {}) if result.object_details else {}
                
                # Create memory entry in the format expected by get_carl_thought
                memory_entry = {
                    "id": visual_id,
                    "type": "vision_object_detection",
                    "timestamp": result.timestamp,
                    "source": "vision_system",
                    "object_name": obj,
                    "detection_confidence": 0.8,  # Default confidence for OpenAI detections
                    "visual_id": visual_id,
                    "WHAT": analysis.get("what", f"Vision: {obj}"),
                    "WHERE": analysis.get("where", "Camera view"),
                    "WHY": analysis.get("why", "Object detection during vision analysis"),
                    "HOW": analysis.get("how", "OpenAI Vision API analysis"),
                    "WHO": analysis.get("who", "Carl (self)"),
                    "emotions": ["curiosity"],
                    "concepts": [obj.lower()],
                    "vision_data": {
                        "object_name": obj,
                        "detection_source": "openai_vision",
                        "confidence": 0.8,
                        "visual_id": visual_id,
                        "timestamp": result.timestamp,
                        "image_path": result.image_path,
                        "object_details": object_details,
                        "analysis": analysis  # Include full analysis data
                    },
                    "object_details": object_details,  # Include detailed object information
                    "analysis": analysis,  # Store analysis data for STM/LTM
                    "neucogar_emotional_state": {
                        "primary": "curiosity",
                        "intensity": 0.6,
                        "neuro_coordinates": {
                            "dopamine": 0.6,
                            "serotonin": 0.5,
                            "noradrenaline": 0.4
                        }
                    }
                }
                
                # 🔧 FIX #3: Extract vision_analysis concepts (who, what, when, where, why, how) for STM/LTM
                vision_concepts = []
                if analysis:
                    # Extract concepts from analysis fields
                    for field in ['who', 'what', 'when', 'where', 'why', 'how']:
                        value = analysis.get(field, '')
                        if value:
                            # Split into individual words/concepts
                            words = value.lower().split()
                            for word in words:
                                # Filter out common words
                                if len(word) > 2 and word not in ['the', 'and', 'or', 'at', 'in', 'on', 'a', 'an']:
                                    vision_concepts.append(word)
                    
                    # Add vision concepts to memory entry
                    if vision_concepts:
                        memory_entry['vision_concepts'] = list(set(vision_concepts))
                        memory_entry['concepts'] = memory_entry.get('concepts', []) + vision_concepts
                
                # Save to short-term memory
                self._save_to_short_term_memory(memory_entry)
                
                # 🔧 FIX #3: Add vision concepts to LTM concept system
                if vision_concepts and hasattr(self, 'main_app') and self.main_app:
                    if hasattr(self.main_app, 'concept_system') and self.main_app.concept_system:
                        for concept in vision_concepts:
                            try:
                                self.main_app.concept_system.create_or_update_concept(
                                    word=concept,
                                    word_type="thing",  # Vision concepts are typically things
                                    event={"WHAT": f"Vision analysis: {concept}", "source": "vision_system"}
                                )
                            except Exception as e:
                                self.logger.error(f"⚠️ Error adding vision concept {concept} to LTM: {e}")
                
                self.logger.info(f"🔧 Saved vision detection to memory: {obj} (ID: {visual_id})")
                
        except Exception as e:
            self.logger.error(f"❌ Error saving vision detections to memory: {e}")
    
    def _save_to_short_term_memory(self, memory_entry: dict):
        """Save memory entry to short-term memory JSON file."""
        try:
            stm_file = 'short_term_memory.json'
            
            # Load existing short-term memory
            if os.path.exists(stm_file):
                with open(stm_file, 'r', encoding='utf-8') as f:
                    stm_data = json.load(f)
            else:
                stm_data = []
            
            # Add new memory entry to the beginning (most recent first)
            stm_data.insert(0, memory_entry)
            
            # Keep only the last 100 entries to prevent file from growing too large
            if len(stm_data) > 100:
                stm_data = stm_data[:100]
            
            # Save back to file
            with open(stm_file, 'w', encoding='utf-8') as f:
                json.dump(stm_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            self.logger.error(f"❌ Error saving to short-term memory: {e}")
    
    def get_vision_context_for_thought(self) -> Dict[str, Any]:
        """Get current vision context for integration with thought process."""
        return self.vision_context.copy()
    
    def get_vision_processing_status(self) -> Dict[str, Any]:
        """Get current vision processing status."""
        return {
            "vision_processing_active": self.vision_processing_active,
            "vision_enabled": self.vision_enabled,
            "camera_active": self.camera_active,
            "time_since_last_analysis": time.time() - self.last_vision_analysis_time,
            "recent_objects": self.vision_context.get("recent_objects", []),
            "danger_level": self.vision_context.get("danger_level", 0.0),
            "pleasure_level": self.vision_context.get("pleasure_level", 0.0)
        }
    
    def get_latest_vision_result(self) -> Optional[VisionAnalysisResult]:
        """Get the most recent vision analysis result."""
        if self.recent_vision_results:
            return self.recent_vision_results[-1]
        return None
    
    def save_object_detection_memory(self, object_name: str, object_color: str = "", 
                                   object_shape: str = "", confidence: float = 0.8,
                                   visual_id: str = None, image_data: str = None) -> str:
        """
        Save object detection as a memory event with associated image and visual_id.
        Enhanced with concept matching and fuzzy search for better object recognition.
        
        Args:
            object_name: Name of the detected object
            object_color: Color of the object (if available)
            object_shape: Shape of the object (if available)
            confidence: Detection confidence (0.0 to 1.0)
            visual_id: Unique identifier for this vision detection
            image_data: Path to captured image data
            
        Returns:
            str: Path to the saved memory file
        """
        try:
            # 🔧 ENHANCEMENT: Cross-reference detected object with concept files
            concept_match = self._find_concept_match(object_name, object_color, object_shape)
            
            # Capture current image
            image_path = self.capture_image()
            if not image_path:
                # Use test image if camera not available
                image_path = self.use_test_image()
            
            if not image_path:
                self.logger.warning("Could not capture image for object detection memory")
                return ""
            
            # Create memory data with visual_id association and concept matching
            memory_data = {
                "id": visual_id if visual_id else f"vision_{int(time.time())}",
                "type": "vision_object_detection",
                "timestamp": datetime.now().isoformat(),
                "filename": f"vision_capture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg",  # Use proper timestamp filename
                "filepath": image_path,  # Add filepath for memory system
                "WHAT": f"Vision: {object_name}",
                "WHERE": "Camera view",
                "WHY": "Object detection during vision analysis",
                "HOW": "Computer vision analysis",
                "WHO": "Carl (self)",
                "emotions": ["curiosity"],
                
                # 🔧 ENHANCEMENT: Add concept associations for better memory retrieval
                "concepts": concept_match.get("concepts", [object_name.lower()]),
                "needs": concept_match.get("needs", []),
                "goals": concept_match.get("goals", []),
                "concept_match": concept_match,
                "vision_data": {
                    "object_name": object_name,
                    "object_color": object_color,
                    "object_shape": object_shape,
                    "confidence": confidence,
                    "image_path": image_path,
                    "detection_time": datetime.now().isoformat(),
                    "visual_id": visual_id if visual_id else f"vision_{int(time.time())}",
                    "memory_association": {
                        "object_name": object_name,
                        "visual_id": visual_id if visual_id else f"vision_{int(time.time())}",
                        "recall_available": True
                    }
                },
                "neucogar_emotional_state": {
                    "primary": "curiosity",
                    "intensity": 0.6,
                    "neuro_coordinates": {
                        "dopamine": 0.6,
                        "serotonin": 0.5,
                        "noradrenaline": 0.4
                    }
                },
                "visual_memory_section": {
                    "object_detection": {
                        "name": object_name,
                        "color": object_color,
                        "shape": object_shape,
                        "confidence": confidence,
                        "visual_id": visual_id if visual_id else f"vision_{int(time.time())}",
                        "image_path": image_path,
                        "detection_timestamp": datetime.now().isoformat()
                    },
                    "analysis_results": {
                        "source": "vision_system",
                        "processing_status": "completed",
                        "memory_association": "stored",
                        "recall_available": True
                    }
                }
            }
            
            # Save to memory system if available
            if self.memory_system:
                try:
                    memory_filepath = self.memory_system.add_vision_memory(memory_data)
                    self.logger.info(f"Saved object detection memory: {memory_filepath}")
                    return memory_filepath
                except Exception as e:
                    self.logger.error(f"Error saving to memory system: {e}")
            
            # Fallback: save directly to file
            memory_dir = "memories"
            os.makedirs(memory_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"vision_{timestamp}_{object_name.lower().replace(' ', '_')}.json"
            filepath = os.path.join(memory_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(memory_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Saved object detection memory to file: {filepath}")
            return filepath
            
        except Exception as e:
            self.logger.error(f"Error saving object detection memory: {e}")
            return ""
    
    def _find_concept_match(self, object_name: str, object_color: str = "", object_shape: str = "") -> Dict:
        """
        Find matching concept files for detected vision objects.
        Uses JSON-based concept matching with fuzzy search fallback.
        
        Args:
            object_name: Name of the detected object
            object_color: Color of the object (if available)
            object_shape: Shape of the object (if available)
            
        Returns:
            Dict: Concept match data with concepts, needs, goals, and confidence
        """
        try:
            import os
            import json
            from difflib import SequenceMatcher
            
            concepts_dir = "concepts"
            if not os.path.exists(concepts_dir):
                self.logger.warning(f"Concepts directory not found: {concepts_dir}")
                return self._create_fallback_concept_match(object_name)
            
            # Search terms for matching
            search_terms = [object_name.lower()]
            if object_color:
                search_terms.append(object_color.lower())
            if object_shape:
                search_terms.append(object_shape.lower())
            
            best_match = None
            best_score = 0.0
            match_threshold = 0.6  # Minimum similarity threshold
            
            # Search through all concept files
            for filename in os.listdir(concepts_dir):
                if not filename.endswith('.json'):
                    continue
                    
                concept_file = os.path.join(concepts_dir, filename)
                try:
                    with open(concept_file, 'r', encoding='utf-8') as f:
                        concept_data = json.load(f)
                    
                    # Calculate match score
                    match_score = self._calculate_concept_match_score(concept_data, search_terms)
                    
                    if match_score > best_score and match_score >= match_threshold:
                        best_score = match_score
                        best_match = concept_data
                        best_match['match_score'] = match_score
                        best_match['source_file'] = filename
                        
                except Exception as e:
                    self.logger.warning(f"Error reading concept file {filename}: {e}")
                    continue
            
            # 🔧 ENHANCEMENT: Also search things directory for toy/object data
            things_match = self._search_things_directory_for_object(object_name, object_color, object_shape)
            if things_match and things_match.get('match_score', 0) > best_score:
                best_match = things_match
                best_score = things_match.get('match_score', 0)
                self.logger.info(f"Found things directory match: {things_match.get('name', 'unknown')} (score: {best_score:.2f})")
            
            if best_match:
                self.logger.info(f"Found concept match: {best_match.get('word', best_match.get('name', 'unknown'))} (score: {best_score:.2f})")
                concept_associations = self._extract_concept_associations(best_match)
                
                # 🔧 ENHANCEMENT: Cross-check with episodic memory for object-related events
                episodic_context = self._search_episodic_memory_for_object(object_name, concept_associations)
                if episodic_context:
                    concept_associations['episodic_context'] = episodic_context
                    concept_associations['has_episodic_memory'] = True
                else:
                    concept_associations['has_episodic_memory'] = False
                
                return concept_associations
            else:
                self.logger.info(f"No concept match found for '{object_name}', using fallback")
                fallback_match = self._create_fallback_concept_match(object_name)
                
                # Still check episodic memory even for fallback
                episodic_context = self._search_episodic_memory_for_object(object_name, fallback_match)
                if episodic_context:
                    fallback_match['episodic_context'] = episodic_context
                    fallback_match['has_episodic_memory'] = True
                else:
                    fallback_match['has_episodic_memory'] = False
                
                return fallback_match
                
        except Exception as e:
            self.logger.error(f"Error in concept matching: {e}")
            return self._create_fallback_concept_match(object_name)
    
    def _search_episodic_memory_for_object(self, object_name: str, concept_associations: Dict) -> Optional[Dict]:
        """
        Search episodic memory for object-related events to provide context for object recognition.
        
        Args:
            object_name: Name of the detected object
            concept_associations: Concept associations from concept files
            
        Returns:
            Dict: Episodic memory context if found, None otherwise
        """
        try:
            import os
            import json
            from datetime import datetime, timedelta
            
            memories_dir = "memories"
            episodic_dir = os.path.join(memories_dir, "episodic")
            
            if not os.path.exists(episodic_dir):
                return None
            
            # Search terms for episodic memory matching
            search_terms = [object_name.lower()]
            if concept_associations.get('concepts'):
                search_terms.extend([c.lower() for c in concept_associations['concepts']])
            if concept_associations.get('keywords'):
                search_terms.extend([k.lower() for k in concept_associations['keywords']])
            
            # Look for recent episodic memories (last 30 days)
            cutoff_date = datetime.now() - timedelta(days=30)
            relevant_memories = []
            
            for filename in os.listdir(episodic_dir):
                if not filename.endswith('.json'):
                    continue
                
                try:
                    memory_file = os.path.join(episodic_dir, filename)
                    with open(memory_file, 'r', encoding='utf-8') as f:
                        memory_data = json.load(f)
                    
                    # Check if memory is recent enough
                    memory_timestamp = memory_data.get('timestamp', '')
                    if memory_timestamp:
                        try:
                            memory_date = datetime.fromisoformat(memory_timestamp.replace('Z', '+00:00'))
                            if memory_date < cutoff_date:
                                continue
                        except:
                            continue
                    
                    # Check if memory contains object-related information
                    memory_text = str(memory_data).lower()
                    for term in search_terms:
                        if term in memory_text:
                            # Calculate relevance score
                            relevance_score = memory_text.count(term) / len(search_terms)
                            
                            relevant_memories.append({
                                'memory_data': memory_data,
                                'relevance_score': relevance_score,
                                'timestamp': memory_timestamp,
                                'filename': filename
                            })
                            break
                            
                except Exception as e:
                    continue
            
            if relevant_memories:
                # Sort by relevance and recency
                relevant_memories.sort(key=lambda x: (x['relevance_score'], x['timestamp']), reverse=True)
                
                # Return top 3 most relevant memories
                top_memories = relevant_memories[:3]
                
                episodic_context = {
                    'object_name': object_name,
                    'related_memories': top_memories,
                    'total_found': len(relevant_memories),
                    'search_terms_used': search_terms
                }
                
                self.logger.info(f"Found {len(relevant_memories)} episodic memories for object '{object_name}'")
                return episodic_context
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching episodic memory for object '{object_name}': {e}")
            return None
    
    def _calculate_concept_match_score(self, concept_data: Dict, search_terms: List[str]) -> float:
        """Calculate similarity score between concept data and search terms."""
        try:
            from difflib import SequenceMatcher
            
            score = 0.0
            total_weight = 0.0
            
            # Check keywords (highest weight)
            keywords = concept_data.get('keywords', [])
            for keyword in keywords:
                keyword_lower = keyword.lower()
                for term in search_terms:
                    similarity = SequenceMatcher(None, term, keyword_lower).ratio()
                    if similarity > 0.5:  # Partial match threshold
                        score += similarity * 1.0  # High weight for keywords
                        total_weight += 1.0
            
            # Check related concepts (medium weight)
            related_concepts = concept_data.get('related_concepts', [])
            for concept in related_concepts:
                concept_lower = concept.lower()
                for term in search_terms:
                    similarity = SequenceMatcher(None, term, concept_lower).ratio()
                    if similarity > 0.5:
                        score += similarity * 0.7  # Medium weight for related concepts
                        total_weight += 0.7
            
            # Check word field (medium weight)
            word = concept_data.get('word', '').lower()
            for term in search_terms:
                similarity = SequenceMatcher(None, term, word).ratio()
                if similarity > 0.5:
                    score += similarity * 0.8  # Medium-high weight for word field
                    total_weight += 0.8
            
            # Check semantic relationships (lower weight)
            semantic_relationships = concept_data.get('semantic_relationships', [])
            for relationship in semantic_relationships:
                relationship_lower = relationship.lower()
                for term in search_terms:
                    similarity = SequenceMatcher(None, term, relationship_lower).ratio()
                    if similarity > 0.5:
                        score += similarity * 0.5  # Lower weight for semantic relationships
                        total_weight += 0.5
            
            return score / total_weight if total_weight > 0 else 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating concept match score: {e}")
            return 0.0
    
    def _extract_concept_associations(self, concept_data: Dict) -> Dict:
        """Extract concept associations (concepts, needs, goals) from matched concept data."""
        try:
            # Handle both concept files and things directory data
            if concept_data.get('source') == 'things_directory':
                # Extract from things directory data
                return {
                    "concepts": concept_data.get('keywords', []) + concept_data.get('related_concepts', []),
                    "needs": concept_data.get('needs', []),
                    "goals": concept_data.get('goals', []),
                    "skills": concept_data.get('skills', []),
                    "senses": concept_data.get('senses', []),
                    "emotional_associations": concept_data.get('emotional_associations', {}),
                    "neucogar_associations": concept_data.get('neucogar_associations', {}),
                    "match_confidence": concept_data.get('match_score', 0.0),
                    "source_concept": concept_data.get('name', 'unknown'),
                    "source_file": concept_data.get('source_file', 'unknown'),
                    "description": concept_data.get('description', ''),
                    "type": concept_data.get('type', 'object')
                }
            else:
                # Extract from concept files
                return {
                    "concepts": concept_data.get('keywords', []) + concept_data.get('related_concepts', []),
                    "needs": concept_data.get('linked_needs', []),
                    "goals": concept_data.get('linked_goals', []),
                    "skills": concept_data.get('linked_skills', []),
                    "senses": concept_data.get('linked_senses', []),
                    "emotional_associations": concept_data.get('emotional_associations', {}),
                    "neucogar_associations": concept_data.get('neucogar_emotional_associations', {}),
                    "match_confidence": concept_data.get('match_score', 0.0),
                    "source_concept": concept_data.get('word', 'unknown'),
                    "source_file": concept_data.get('source_file', 'unknown')
                }
        except Exception as e:
            self.logger.error(f"Error extracting concept associations: {e}")
            return self._create_fallback_concept_match("unknown")
    
    def _search_things_directory_for_object(self, object_name: str, object_color: str = "", object_shape: str = "") -> Optional[Dict]:
        """
        Search things directory for toy/object data that matches the detected object.
        
        Args:
            object_name: Name of the detected object
            object_color: Color of the object (if available)
            object_shape: Shape of the object (if available)
            
        Returns:
            Dict: Thing data with match score if found, None otherwise
        """
        try:
            import os
            import json
            
            things_dir = "things"
            if not os.path.exists(things_dir):
                self.logger.warning(f"Things directory not found: {things_dir}")
                return None
            
            object_lower = object_name.lower()
            best_match = None
            best_score = 0.0
            match_threshold = 0.5  # Minimum similarity threshold for things
            
            # Search through all things files
            for filename in os.listdir(things_dir):
                if not filename.endswith('.json'):
                    continue
                
                thing_file = os.path.join(things_dir, filename)
                try:
                    with open(thing_file, 'r', encoding='utf-8') as f:
                        thing_data = json.load(f)
                    
                    # Calculate match score
                    match_score = 0.0
                    
                    # Check against thing name
                    thing_name = thing_data.get('name', '').lower()
                    if thing_name and object_lower in thing_name:
                        match_score += 0.8
                    elif thing_name and any(word in object_lower for word in thing_name.split()):
                        match_score += 0.6
                    
                    # Check against keywords
                    keywords = thing_data.get('keywords', [])
                    for keyword in keywords:
                        if keyword.lower() in object_lower or object_lower in keyword.lower():
                            match_score += 0.4
                    
                    # Check against related concepts
                    related_concepts = thing_data.get('related_concepts', [])
                    for concept in related_concepts:
                        if concept.lower() in object_lower or object_lower in concept.lower():
                            match_score += 0.3
                    
                    # Special handling for Chomp and dinosaur-related objects
                    if 'chomp' in object_lower or 'dino' in object_lower or 'dinosaur' in object_lower:
                        if 'chomp' in thing_name or 'dino' in thing_name:
                            match_score += 0.5
                    
                    # Check against color if available
                    if object_color:
                        thing_color = thing_data.get('color', '').lower()
                        if thing_color and object_color.lower() in thing_color:
                            match_score += 0.3
                    
                    # Check against shape if available
                    if object_shape:
                        thing_shape = thing_data.get('shape', '').lower()
                        if thing_shape and object_shape.lower() in thing_shape:
                            match_score += 0.3
                    
                    if match_score > best_score and match_score >= match_threshold:
                        best_score = match_score
                        best_match = thing_data.copy()
                        best_match['match_score'] = min(match_score, 1.0)
                        best_match['source_file'] = filename
                        best_match['source'] = 'things_directory'
                
                except Exception as e:
                    self.logger.warning(f"Error reading thing file {filename}: {e}")
                    continue
            
            if best_match:
                self.logger.info(f"Found things directory match: {best_match.get('name', 'unknown')} (score: {best_score:.2f})")
                return best_match
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error searching things directory: {e}")
            return None

    def _create_fallback_concept_match(self, object_name: str) -> Dict:
        """Create fallback concept match when no JSON concept is found."""
        return {
            "concepts": [object_name.lower()],
            "needs": [],
            "goals": [],
            "skills": [],
            "senses": [],
            "emotional_associations": {"curiosity": 0.5},
            "neucogar_associations": {"primary": "curiosity", "intensity": 0.5},
            "match_confidence": 0.3,
            "source_concept": object_name.lower(),
            "source_file": "fallback"
        }
    
    def _update_motion_tracking_based_on_exploration(self):
        """
        Update motion tracking based on exploration_active flag from InnerSelf.
        This implements System Issue 2: Motion tracking only when exploring.
        """
        try:
            if not self.main_app:
                return
                
            # Check if InnerSelf is available and get exploration state
            exploration_active = False
            if hasattr(self.main_app, 'inner_self') and self.main_app.inner_self:
                exploration_active = getattr(self.main_app.inner_self, 'exploration_active', False)
            
            # Get current motion tracking state
            current_motion_enabled = getattr(self, '_motion_tracking_enabled', False)
            
            # Update motion tracking based on exploration state
            if exploration_active and not current_motion_enabled:
                # Enable motion tracking during exploration
                if hasattr(self.main_app, '_enable_motion_detection'):
                    if self.main_app._enable_motion_detection():
                        self._motion_tracking_enabled = True
                        self.logger.info("🎯 Motion tracking enabled for PDB exploration")
                    else:
                        self.logger.warning("⚠️ Failed to enable motion tracking for exploration")
                        
            elif not exploration_active and current_motion_enabled:
                # Disable motion tracking when not exploring
                if hasattr(self.main_app, '_disable_motion_detection'):
                    if self.main_app._disable_motion_detection():
                        self._motion_tracking_enabled = False
                        self.logger.info("🎯 Motion tracking disabled - exploration complete")
                    else:
                        self.logger.warning("⚠️ Failed to disable motion tracking")
                        
        except Exception as e:
            self.logger.error(f"❌ Error updating motion tracking based on exploration: {e}")

    def cleanup(self):
        """Clean up camera resources."""
        if self.camera:
            self.camera.release()
        self.camera_active = False
        self.vision_enabled = False
