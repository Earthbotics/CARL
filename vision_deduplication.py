#!/usr/bin/env python3
"""
Vision Deduplication System
===========================

Implements deduplication for vision events to prevent spam and improve
pipeline robustness. Uses TTL-based caching to ensure events are only
processed once per object/color combination within a time window.
"""

import time
import logging
from typing import Dict, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict
from vision_events import VisionEvent

class VisionDeduplicationSystem:
    """
    Vision deduplication system with TTL-based caching.
    
    Prevents duplicate vision events by maintaining a cache of recent
    detections with configurable time-to-live (TTL) values.
    """
    
    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize the deduplication system.
        
        Args:
            ttl_seconds: Time-to-live for cached events in seconds
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.logger = logging.getLogger(__name__)
        
        # Statistics
        self.total_events = 0
        self.duplicate_events = 0
        self.unique_events = 0
        
        self.logger.info(f"Vision deduplication system initialized with TTL: {ttl_seconds}s")
    
    def is_duplicate(self, event: VisionEvent) -> bool:
        """
        Check if a vision event is a duplicate.
        
        Args:
            event: VisionEvent to check
            
        Returns:
            True if event is a duplicate, False otherwise
        """
        self.total_events += 1
        
        # Clean expired entries
        self._cleanup_expired()
        
        # Create cache key
        cache_key = f"{event.name}|{event.color}"
        current_time = time.time()
        
        # Check if we have a recent entry for this object/color
        if cache_key in self.cache:
            last_seen = self.cache[cache_key]
            if current_time - last_seen < self.ttl_seconds:
                self.duplicate_events += 1
                self.logger.debug(f"Duplicate vision event: {cache_key} (last seen: {current_time - last_seen:.1f}s ago)")
                return True
        
        # Not a duplicate, add to cache
        self.cache[cache_key] = current_time
        self.unique_events += 1
        self.logger.debug(f"New vision event: {cache_key}")
        return False
    
    def _cleanup_expired(self):
        """Remove expired entries from the cache."""
        current_time = time.time()
        expired_keys = []
        
        for cache_key, timestamp in self.cache.items():
            if current_time - timestamp >= self.ttl_seconds:
                expired_keys.append(cache_key)
        
        for key in expired_keys:
            del self.cache[key]
        
        if expired_keys:
            self.logger.debug(f"Cleaned up {len(expired_keys)} expired vision cache entries")
    
    def get_stats(self) -> Dict[str, int]:
        """Get deduplication statistics."""
        return {
            "total_events": self.total_events,
            "duplicate_events": self.duplicate_events,
            "unique_events": self.unique_events,
            "cache_size": len(self.cache),
            "duplicate_rate": (self.duplicate_events / self.total_events * 100) if self.total_events > 0 else 0
        }
    
    def reset_stats(self):
        """Reset statistics counters."""
        self.total_events = 0
        self.duplicate_events = 0
        self.unique_events = 0
        self.logger.info("Vision deduplication statistics reset")
    
    def clear_cache(self):
        """Clear all cached entries."""
        self.cache.clear()
        self.logger.info("Vision deduplication cache cleared")

# Global instance
vision_deduplication = VisionDeduplicationSystem()
