#!/usr/bin/env python3
"""
Vision → Flask Stabilization System

Implements debouncing, deduplication, and proper cadence control for vision events
sent to Flask server. Prevents spam and ensures stable communication.
"""

import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import queue
from vision_events import VisionEvent, VisionDetection, VisionCacheEntry

@dataclass
class VisionStabilizationEntry:
    """Entry for vision stabilization tracking."""
    detection: VisionDetection
    last_sent: str
    send_count: int = 0
    is_active: bool = True

class VisionStabilizationSystem:
    """
    Vision stabilization system with debouncing and deduplication.
    
    Features:
    - Debouncing: Prevents rapid-fire detection spam
    - Deduplication: Avoids sending duplicate detections
    - Queue management: Manages detection queue with priorities
    - TTL-based caching: Automatically expires old detections
    - Connection-aware: Only sends when ARC is connected
    """
    
    def __init__(self, 
                 debounce_time: float = 30.0,  # 30 seconds debounce
                 max_queue_size: int = 100,
                 ttl_seconds: int = 300,  # 5 minutes TTL
                 arc_connection_check: Optional[callable] = None):
        
        self.debounce_time = debounce_time
        self.max_queue_size = max_queue_size
        self.ttl_seconds = ttl_seconds
        self.arc_connection_check = arc_connection_check
        
        self.logger = logging.getLogger(__name__)
        
        # Detection cache with TTL
        self.detection_cache: Dict[str, VisionCacheEntry] = {}
        
        # Send queue for Flask
        self.send_queue = queue.Queue(maxsize=max_queue_size)
        
        # Statistics
        self.stats = {
            "total_detections": 0,
            "total_sent": 0,
            "total_dropped": 0,
            "total_debounced": 0,
            "total_deduplicated": 0,
            "queue_overflows": 0,
            "connection_errors": 0
        }
        
        # Threading
        self.running = False
        self.send_thread = None
        self.lock = threading.Lock()
        
        # Start the send thread
        self.start()
    
    def start(self):
        """Start the vision stabilization system."""
        if not self.running:
            self.running = True
            self.send_thread = threading.Thread(target=self._send_worker, daemon=True)
            self.send_thread.start()
            self.logger.info("Vision stabilization system started")
    
    def stop(self):
        """Stop the vision stabilization system."""
        self.running = False
        if self.send_thread:
            self.send_thread.join(timeout=1.0)
        self.logger.info("Vision stabilization system stopped")
    
    def process_detection(self, detection: VisionDetection) -> bool:
        """
        Process a new vision detection.
        
        Args:
            detection: The vision detection to process
            
        Returns:
            True if detection was queued for sending, False if dropped
        """
        try:
            with self.lock:
                self.stats["total_detections"] += 1
                
                # Create unique identifier for the detection
                detection_id = self._create_detection_id(detection)
                
                # Check if we should send this detection
                should_send = self._should_send_detection(detection_id, detection)
                
                if should_send:
                    # Add to send queue
                    try:
                        self.send_queue.put_nowait((detection_id, detection))
                        self.stats["total_sent"] += 1
                        
                        # Update cache
                        self._update_cache(detection_id, detection)
                        
                        self.logger.info(f"Queued detection: {detection.name} ({detection.color})")
                        return True
                        
                    except queue.Full:
                        self.stats["queue_overflows"] += 1
                        self.stats["total_dropped"] += 1
                        self.logger.warning(f"Send queue full, dropped detection: {detection.name}")
                        return False
                else:
                    # Update cache without sending
                    self._update_cache(detection_id, detection)
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error processing detection: {e}")
            self.stats["total_dropped"] += 1
            return False
    
    def _create_detection_id(self, detection: VisionDetection) -> str:
        """Create a unique identifier for a detection."""
        return f"{detection.name}|{detection.color}"
    
    def _should_send_detection(self, detection_id: str, detection: VisionDetection) -> bool:
        """
        Determine if a detection should be sent based on debouncing and deduplication rules.
        
        Rules:
        1. Not in recent queue (debouncing)
        2. 30s cool-down elapsed for that identifier
        3. ARC connected (if connection check available)
        """
        current_time = datetime.now()
        
        # Check cache for existing entry
        if detection_id in self.detection_cache:
            cache_entry = self.detection_cache[detection_id]
            
            # Check if cool-down period has elapsed
            last_sent_time = datetime.fromisoformat(cache_entry.last_sent)
            time_since_last = current_time - last_sent_time
            
            if time_since_last.total_seconds() < self.debounce_time:
                self.stats["total_debounced"] += 1
                self.logger.debug(f"Debounced detection: {detection_id} (last sent {time_since_last.total_seconds():.1f}s ago)")
                return False
            
            # Check if detection is significantly different (confidence change > 0.1)
            confidence_diff = abs(detection.confidence - cache_entry.detection.confidence)
            if confidence_diff < 0.1:
                self.stats["total_deduplicated"] += 1
                self.logger.debug(f"Deduplicated detection: {detection_id} (confidence diff: {confidence_diff:.3f})")
                return False
        
        # Check ARC connection if available
        if self.arc_connection_check and not self.arc_connection_check():
            self.stats["connection_errors"] += 1
            self.logger.warning(f"ARC not connected, dropping detection: {detection_id}")
            return False
        
        return True
    
    def _update_cache(self, detection_id: str, detection: VisionDetection):
        """Update the detection cache."""
        current_time = datetime.now()
        
        if detection_id in self.detection_cache:
            # Update existing entry
            cache_entry = self.detection_cache[detection_id]
            cache_entry.detection = detection
            cache_entry.send_count += 1
        else:
            # Create new entry
            cache_entry = VisionCacheEntry(
                detection=detection,
                last_sent=current_time.isoformat(),
                send_count=1
            )
        
        self.detection_cache[detection_id] = cache_entry
    
    def _send_worker(self):
        """Worker thread that sends detections to Flask."""
        while self.running:
            try:
                # Get detection from queue with timeout
                try:
                    detection_id, detection = self.send_queue.get(timeout=1.0)
                except queue.Empty:
                    continue
                
                # Send to Flask
                success = self._send_to_flask(detection)
                
                if success:
                    # Update last sent time
                    with self.lock:
                        if detection_id in self.detection_cache:
                            self.detection_cache[detection_id].last_sent = datetime.now().isoformat()
                
                # Mark task as done
                self.send_queue.task_done()
                
            except Exception as e:
                self.logger.error(f"Error in send worker: {e}")
                time.sleep(0.1)
    
    def _send_to_flask(self, detection: VisionDetection) -> bool:
        """
        Send detection to Flask server.
        
        Args:
            detection: The detection to send
            
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            # Create detection payload
            payload = {
                "name": detection.name,
                "color": detection.color,
                "confidence": detection.confidence,
                "timestamp": detection.timestamp,
                "location": detection.location,
                "size": detection.size
            }
            
            # TODO: Implement actual Flask sending logic
            # For now, just log the detection
            self.logger.info(f"📡 Sending to Flask: {detection.name} ({detection.color}) - confidence: {detection.confidence:.3f}")
            
            # Simulate network delay
            time.sleep(0.1)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error sending to Flask: {e}")
            return False
    
    def cleanup_expired_cache(self):
        """Remove expired entries from the detection cache."""
        try:
            current_time = datetime.now()
            expired_entries = []
            
            with self.lock:
                for detection_id, cache_entry in self.detection_cache.items():
                    last_sent_time = datetime.fromisoformat(cache_entry.last_sent)
                    time_since_last = current_time - last_sent_time
                    
                    if time_since_last.total_seconds() > self.ttl_seconds:
                        expired_entries.append(detection_id)
                
                # Remove expired entries
                for detection_id in expired_entries:
                    del self.detection_cache[detection_id]
                
                if expired_entries:
                    self.logger.info(f"Cleaned up {len(expired_entries)} expired cache entries")
            
        except Exception as e:
            self.logger.error(f"Error cleaning up expired cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        with self.lock:
            stats = self.stats.copy()
            stats.update({
                "cache_size": len(self.detection_cache),
                "queue_size": self.send_queue.qsize(),
                "running": self.running,
                "last_updated": datetime.now().isoformat()
            })
            return stats
    
    def get_cache_summary(self) -> Dict[str, Any]:
        """Get a summary of the detection cache."""
        with self.lock:
            summary = {
                "total_entries": len(self.detection_cache),
                "entries": {}
            }
            
            for detection_id, cache_entry in self.detection_cache.items():
                summary["entries"][detection_id] = {
                    "name": cache_entry.detection.name,
                    "color": cache_entry.detection.color,
                    "confidence": cache_entry.detection.confidence,
                    "send_count": cache_entry.send_count,
                    "last_sent": cache_entry.last_sent,
                    "is_active": cache_entry.is_active
                }
            
            return summary

class FlaskVisionServer:
    """
    Flask server-side vision detection cache with TTL.
    
    Implements server-side deduplication and caching to prevent
    duplicate processing of the same detection.
    """
    
    def __init__(self, ttl_seconds: int = 30):
        self.ttl_seconds = ttl_seconds
        self.logger = logging.getLogger(__name__)
        
        # Detection cache with TTL
        self.detection_cache: Dict[str, Dict] = {}
        
        # Statistics
        self.stats = {
            "total_received": 0,
            "total_processed": 0,
            "total_dropped": 0,
            "total_deduplicated": 0
        }
    
    def process_detection(self, detection_data: Dict) -> bool:
        """
        Process a detection received from the vision system.
        
        Args:
            detection_data: Detection data from vision system
            
        Returns:
            True if detection was processed, False if dropped
        """
        try:
            self.stats["total_received"] += 1
            
            # Create unique identifier
            detection_id = f"{detection_data.get('name', '')}|{detection_data.get('color', '')}"
            
            # Check if we should process this detection
            if self._should_process_detection(detection_id, detection_data):
                # Process the detection
                self._process_detection_logic(detection_data)
                
                # Update cache
                self._update_cache(detection_id, detection_data)
                
                self.stats["total_processed"] += 1
                self.logger.info(f"Processed detection: {detection_id}")
                return True
            else:
                self.stats["total_dropped"] += 1
                self.logger.debug(f"Dropped duplicate detection: {detection_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing detection: {e}")
            self.stats["total_dropped"] += 1
            return False
    
    def _should_process_detection(self, detection_id: str, detection_data: Dict) -> bool:
        """Determine if a detection should be processed."""
        current_time = time.time()
        
        if detection_id in self.detection_cache:
            cache_entry = self.detection_cache[detection_id]
            
            # Check TTL
            if current_time - cache_entry["timestamp"] < self.ttl_seconds:
                self.stats["total_deduplicated"] += 1
                return False
        
        return True
    
    def _process_detection_logic(self, detection_data: Dict):
        """Process the detection (implement actual logic here)."""
        # TODO: Implement actual detection processing logic
        # This could include:
        # - Updating robot behavior
        # - Triggering actions
        # - Updating internal state
        # - Sending notifications
        
        name = detection_data.get("name", "")
        color = detection_data.get("color", "")
        confidence = detection_data.get("confidence", 0.0)
        
        self.logger.info(f"🎯 Processing detection: {name} ({color}) - confidence: {confidence:.3f}")
    
    def _update_cache(self, detection_id: str, detection_data: Dict):
        """Update the detection cache."""
        self.detection_cache[detection_id] = {
            "data": detection_data,
            "timestamp": time.time()
        }
    
    def cleanup_expired_cache(self):
        """Remove expired entries from the cache."""
        current_time = time.time()
        expired_entries = []
        
        for detection_id, cache_entry in self.detection_cache.items():
            if current_time - cache_entry["timestamp"] > self.ttl_seconds:
                expired_entries.append(detection_id)
        
        for detection_id in expired_entries:
            del self.detection_cache[detection_id]
        
        if expired_entries:
            self.logger.info(f"Cleaned up {len(expired_entries)} expired cache entries")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get server statistics."""
        stats = self.stats.copy()
        stats.update({
            "cache_size": len(self.detection_cache),
            "ttl_seconds": self.ttl_seconds
        })
        return stats

# Global instances
vision_stabilization = VisionStabilizationSystem()
flask_vision_server = FlaskVisionServer()
