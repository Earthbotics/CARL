"""
Memory Store System

Manages memory events with image binding, timestamps, and recall capabilities.
Implements event commit contracts and memory retrieval API.
"""

import os
import json
import time
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, asdict
import shutil


@dataclass
class MemoryHit:
    """Represents a memory retrieval result."""
    event_id: str
    timestamp: str
    summary: str
    image_file: Optional[str]
    concepts: List[str]
    emotion: Dict[str, str]
    relevance_score: float


@dataclass
class EventContext:
    """Context for memory events."""
    event_type: str
    content: str
    concepts: List[str]
    emotion: Dict[str, str]
    metadata: Dict[str, Any]


class MemoryStore:
    """Manages memory storage and retrieval."""
    
    def __init__(self, memory_dir: str = "memories"):
        self.memory_dir = memory_dir
        self.events_file = os.path.join(memory_dir, "events.json")
        self.memshots_dir = os.path.join(memory_dir, "memshots")
        self._logger = None
        
        # Ensure directories exist
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(self.memshots_dir, exist_ok=True)
        
        # Load existing events
        self.events = self._load_events()
    
    def set_logger(self, logger):
        """Set the logger for this store."""
        self._logger = logger
    
    def commit_event(self, event_ctx: Dict[str, Any], image_path: Optional[str] = None) -> str:
        """
        Commit an event to memory with optional image.
        
        Args:
            event_ctx: Event context dictionary
            image_path: Optional path to image file
            
        Returns:
            Event ID
        """
        # Generate event ID
        event_id = f"evt_{datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%fZ')}"
        timestamp = datetime.now().isoformat()
        
        # Handle image file
        final_image_path = None
        if image_path and os.path.exists(image_path):
            # Copy image to memshots directory
            image_ext = os.path.splitext(image_path)[1]
            final_image_path = f"memshots/{event_id}{image_ext}"
            dest_path = os.path.join(self.memory_dir, final_image_path)
            
            try:
                shutil.copy2(image_path, dest_path)
                if self._logger:
                    self._logger(f"[MEMORY] saved image: {final_image_path}")
            except Exception as e:
                if self._logger:
                    self._logger(f"[MEMORY] image save error: {e}")
                final_image_path = None
        
        # Create event record
        event_record = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_ctx.get("event_type", "unknown"),
            "content": event_ctx.get("content", ""),
            "concepts": event_ctx.get("concepts", []),
            "emotion": event_ctx.get("emotion", {"primary": "neutral", "sub": "neutral"}),
            "image_file": final_image_path,
            "metadata": event_ctx.get("metadata", {})
        }
        
        # Add to events list
        self.events.append(event_record)
        
        # Save to file
        self._save_events()
        
        if self._logger:
            self._logger(f"[MEMORY] committed event {event_id} concepts={event_ctx.get('concepts', [])}")
        
        return event_id
    
    def recall_memory(self, query: str) -> List[MemoryHit]:
        """
        Recall memories based on query.
        
        Args:
            query: Search query (entity/place/time)
            
        Returns:
            List of MemoryHit objects
        """
        query_lower = query.lower()
        hits = []
        
        for event in self.events:
            relevance_score = self._calculate_relevance(query_lower, event)
            
            if relevance_score > 0.1:  # Minimum relevance threshold
                hit = MemoryHit(
                    event_id=event["event_id"],
                    timestamp=event["timestamp"],
                    summary=self._generate_summary(event),
                    image_file=event.get("image_file"),
                    concepts=event.get("concepts", []),
                    emotion=event.get("emotion", {}),
                    relevance_score=relevance_score
                )
                hits.append(hit)
        
        # Sort by relevance score (descending)
        hits.sort(key=lambda x: x.relevance_score, reverse=True)
        
        if self._logger:
            self._logger(f"[MEMORY] recall '{query}' → {len(hits)} hits")
        
        return hits
    
    def get_event_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """Get event by ID."""
        for event in self.events:
            if event["event_id"] == event_id:
                return event
        return None
    
    def get_events_by_concept(self, concept: str) -> List[Dict[str, Any]]:
        """Get all events containing a specific concept."""
        concept_lower = concept.lower()
        matching_events = []
        
        for event in self.events:
            event_concepts = [c.lower() for c in event.get("concepts", [])]
            if concept_lower in event_concepts:
                matching_events.append(event)
        
        return matching_events
    
    def get_recent_events(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get events from the last N hours."""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        recent_events = []
        
        for event in self.events:
            try:
                event_time = datetime.fromisoformat(event["timestamp"]).timestamp()
                if event_time >= cutoff_time:
                    recent_events.append(event)
            except (ValueError, KeyError):
                continue
        
        return recent_events
    
    def _calculate_relevance(self, query: str, event: Dict[str, Any]) -> float:
        """Calculate relevance score for a query against an event."""
        score = 0.0
        
        # Check concepts
        event_concepts = [c.lower() for c in event.get("concepts", [])]
        for concept in event_concepts:
            if query in concept or concept in query:
                score += 0.4
        
        # Check content
        content_lower = event.get("content", "").lower()
        if query in content_lower:
            score += 0.3
        
        # Check time-based queries
        if "today" in query or "first" in query:
            # Boost recent events
            try:
                event_time = datetime.fromisoformat(event["timestamp"])
                hours_ago = (datetime.now() - event_time).total_seconds() / 3600
                if hours_ago < 24:
                    score += 0.2
                if "first" in query and hours_ago < 1:
                    score += 0.3
            except (ValueError, KeyError):
                pass
        
        # Check entity queries
        if any(word in query for word in ["see", "saw", "detect", "vision"]):
            if event.get("event_type") == "vision":
                score += 0.3
        
        return min(score, 1.0)
    
    def _generate_summary(self, event: Dict[str, Any]) -> str:
        """Generate a short summary of an event."""
        event_type = event.get("event_type", "unknown")
        content = event.get("content", "")
        concepts = event.get("concepts", [])
        
        if event_type == "vision":
            if concepts:
                return f"Saw {', '.join(concepts[:3])}"
            else:
                return f"Vision event: {content[:50]}"
        elif event_type == "speech":
            return f"Conversation: {content[:50]}"
        elif event_type == "action":
            return f"Action: {content[:50]}"
        else:
            return f"{event_type.title()}: {content[:50]}"
    
    def _load_events(self) -> List[Dict[str, Any]]:
        """Load events from file."""
        try:
            if os.path.exists(self.events_file):
                with open(self.events_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            if self._logger:
                self._logger(f"[MEMORY] load error: {e}")
        
        return []
    
    def _save_events(self) -> None:
        """Save events to file."""
        try:
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
        except Exception as e:
            if self._logger:
                self._logger(f"[MEMORY] save error: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        total_events = len(self.events)
        events_with_images = sum(1 for e in self.events if e.get("image_file"))
        
        # Count by event type
        event_types = {}
        for event in self.events:
            event_type = event.get("event_type", "unknown")
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return {
            "total_events": total_events,
            "events_with_images": events_with_images,
            "event_types": event_types,
            "memory_file_size": os.path.getsize(self.events_file) if os.path.exists(self.events_file) else 0
        }


# Global instance
memory_store = MemoryStore()


def commit_event(event_ctx: Dict[str, Any], image_path: Optional[str] = None) -> str:
    """Convenience function to commit an event."""
    return memory_store.commit_event(event_ctx, image_path)


def recall_memory(query: str) -> List[MemoryHit]:
    """Convenience function to recall memories."""
    return memory_store.recall_memory(query)


def get_event_by_id(event_id: str) -> Optional[Dict[str, Any]]:
    """Convenience function to get event by ID."""
    return memory_store.get_event_by_id(event_id)


def get_events_by_concept(concept: str) -> List[Dict[str, Any]]:
    """Convenience function to get events by concept."""
    return memory_store.get_events_by_concept(concept)


def get_recent_events(hours: int = 24) -> List[Dict[str, Any]]:
    """Convenience function to get recent events."""
    return memory_store.get_recent_events(hours)
