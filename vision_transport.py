#!/usr/bin/env python3
"""
Vision Transport System
=======================

Decouples ARC vision posting from EZ-Robot connection status with:
- Exponential backoff with jitter
- Circuit breaker pattern
- Independent retry mechanism
- Event caching to STM
"""

import json
import time
import random
import threading
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging
import hashlib
from PIL import Image
import io
from vision_events import VisionEvent

class VisionTransport:
    """
    Decoupled vision transport system with retry logic and circuit breaker.
    """
    
    def __init__(self, flask_url: str = "http://localhost:5000", 
                 max_retries: int = 5, 
                 circuit_breaker_window: int = 30):
        """
        Initialize vision transport.
        
        Args:
            flask_url: Flask server URL
            max_retries: Maximum retry attempts
            circuit_breaker_window: Circuit breaker window in seconds
        """
        self.flask_url = flask_url
        self.max_retries = max_retries
        self.circuit_breaker_window = circuit_breaker_window
        
        # Circuit breaker state
        self.failure_count = 0
        self.last_failure_time = None
        self.circuit_open = False
        
        # Retry state
        self.retry_delay = 1.0  # Start with 1 second
        self.max_delay = 5.0    # Maximum 5 second delay
        
        # Event cache for when Flask is unavailable
        self.event_cache: List[VisionEvent] = []
        self.max_cache_size = 100
        
        # Threading
        self.lock = threading.Lock()
        self.logger = logging.getLogger(__name__)
        
    def post_vision_event(self, event: VisionEvent) -> bool:
        """
        Post vision event to Flask with retry logic.
        
        Args:
            event: Vision event to post
            
        Returns:
            True if successful, False otherwise
        """
        # Check circuit breaker
        if self._is_circuit_open():
            self._cache_event(event)
            return False
            
        # Try to post with exponential backoff
        for attempt in range(self.max_retries):
            try:
                success = self._attempt_post(event)
                if success:
                    self._on_success()
                    return True
                else:
                    self._on_failure()
                    
            except Exception as e:
                self.logger.error(f"Vision transport error on attempt {attempt + 1}: {e}")
                self._on_failure()
                
            # Exponential backoff with jitter
            if attempt < self.max_retries - 1:
                delay = self._calculate_backoff_delay(attempt)
                time.sleep(delay)
                
        # All attempts failed
        self._cache_event(event)
        return False
    
    def _attempt_post(self, event: VisionEvent) -> bool:
        """Attempt to post a single vision event."""
        try:
            payload = {
                "timestamp": event.timestamp,
                "label": event.label,
                "bbox": event.bbox,
                "confidence": event.confidence,
                "image_hash": event.image_hash,
                "source": event.source
            }
            
            response = requests.post(
                f"{self.flask_url}/vision/event",
                json=payload,
                timeout=5.0
            )
            
            if response.status_code == 200:
                self.logger.info(f"Vision event posted successfully: {event.label}")
                return True
            else:
                self.logger.warning(f"Vision event post failed with status {response.status_code}")
                return False
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Vision transport request failed: {e}")
            return False
    
    def _calculate_backoff_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        base_delay = min(self.retry_delay * (2 ** attempt), self.max_delay)
        jitter = random.uniform(0, 0.1 * base_delay)  # 10% jitter
        return base_delay + jitter
    
    def _is_circuit_open(self) -> bool:
        """Check if circuit breaker is open."""
        with self.lock:
            if not self.circuit_open:
                return False
                
            # Check if circuit breaker window has passed
            if (self.last_failure_time and 
                datetime.now() - self.last_failure_time > timedelta(seconds=self.circuit_breaker_window)):
                self.circuit_open = False
                self.failure_count = 0
                self.logger.info("Circuit breaker reset")
                return False
                
            return True
    
    def _on_success(self):
        """Handle successful post."""
        with self.lock:
            self.failure_count = 0
            self.circuit_open = False
            self.retry_delay = max(1.0, self.retry_delay * 0.5)  # Reduce delay on success
    
    def _on_failure(self):
        """Handle failed post."""
        with self.lock:
            self.failure_count += 1
            self.last_failure_time = datetime.now()
            self.retry_delay = min(self.max_delay, self.retry_delay * 2)  # Increase delay on failure
            
            # Open circuit breaker if too many failures
            if self.failure_count >= 3:
                self.circuit_open = True
                self.logger.warning("Circuit breaker opened due to repeated failures")
    
    def _cache_event(self, event: VisionEvent):
        """Cache event for later processing."""
        with self.lock:
            self.event_cache.append(event)
            if len(self.event_cache) > self.max_cache_size:
                self.event_cache.pop(0)  # Remove oldest event
            self.logger.info(f"Cached vision event: {event.label}")
    
    def get_cached_events(self) -> List[VisionEvent]:
        """Get all cached events and clear cache."""
        with self.lock:
            events = self.event_cache.copy()
            self.event_cache.clear()
            return events
    
    def calculate_image_hash(self, image_data: bytes) -> str:
        """Calculate hash of image data."""
        return hashlib.md5(image_data).hexdigest()
    
    def create_vision_event(self, label: str, bbox: List[float], 
                          confidence: float, image_data: Optional[bytes] = None) -> VisionEvent:
        """Create a vision event with optional image hash."""
        image_hash = None
        if image_data:
            image_hash = self.calculate_image_hash(image_data)
            
        return VisionEvent(
            name=label,
            label=label,
            confidence=confidence,
            timestamp=datetime.now().isoformat(),
            bbox=bbox,
            image_hash=image_hash
        )
