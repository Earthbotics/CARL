#!/usr/bin/env python3
"""
Test script to verify CARL's object recognition system is working correctly.
This test specifically focuses on the Chomp & Count Dino recognition issue.
"""

import sys
import os
import json
from pathlib import Path

# Add the parent directory to the path so we can import CARL modules
sys.path.append(str(Path(__file__).parent.parent))

from memory_retrieval_system import MemoryRetrievalSystem

def test_chomp_recognition():
    """Test that CARL can properly recognize Chomp & Count Dino."""
    print("Testing CARL's object recognition system...")
    
    # Initialize the memory retrieval system
    memory_system = MemoryRetrievalSystem(personality_type="INTP")
    
    # Test queries that should trigger Chomp recognition
    test_queries = [
        "Do you remember this object?",
        "What is this object?",
        "Do you know what this is?",
        "Have you seen this before?",
        "chomp",
        "dinosaur",
        "toy dinosaur",
        "green dinosaur"
    ]
    
    print("\nTesting various queries for Chomp & Count Dino recognition:")
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        
        try:
            # Test the memory retrieval system
            result = memory_system.retrieve_memory(
                query=query,
                context="",
                cognitive_ticks=0
            )
            
            if result and result.get('success'):
                print(f"Success: {result.get('reasoning', 'No reasoning provided')}")
                if result.get('response'):
                    print(f"Response: {result['response']}")
                if result.get('memory'):
                    memory_data = result['memory']
                    print(f"Memory data: {memory_data.get('object_name', 'Unknown')} (confidence: {memory_data.get('confidence', 0.0):.2f})")
            else:
                print(f"Failed: {result.get('reasoning', 'No reasoning provided') if result else 'No result returned'}")
                
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nTesting specific Chomp & Count Dino recognition:")
    
    # Test the specific object recognition query
    try:
        result = memory_system.retrieve_memory(
            query="Do you remember this object?",
            context="",
            cognitive_ticks=0
        )
        
        if result and result.get('success'):
            print("Object recognition query successful!")
            print(f"Result: {json.dumps(result, indent=2)}")
        else:
            print("Object recognition query failed!")
            print(f"Result: {json.dumps(result, indent=2) if result else 'No result'}")
            
    except Exception as e:
        print(f"Error in object recognition test: {e}")

def test_concept_files():
    """Test that the concept files exist and contain the expected data."""
    print("\nTesting concept files...")
    
    # Check if Chomp & Count Dino concept file exists
    chomp_file = "concepts/chomp_and_count_dino_self_learned.json"
    if os.path.exists(chomp_file):
        print(f"Found concept file: {chomp_file}")
        
        try:
            with open(chomp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Concept data:")
            print(f"   - Name: {data.get('word', 'Unknown')}")
            print(f"   - Keywords: {data.get('keywords', [])}")
            print(f"   - Description: {data.get('description', 'No description')}")
            print(f"   - Related concepts: {data.get('related_concepts', [])}")
            
        except Exception as e:
            print(f"Error reading concept file: {e}")
    else:
        print(f"Concept file not found: {chomp_file}")
    
    # Check if chomp.json exists
    chomp_json = "concepts/chomp.json"
    if os.path.exists(chomp_json):
        print(f"Found chomp.json: {chomp_json}")
        
        try:
            with open(chomp_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"Chomp data:")
            print(f"   - Name: {data.get('word', 'Unknown')}")
            print(f"   - Keywords: {data.get('keywords', [])}")
            print(f"   - Description: {data.get('description', 'No description')}")
            
        except Exception as e:
            print(f"Error reading chomp.json: {e}")
    else:
        print(f"chomp.json not found: {chomp_json}")

if __name__ == "__main__":
    print("Starting CARL Object Recognition Test")
    print("=" * 50)
    
    # Test concept files first
    test_concept_files()
    
    # Test the recognition system
    test_chomp_recognition()
    
    print("\n" + "=" * 50)
    print("Test completed!")
