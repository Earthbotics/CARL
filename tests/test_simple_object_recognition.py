#!/usr/bin/env python3
"""
Simple test to debug the object recognition system.
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path so we can import CARL modules
sys.path.append(str(Path(__file__).parent.parent))

from memory_retrieval_system import MemoryRetrievalSystem

def test_simple_recognition():
    """Test simple object recognition."""
    print("Testing simple object recognition...")
    
    # Initialize the memory retrieval system
    memory_system = MemoryRetrievalSystem(personality_type="INTP")
    
    # Test with a proper object recognition query
    query = "Do you remember this object?"
    print(f"Testing query: '{query}'")
    
    try:
        result = memory_system.retrieve_memory(
            query=query,
            context="",
            cognitive_ticks=0
        )
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_recognition()
