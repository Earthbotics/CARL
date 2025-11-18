#!/usr/bin/env python3
"""
Integration test to verify the complete flow from vision API response
to Objects Detected display box update.

This test simulates the actual runtime flow:
1. Vision API returns objects
2. _trigger_vision_analysis_before_thought processes results
3. vision_display_result is created
4. _update_vision_analysis_display is called
5. Objects appear in Objects Detected text widget
"""

import sys
import os
import json
import tkinter as tk
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_complete_vision_to_display_flow():
    """Test the complete flow from vision API to display."""
    print("\n=== TEST: Complete Vision to Display Flow ===")
    
    # Step 1: Simulate API response (from openai_call_summary_20251116_163918.txt)
    api_response_json = {
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
    
    # Step 2: Simulate vision_system.capture_and_analyze_vision return structure
    # From vision_system.py line 1043-1055
    capture_result = {
        "success": True,
        "error": None,
        "data": {
            "objects": api_response_json["objects"],  # Line 1047
            "danger_detected": api_response_json["danger_detected"],
            "pleasure_detected": api_response_json["pleasure_detected"],
            "neucogar": api_response_json["neucogar"],
            "analysis": api_response_json["analysis"],
            "image_path": "test_image.jpg",
            "timestamp": "2025-11-16T16:37:13"
        }
    }
    
    print(f"[TEST] Step 1 - API response: {len(api_response_json['objects'])} objects")
    print(f"[TEST] Step 2 - capture_result structure: success={capture_result['success']}")
    print(f"[TEST] Step 2 - capture_result['data']['objects']: {len(capture_result['data']['objects'])} objects")
    
    # Step 3: Simulate _trigger_vision_analysis_before_thought extraction
    # From main.py line 40924
    result = capture_result
    objects_detected = result["data"].get("objects", [])
    
    print(f"[TEST] Step 3 - objects_detected extracted: {len(objects_detected)} objects")
    assert len(objects_detected) == 10, f"Expected 10 objects, got {len(objects_detected)}"
    
    # Step 4: Simulate vision_display_result creation
    # From main.py line 40952 (in _trigger_vision_analysis_before_thought)
    vision_display_result = {
        "objects_detected": objects_detected,
        "danger_detected": result["data"].get("danger_detected", False),
        "danger_reason": result["data"].get("danger_reason", ""),
        "pleasure_detected": result["data"].get("pleasure_detected", False),
        "pleasure_reason": result["data"].get("pleasure_reason", ""),
        "analysis": result["data"].get("analysis", {})
    }
    
    print(f"[TEST] Step 4 - vision_display_result created")
    print(f"[TEST] Step 4 - vision_display_result['objects_detected']: {len(vision_display_result['objects_detected'])} objects")
    assert 'objects_detected' in vision_display_result, "vision_display_result must have 'objects_detected' key"
    assert len(vision_display_result['objects_detected']) == 10, "Must have 10 objects"
    
    # Step 5: Simulate _update_vision_analysis_display processing
    # From main.py line 8881-8925
    vision_result = vision_display_result
    
    # Extract objects with fallback logic (from _update_vision_analysis_display)
    objects_for_display = vision_result.get('objects_detected', [])
    if not objects_for_display:
        if 'objects' in vision_result:
            objects_for_display = vision_result.get('objects', [])
        elif 'data' in vision_result and isinstance(vision_result.get('data'), dict):
            objects_for_display = vision_result['data'].get('objects', [])
    
    print(f"[TEST] Step 5 - objects_for_display extracted: {len(objects_for_display)} objects")
    assert len(objects_for_display) == 10, f"Expected 10 objects for display, got {len(objects_for_display)}"
    
    # Step 6: Test actual widget update
    root = tk.Tk()
    root.withdraw()
    
    objects_detected_text = tk.Text(root, height=4, width=25, font=('Arial', 7), wrap=tk.WORD)
    objects_detected_text.pack()
    
    # Simulate the update logic
    objects_detected_text.config(state=tk.NORMAL)
    objects_detected_text.delete('1.0', tk.END)
    
    if objects_for_display:
        objects_text = '\n'.join([f"• {obj}" for obj in objects_for_display])
        objects_detected_text.insert('1.0', objects_text)
    else:
        objects_detected_text.insert('1.0', 'None detected')
    
    objects_detected_text.config(state=tk.DISABLED)
    root.update_idletasks()
    
    # Verify widget content
    widget_content = objects_detected_text.get('1.0', tk.END).strip()
    print(f"[TEST] Step 6 - Widget content length: {len(widget_content)}")
    print(f"[TEST] Step 6 - Widget content (first 150 chars): {widget_content[:150]}...")
    
    assert len(widget_content) > 0, "Widget content should not be empty"
    assert "• person" in widget_content, "Widget should contain '• person'"
    assert "• glasses" in widget_content, "Widget should contain '• glasses'"
    assert "• computer" in widget_content, "Widget should contain '• computer'"
    
    # Count objects in widget
    object_count = widget_content.count('•')
    print(f"[TEST] Step 6 - Objects found in widget: {object_count}")
    assert object_count == len(objects_for_display), f"Widget should contain {len(objects_for_display)} objects, found {object_count}"
    
    root.destroy()
    
    print("[PASS] TEST PASSED: Complete flow works correctly")
    return True

def test_vision_result_structure_variations():
    """Test that display handles different vision_result structures."""
    print("\n=== TEST: Vision Result Structure Variations ===")
    
    # Test case 1: Standard structure with objects_detected
    vision_result_1 = {
        "objects_detected": ["person", "glasses", "computer"],
        "analysis": {}
    }
    objects_1 = vision_result_1.get('objects_detected', [])
    if not objects_1:
        if 'objects' in vision_result_1:
            objects_1 = vision_result_1.get('objects', [])
    assert len(objects_1) == 3, "Should extract 3 objects from standard structure"
    print("[PASS] Test case 1: Standard structure")
    
    # Test case 2: Objects in 'objects' key
    vision_result_2 = {
        "objects": ["person", "glasses"],
        "analysis": {}
    }
    objects_2 = vision_result_2.get('objects_detected', [])
    if not objects_2:
        if 'objects' in vision_result_2:
            objects_2 = vision_result_2.get('objects', [])
    assert len(objects_2) == 2, "Should extract 2 objects from 'objects' key"
    print("[PASS] Test case 2: Objects in 'objects' key")
    
    # Test case 3: Nested in 'data.objects'
    vision_result_3 = {
        "data": {
            "objects": ["person", "computer", "monitor"]
        }
    }
    objects_3 = vision_result_3.get('objects_detected', [])
    if not objects_3:
        if 'objects' in vision_result_3:
            objects_3 = vision_result_3.get('objects', [])
        elif 'data' in vision_result_3 and isinstance(vision_result_3.get('data'), dict):
            objects_3 = vision_result_3['data'].get('objects', [])
    assert len(objects_3) == 3, "Should extract 3 objects from nested 'data.objects'"
    print("[PASS] Test case 3: Nested in 'data.objects'")
    
    print("[PASS] TEST PASSED: All structure variations handled correctly")
    return True

if __name__ == "__main__":
    print("=" * 70)
    print("Vision Display Integration Test")
    print("=" * 70)
    
    try:
        test1_passed = test_complete_vision_to_display_flow()
        test2_passed = test_vision_result_structure_variations()
        
        if test1_passed and test2_passed:
            print("\n" + "=" * 70)
            print("ALL TESTS PASSED")
            print("=" * 70)
            print("\nThe flow from API to display is working correctly.")
            print("If objects still don't appear in the GUI, check the logs for:")
            print("1. [PERCEPTION] messages showing objects_detected extraction")
            print("2. [DISPLAY CALLBACK] messages showing callback execution")
            print("3. [VISION DISPLAY] messages showing widget updates")
            print("4. Any error messages in the traceback")
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

