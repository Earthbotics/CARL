#!/usr/bin/env python3
"""
Working Memory System for CARL
This implements a human-like working memory system for remembering information.
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class WorkingMemory:
    """Working memory system that mimics human memory processes."""
    
    def __init__(self, memory_file: str = "working_memory.json"):
        self.memory_file = memory_file
        self.memories = self._load_memories()
        
        # Memory capacity limits (like human working memory)
        self.max_items = 7  # Miller's Law: 7±2 items
        self.max_age_hours = 24  # Working memory typically lasts hours, not days
        
    def _load_memories(self) -> Dict:
        """Load existing memories from file."""
        try:
            if os.path.exists(self.memory_file):
                with open(self.memory_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading working memory: {e}")
        
        return {
            "items": [],
            "last_updated": datetime.now().isoformat(),
            "total_items_created": 0
        }
    
    def _save_memories(self):
        """Save memories to file."""
        try:
            self.memories["last_updated"] = datetime.now().isoformat()
            with open(self.memory_file, 'w') as f:
                json.dump(self.memories, f, indent=2)
        except Exception as e:
            print(f"Error saving working memory: {e}")
    
    def _cleanup_old_memories(self):
        """Remove memories that are too old."""
        current_time = datetime.now()
        items = self.memories.get("items", [])
        
        # Filter out old memories
        valid_items = []
        for item in items:
            created_time = datetime.fromisoformat(item.get("created", "2025-01-01T00:00:00"))
            age_hours = (current_time - created_time).total_seconds() / 3600
            
            if age_hours < self.max_age_hours:
                valid_items.append(item)
        
        self.memories["items"] = valid_items
    
    def remember(self, content: str, context: str = "", importance: int = 5) -> bool:
        """
        Remember a piece of information.
        
        Args:
            content: The information to remember (e.g., "25", "blue car", etc.)
            context: Context about why this is being remembered
            importance: Importance level (1-10, higher = more important)
            
        Returns:
            bool: True if successfully remembered, False otherwise
        """
        try:
            self._cleanup_old_memories()
            
            # Check if we're at capacity
            items = self.memories.get("items", [])
            if len(items) >= self.max_items:
                # Remove least important item
                items.sort(key=lambda x: x.get("importance", 0))
                items.pop(0)
            
            # Create new memory item
            memory_item = {
                "id": self.memories.get("total_items_created", 0) + 1,
                "content": content,
                "context": context,
                "importance": min(max(importance, 1), 10),  # Clamp between 1-10
                "created": datetime.now().isoformat(),
                "last_accessed": datetime.now().isoformat(),
                "access_count": 0,
                "confidence": 1.0  # Starts high, decreases with time/forgetting
            }
            
            # Add to memory
            items.append(memory_item)
            self.memories["items"] = items
            self.memories["total_items_created"] = memory_item["id"]
            
            # Save to file
            self._save_memories()
            
            print(f"✅ Remembered: '{content}' (ID: {memory_item['id']})")
            return True
            
        except Exception as e:
            print(f"❌ Error remembering information: {e}")
            return False
    
    def recall(self, query: str = None, item_id: int = None) -> Optional[Dict]:
        """
        Recall information from working memory.
        
        Args:
            query: Search query to find matching content
            item_id: Specific memory ID to recall
            
        Returns:
            Dict: Memory item if found, None otherwise
        """
        try:
            self._cleanup_old_memories()
            
            items = self.memories.get("items", [])
            
            if item_id is not None:
                # Recall by ID
                for item in items:
                    if item.get("id") == item_id:
                        self._update_access(item)
                        return item
                return None
            
            if query:
                # Search by content or context
                query_lower = query.lower()
                best_match = None
                best_score = 0
                
                for item in items:
                    content = item.get("content", "").lower()
                    context = item.get("context", "").lower()
                    
                    # Calculate match score
                    score = 0
                    if query_lower in content:
                        score += 3  # Exact content match
                    elif query_lower in context:
                        score += 2  # Context match
                    elif any(word in content for word in query_lower.split()):
                        score += 1  # Partial match
                    
                    # Boost score by importance and recency
                    importance = item.get("importance", 5)
                    score += importance * 0.1
                    
                    if score > best_score:
                        best_score = score
                        best_match = item
                
                if best_match and best_score > 0:
                    self._update_access(best_match)
                    return best_match
            
            return None
            
        except Exception as e:
            print(f"❌ Error recalling information: {e}")
            return None
    
    def _update_access(self, item: Dict):
        """Update access statistics for a memory item."""
        item["last_accessed"] = datetime.now().isoformat()
        item["access_count"] = item.get("access_count", 0) + 1
        
        # Decrease confidence slightly with each access (simulating forgetting)
        current_confidence = item.get("confidence", 1.0)
        item["confidence"] = max(current_confidence - 0.05, 0.1)
        
        self._save_memories()
    
    def list_memories(self) -> List[Dict]:
        """List all current working memories."""
        try:
            self._cleanup_old_memories()
            items = self.memories.get("items", [])
            
            # Sort by importance and recency
            items.sort(key=lambda x: (x.get("importance", 0), x.get("created", "")), reverse=True)
            
            return items
            
        except Exception as e:
            print(f"❌ Error listing memories: {e}")
            return []
    
    def forget(self, item_id: int) -> bool:
        """
        Forget a specific memory item.
        
        Args:
            item_id: ID of the memory to forget
            
        Returns:
            bool: True if successfully forgotten, False otherwise
        """
        try:
            items = self.memories.get("items", [])
            
            for i, item in enumerate(items):
                if item.get("id") == item_id:
                    removed_item = items.pop(i)
                    self.memories["items"] = items
                    self._save_memories()
                    
                    print(f"🗑️  Forgotten: '{removed_item.get('content', '')}' (ID: {item_id})")
                    return True
            
            print(f"❌ Memory with ID {item_id} not found")
            return False
            
        except Exception as e:
            print(f"❌ Error forgetting memory: {e}")
            return False
    
    def get_memory_stats(self) -> Dict:
        """Get statistics about working memory."""
        try:
            self._cleanup_old_memories()
            items = self.memories.get("items", [])
            
            stats = {
                "total_items": len(items),
                "max_capacity": self.max_items,
                "utilization_percent": (len(items) / self.max_items) * 100,
                "total_created": self.memories.get("total_items_created", 0),
                "last_updated": self.memories.get("last_updated", "Unknown"),
                "average_importance": sum(item.get("importance", 5) for item in items) / max(len(items), 1),
                "average_confidence": sum(item.get("confidence", 1.0) for item in items) / max(len(items), 1)
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ Error getting memory stats: {e}")
            return {}
    
    def clear_all(self) -> bool:
        """Clear all working memories."""
        try:
            self.memories["items"] = []
            self._save_memories()
            print("🧹 All working memories cleared")
            return True
            
        except Exception as e:
            print(f"❌ Error clearing memories: {e}")
            return False

# Example usage
if __name__ == "__main__":
    # Create working memory instance
    wm = WorkingMemory()
    
    # Remember some information
    wm.remember("25", "Joe asked me to remember this number", 8)
    wm.remember("blue car", "Saw a blue car in the parking lot", 6)
    wm.remember("meeting at 3pm", "Important meeting reminder", 9)
    
    # Recall information
    result = wm.recall(query="25")
    if result:
        print(f"Recalled: {result['content']} - {result['context']}")
    
    # List all memories
    memories = wm.list_memories()
    print(f"\nCurrent memories ({len(memories)}):")
    for memory in memories:
        print(f"  ID {memory['id']}: '{memory['content']}' (Importance: {memory['importance']})")
    
    # Get stats
    stats = wm.get_memory_stats()
    print(f"\nMemory stats: {stats}") 