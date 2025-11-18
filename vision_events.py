#!/usr/bin/env python3
"""
Consolidated Vision Event System
===============================

Provides a unified VisionEvent class for all vision-related modules.
Consolidates duplicate VisionEvent definitions from:
- vision_deduplication.py
- vision_transport.py
- vision_stabilization.py
"""

from dataclasses import dataclass
from typing import Optional, Tuple, List, Union
from datetime import datetime
import time


@dataclass
class VisionEvent:
    """
    Unified vision event data structure.
    Consolidates all vision event definitions into a single, comprehensive class.
    """
    # Core identification (required fields first)
    name: str  # Object name (from deduplication)
    label: str  # Object label (from transport)
    confidence: float
    timestamp: Union[str, float, datetime]  # Flexible timestamp support
    
    # Optional fields (with defaults)
    color: Optional[str] = None
    bbox: Optional[Union[List[float], Tuple[int, int, int, int]]] = None
    location: Optional[Tuple[int, int]] = None
    size: Optional[Tuple[int, int]] = None
    image_hash: Optional[str] = None
    source: str = "vision"
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Ensure we have both name and label
        if not self.name and self.label:
            self.name = self.label
        elif not self.label and self.name:
            self.label = self.name
        
        # Normalize timestamp to string if needed
        if isinstance(self.timestamp, datetime):
            self.timestamp = self.timestamp.isoformat()
        elif isinstance(self.timestamp, float):
            # Convert float timestamp to ISO string
            self.timestamp = datetime.fromtimestamp(self.timestamp).isoformat()
    
    def get_cache_key(self) -> str:
        """Get cache key for deduplication."""
        return f"{self.name}|{self.color or 'unknown'}"
    
    def get_bbox_as_list(self) -> List[float]:
        """Get bbox as list of floats."""
        if self.bbox is None:
            return []
        if isinstance(self.bbox, tuple):
            return [float(x) for x in self.bbox]
        return self.bbox
    
    def get_bbox_as_tuple(self) -> Optional[Tuple[int, int, int, int]]:
        """Get bbox as tuple of integers."""
        if self.bbox is None:
            return None
        if isinstance(self.bbox, list):
            return tuple(int(x) for x in self.bbox)
        return self.bbox
    
    def is_duplicate_of(self, other: 'VisionEvent', ttl_seconds: float = 30.0) -> bool:
        """Check if this event is a duplicate of another event."""
        if not isinstance(other, VisionEvent):
            return False
        
        # Same object and color
        if self.name == other.name and self.color == other.color:
            # Check timestamp difference
            try:
                if isinstance(self.timestamp, str) and isinstance(other.timestamp, str):
                    ts1 = datetime.fromisoformat(self.timestamp.replace('Z', '+00:00'))
                    ts2 = datetime.fromisoformat(other.timestamp.replace('Z', '+00:00'))
                    time_diff = abs((ts1 - ts2).total_seconds())
                    return time_diff < ttl_seconds
                elif isinstance(self.timestamp, (int, float)) and isinstance(other.timestamp, (int, float)):
                    return abs(self.timestamp - other.timestamp) < ttl_seconds
            except (ValueError, TypeError):
                pass
        
        return False


@dataclass
class VisionDetection:
    """
    Legacy VisionDetection class for backward compatibility.
    Maps to VisionEvent for consistency.
    """
    name: str
    color: str
    confidence: float
    timestamp: str
    location: Optional[Tuple[int, int]] = None
    size: Optional[Tuple[int, int]] = None
    
    def to_vision_event(self) -> VisionEvent:
        """Convert to VisionEvent."""
        return VisionEvent(
            name=self.name,
            label=self.name,
            confidence=self.confidence,
            color=self.color,
            timestamp=self.timestamp,
            location=self.location,
            size=self.size
        )


@dataclass
class VisionCacheEntry:
    """Cache entry for vision detections with TTL."""
    event: VisionEvent
    timestamp: float
    ttl: float = 30.0
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return (time.time() - self.timestamp) > self.ttl
