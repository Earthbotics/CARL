#!/usr/bin/env python3
"""
Enhanced Eye Expression System for CARL

This module provides improved eye expression handling with:
1. Better error recovery and fallback mechanisms
2. Rate limiting coordination with other EZ-Robot commands
3. Graceful degradation when ARC is unavailable
4. Retry logic for failed expressions
5. Connection health monitoring
"""

import time
import threading
from typing import Optional, Dict, List
from enum import Enum
import logging

class EyeExpressionState(Enum):
    """Eye expression states for tracking."""
    SUCCESS = "success"
    FAILED = "failed"
    PENDING = "pending"
    RETRYING = "retrying"

class EnhancedEyeExpressionSystem:
    """
    Enhanced eye expression system with improved error handling and rate limiting.
    """
    
    def __init__(self, ez_robot=None):
        self.ez_robot = ez_robot
        self.logger = logging.getLogger(__name__)
        
        # Expression tracking
        self.current_expression = "eyes_open"
        self.previous_expression = "eyes_open"
        self.expression_history = []
        self.failed_expressions = []
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds
        self.expression_timeout = 5.0  # seconds
        
        # Rate limiting coordination
        self.last_expression_time = 0
        self.min_expression_interval = 0.5  # seconds
        self.expression_lock = threading.Lock()
        
        # Connection health
        self.consecutive_failures = 0
        self.max_consecutive_failures = 5
        self.connection_healthy = True
        
    def set_eye_expression(self, emotion: str, force: bool = False) -> bool:
        """
        Set eye expression with enhanced error handling and rate limiting.
        
        Args:
            emotion: The emotion to express
            force: Force expression even if rate limited
            
        Returns:
            True if expression was set successfully, False otherwise
        """
        if not self.ez_robot:
            self.logger.warning("EZ-Robot not available for eye expression")
            return False
        
        # Check connection health
        if not self.connection_healthy and not force:
            self.logger.warning("Connection unhealthy, skipping eye expression")
            return False
        
        # Rate limiting check
        current_time = time.time()
        time_since_last = current_time - self.last_expression_time
        
        if time_since_last < self.min_expression_interval and not force:
            self.logger.info(f"Rate limiting eye expression: {emotion} (waiting {self.min_expression_interval - time_since_last:.2f}s)")
            return False
        
        with self.expression_lock:
            try:
                # Map emotion to eye expression
                emotion_to_eye = {
                    'joy': 'eyes_joy',
                    'happiness': 'eyes_joy',
                    'happy': 'eyes_joy',
                    'anger': 'eyes_anger',
                    'angry': 'eyes_anger',
                    'fear': 'eyes_fear',
                    'afraid': 'eyes_fear',
                    'surprise': 'eyes_surprise',
                    'surprised': 'eyes_surprise',
                    'disgust': 'eyes_disgust',
                    'disgusted': 'eyes_disgust',
                    'sadness': 'eyes_sad',
                    'sad': 'eyes_sad',
                    'default': 'eyes_open',
                    'neutral': 'eyes_open'
                }
                
                eye_expression = emotion_to_eye.get(emotion.lower(), 'eyes_open')
                
                # Store previous expression
                if self.current_expression != eye_expression:
                    self.previous_expression = self.current_expression
                
                # Attempt to set expression with retry logic
                success = self._set_expression_with_retry(eye_expression)
                
                if success:
                    self.current_expression = eye_expression
                    self.last_expression_time = current_time
                    self.consecutive_failures = 0
                    self.connection_healthy = True
                    
                    # Log success
                    self.logger.info(f"✅ Eye expression set successfully: {emotion} -> {eye_expression}")
                    
                    # Update history
                    self.expression_history.append({
                        'timestamp': current_time,
                        'emotion': emotion,
                        'expression': eye_expression,
                        'state': EyeExpressionState.SUCCESS
                    })
                    
                    return True
                else:
                    # Handle failure
                    self.consecutive_failures += 1
                    self.failed_expressions.append({
                        'timestamp': current_time,
                        'emotion': emotion,
                        'expression': eye_expression,
                        'attempts': self.max_retries
                    })
                    
                    # Check if connection is unhealthy
                    if self.consecutive_failures >= self.max_consecutive_failures:
                        self.connection_healthy = False
                        self.logger.warning(f"Connection marked as unhealthy after {self.consecutive_failures} consecutive failures")
                    
                    self.logger.warning(f"❌ Failed to set eye expression: {emotion} -> {eye_expression}")
                    return False
                    
            except Exception as e:
                self.logger.error(f"Error setting eye expression '{emotion}': {e}")
                return False
    
    def _set_expression_with_retry(self, eye_expression: str) -> bool:
        """
        Set eye expression with retry logic.
        
        Args:
            eye_expression: The eye expression to set
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(self.max_retries):
            try:
                # Use the EZ-Robot's set_eye_expression method
                result = self.ez_robot.set_eye_expression(eye_expression)
                
                if result is not None:
                    return True
                else:
                    if attempt < self.max_retries - 1:
                        self.logger.info(f"Retrying eye expression '{eye_expression}' (attempt {attempt + 2}/{self.max_retries})")
                        time.sleep(self.retry_delay)
                    else:
                        self.logger.warning(f"Failed to set eye expression '{eye_expression}' after {self.max_retries} attempts")
                        return False
                        
            except Exception as e:
                if attempt < self.max_retries - 1:
                    self.logger.info(f"Exception during eye expression retry: {e}")
                    time.sleep(self.retry_delay)
                else:
                    self.logger.error(f"Exception setting eye expression '{eye_expression}': {e}")
                    return False
        
        return False
    
    def set_waiting_expression(self) -> bool:
        """
        Set eyes to waiting state with enhanced error handling.
        
        Returns:
            True if successful, False otherwise
        """
        return self.set_eye_expression("waiting", force=True)
    
    def restore_previous_expression(self) -> bool:
        """
        Restore the previous eye expression with enhanced error handling.
        
        Returns:
            True if successful, False otherwise
        """
        if self.previous_expression:
            return self.set_eye_expression(self.previous_expression, force=True)
        else:
            return self.set_eye_expression("neutral", force=True)
    
    def get_expression_stats(self) -> Dict:
        """
        Get statistics about eye expression usage.
        
        Returns:
            Dictionary with expression statistics
        """
        return {
            'current_expression': self.current_expression,
            'previous_expression': self.previous_expression,
            'total_expressions': len(self.expression_history),
            'failed_expressions': len(self.failed_expressions),
            'consecutive_failures': self.consecutive_failures,
            'connection_healthy': self.connection_healthy,
            'recent_expressions': self.expression_history[-10:] if self.expression_history else []
        }
    
    def reset_connection_health(self):
        """Reset connection health status."""
        self.connection_healthy = True
        self.consecutive_failures = 0
        self.logger.info("Eye expression connection health reset")
    
    def clear_failed_expressions(self):
        """Clear the failed expressions list."""
        self.failed_expressions.clear()
        self.logger.info("Cleared failed expressions list") 