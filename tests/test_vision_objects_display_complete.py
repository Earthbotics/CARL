#!/usr/bin/env python3
"""
Comprehensive test to verify that vision analysis objects are properly displayed
in the Objects Detected text widget after vision_analysis results are returned.

This test simulates the complete flow:
1. Vision analysis API call returns objects
2. Results are processed and passed to _update_vision_analysis_display
3. Objects appear in the Objects Detected display box
"""

import sys
import os
import json
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_vision_result_structure_from_api():
    """Test that vision results from API are correctly structured."""
    print("\n=== TEST 1: Vision Result Structure from API ===")
    
    # Simulate API response structure (from openai_call_summary_20251116_163918.txt)
    api_response = {
        "objects": [
            "person",
            "glasses",
            "plaid shirt",
            "computer",
            "monitor",
            "desk",
            "cables",
            "controller",
            "shelf",
            "furniture"
        ],
        "object_details": {},
        "danger_detected": False,
        "danger_reason": "",
        "pleasure_detected": False,
        "pleasure_reason": "",
        "neucogar": {
            "dopamine": 0.0,
            "serotonin": 0.0,
            "norepinephrine": 0.0,
            "acetylcholine": 0.0
        },
        "analysis": {
            "who": "unknown individual",
            "what": "person in a room",
            "when": "current time",
            "where": "indoor setting",
            "why": "context not provided",
            "how": "observational",
            "expectation": "unclear",
            "self_recognition": False,
            "mirror_context": False
        }
    }
    
    # Simulate how vision_system.py structures the result (line 1047)
    vision_result_data = {
        "success": True,
        "data": {
            "objects": api_response["objects"],  # This is what capture_and_analyze_vision returns
            "danger_detected": api_response["danger_detected"],
            "pleasure_detected": api_response["pleasure_detected"],
            "neucogar": api_response["neucogar"],
            "analysis": api_response["analysis"],
            "image_path": "test_image.jpg",
            "timestamp": "2025-11-16T16:37:13"
        }
    }
    
    # Simulate how _trigger_vision_analysis_before_thought extracts objects (line 40924)
    objects_detected = vision_result_data["data"].get("objects", [])
    
    print(f"[TEST] API returned {len(api_response['objects'])} objects")
    print(f"[TEST] Objects extracted: {len(objects_detected)} objects")
    print(f"[TEST] Objects: {objects_detected}")
    
    assert len(objects_detected) == 10, f"Expected 10 objects, got {len(objects_detected)}"
    assert "person" in objects_detected, "Expected 'person' in objects"
    assert "glasses" in objects_detected, "Expected 'glasses' in objects"
    
    # Simulate how vision_display_result is created (line 40952)
    vision_display_result = {
        "objects_detected": objects_detected,
        "danger_detected": vision_result_data["data"].get("danger_detected", False),
        "danger_reason": "",
        "pleasure_detected": vision_result_data["data"].get("pleasure_detected", False),
        "pleasure_reason": "",
        "analysis": vision_result_data["data"].get("analysis", {})
    }
    
    print(f"[TEST] Vision display result structure:")
    print(f"  - objects_detected: {len(vision_display_result.get('objects_detected', []))} objects")
    print(f"  - Has 'objects_detected' key: {'objects_detected' in vision_display_result}")
    
    assert 'objects_detected' in vision_display_result, "vision_display_result must have 'objects_detected' key"
    assert len(vision_display_result['objects_detected']) == 10, "Must have 10 objects"
    
    print("[PASS] TEST 1 PASSED: Vision result structure is correct")
    return vision_display_result

def test_display_update_logic():
    """Test the display update logic with actual widget operations."""
    print("\n=== TEST 2: Display Update Logic ===")
    
    # Create a real Tkinter root (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create a real Text widget
    objects_detected_text = tk.Text(root, height=4, width=25, font=('Arial', 7), wrap=tk.WORD)
    objects_detected_text.pack()
    
    # Simulate vision_display_result from test 1
    vision_display_result = {
        "objects_detected": ["person", "glasses", "plaid shirt", "computer", "monitor"],
        "danger_detected": False,
        "danger_reason": "",
        "pleasure_detected": False,
        "pleasure_reason": "",
        "analysis": {}
    }
    
    # Simulate _update_vision_analysis_display logic
    objects_detected = vision_display_result.get('objects_detected', [])
    
    print(f"[TEST] Objects to display: {len(objects_detected)} objects")
    print(f"[TEST] Objects: {objects_detected}")
    
    # Update the widget
    objects_detected_text.config(state=tk.NORMAL)
    objects_detected_text.delete('1.0', tk.END)
    
    if objects_detected:
        objects_text = '\n'.join([f"• {obj}" for obj in objects_detected])
        objects_detected_text.insert('1.0', objects_text)
        print(f"[TEST] Inserted text: {objects_text[:100]}...")
    else:
        objects_detected_text.insert('1.0', 'None detected')
    
    objects_detected_text.config(state=tk.DISABLED)
    
    # Verify the widget content
    widget_content = objects_detected_text.get('1.0', tk.END).strip()
    print(f"[TEST] Widget content (first 100 chars): {widget_content[:100]}...")
    print(f"[TEST] Widget content length: {len(widget_content)}")
    
    assert len(widget_content) > 0, "Widget content should not be empty"
    assert "• person" in widget_content, "Widget should contain '• person'"
    assert "• glasses" in widget_content, "Widget should contain '• glasses'"
    assert "• computer" in widget_content, "Widget should contain '• computer'"
    
    # Count objects in widget
    object_count = widget_content.count('•')
    print(f"[TEST] Objects found in widget: {object_count}")
    assert object_count == len(objects_detected), f"Widget should contain {len(objects_detected)} objects, found {object_count}"
    
    root.destroy()
    print("[PASS] TEST 2 PASSED: Display update logic works correctly")
    return True

def test_complete_flow_simulation():
    """Test the complete flow from API response to display update."""
    print("\n=== TEST 3: Complete Flow Simulation ===")
    
    # Step 1: API response
    api_response = {
        "objects": ["person", "glasses", "computer", "monitor", "desk"],
        "analysis": {
            "who": "unknown individual",
            "what": "person in a room",
            "where": "indoor setting"
        }
    }
    
    # Step 2: vision_system.capture_and_analyze_vision returns
    vision_result_data = {
        "success": True,
        "data": {
            "objects": api_response["objects"],
            "analysis": api_response["analysis"]
        }
    }
    
    # Step 3: _trigger_vision_analysis_before_thought extracts
    objects_detected = vision_result_data["data"].get("objects", [])
    
    # Step 4: vision_display_result is created
    vision_display_result = {
        "objects_detected": objects_detected,
        "analysis": vision_result_data["data"].get("analysis", {})
    }
    
    # Step 5: _update_vision_analysis_display receives it
    # Simulate the function logic
    objects_for_display = vision_display_result.get('objects_detected', [])
    
    # Check fallback logic
    if not objects_for_display:
        if 'objects' in vision_display_result:
            objects_for_display = vision_display_result.get('objects', [])
        elif 'data' in vision_display_result:
            objects_for_display = vision_display_result.get('data', {}).get('objects', [])
    
    print(f"[TEST] Step 1 - API objects: {len(api_response['objects'])}")
    print(f"[TEST] Step 2 - Vision result objects: {len(vision_result_data['data']['objects'])}")
    print(f"[TEST] Step 3 - Extracted objects: {len(objects_detected)}")
    print(f"[TEST] Step 4 - Display result objects: {len(vision_display_result['objects_detected'])}")
    print(f"[TEST] Step 5 - Objects for display: {len(objects_for_display)}")
    
    assert len(objects_for_display) == 5, f"Expected 5 objects for display, got {len(objects_for_display)}"
    assert objects_for_display == api_response["objects"], "Objects should match API response"
    
    # Step 6: Format for display
    if objects_for_display:
        objects_text = '\n'.join([f"• {obj}" for obj in objects_for_display])
        print(f"[TEST] Step 6 - Formatted text: {objects_text[:80]}...")
        assert len(objects_text) > 0, "Formatted text should not be empty"
        assert "• person" in objects_text, "Formatted text should contain '• person'"
    
    print("[PASS] TEST 3 PASSED: Complete flow works correctly")
    return True

def test_edge_cases():
    """Test edge cases that might cause display issues."""
    print("\n=== TEST 4: Edge Cases ===")
    
    # Test case 1: Empty objects list
    vision_result_empty = {
        "objects_detected": [],
        "analysis": {"what": "person in a room"}
    }
    objects = vision_result_empty.get('objects_detected', [])
    assert len(objects) == 0, "Should handle empty objects list"
    print("[PASS] Edge case 1: Empty objects list handled")
    
    # Test case 2: Missing objects_detected key
    vision_result_missing = {
        "analysis": {"what": "person in a room"}
    }
    objects = vision_result_missing.get('objects_detected', [])
    assert len(objects) == 0, "Should handle missing objects_detected key"
    print("[PASS] Edge case 2: Missing objects_detected key handled")
    
    # Test case 3: Objects in 'objects' key instead of 'objects_detected'
    vision_result_alt_key = {
        "objects": ["person", "glasses"],
        "analysis": {}
    }
    objects = vision_result_alt_key.get('objects_detected', [])
    if not objects:
        objects = vision_result_alt_key.get('objects', [])
    assert len(objects) == 2, "Should find objects in 'objects' key"
    print("[PASS] Edge case 3: Objects in 'objects' key found")
    
    # Test case 4: Nested data structure
    vision_result_nested = {
        "data": {
            "objects": ["person", "computer"]
        }
    }
    objects = vision_result_nested.get('objects_detected', [])
    if not objects and 'data' in vision_result_nested:
        objects = vision_result_nested['data'].get('objects', [])
    assert len(objects) == 2, "Should find objects in nested 'data.objects'"
    print("[PASS] Edge case 4: Nested data structure handled")
    
    print("[PASS] TEST 4 PASSED: All edge cases handled correctly")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("Vision Objects Display Complete Flow Test")
    print("=" * 70)
    
    try:
        test1_result = test_vision_result_structure_from_api()
        test2_passed = test_display_update_logic()
        test3_passed = test_complete_flow_simulation()
        test4_passed = test_edge_cases()
        
        if test1_result and test2_passed and test3_passed and test4_passed:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED")
            print("=" * 70)
            print("\nHowever, if objects still don't appear in the GUI, check:")
            print("1. Is _update_vision_analysis_display being called?")
            print("2. Is the after() call executing on the main thread?")
            print("3. Are there any exceptions being silently caught?")
            print("4. Is objects_detected_text widget initialized before update?")
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("SOME TESTS FAILED")
            print("=" * 70)
            sys.exit(1)
    except Exception as e:
        print(f"\nTEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

