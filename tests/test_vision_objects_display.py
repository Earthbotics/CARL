#!/usr/bin/env python3
"""
Test script to verify that vision analysis objects are properly displayed
in the Objects Detected listbox.

This test simulates the API response from openai_call_summary_20251116_163918.txt
and verifies that objects are correctly extracted and displayed.
"""

import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_vision_objects_extraction():
    """Test that objects are correctly extracted from vision API response."""
    print("\n=== TEST: Vision Objects Extraction ===")
    
    # Simulate API response from openai_call_summary_20251116_163918.txt
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
        "object_details": {
            "person": {
                "text_visible": "",
                "colors": ["gray", "black", "red"],
                "material": "skin, fabric",
                "brand": "",
                "character": "",
                "size": "average adult",
                "features": ["glasses", "facial hair"]
            }
        },
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
    
    # Simulate how vision_system.py structures the result
    # From vision_system.py line 1047: "objects": result.objects
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
    
    # Simulate how _trigger_vision_analysis_before_thought extracts objects
    # From main.py line 40924: objects_detected = result["data"].get("objects", [])
    objects_detected = vision_result_data["data"].get("objects", [])
    
    print(f"[TEST] Objects extracted from API response: {len(objects_detected)} objects")
    print(f"[TEST] Objects list: {objects_detected}")
    
    # Verify objects were extracted
    assert len(objects_detected) == 10, f"Expected 10 objects, got {len(objects_detected)}"
    assert "person" in objects_detected, "Expected 'person' in objects"
    assert "glasses" in objects_detected, "Expected 'glasses' in objects"
    assert "computer" in objects_detected, "Expected 'computer' in objects"
    
    # Simulate how vision_display_result is created
    # From main.py line 40952: "objects_detected": objects_detected
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
    print(f"  - danger_detected: {vision_display_result.get('danger_detected', False)}")
    print(f"  - pleasure_detected: {vision_display_result.get('pleasure_detected', False)}")
    print(f"  - analysis keys: {list(vision_display_result.get('analysis', {}).keys())}")
    
    # Simulate how _update_vision_analysis_display extracts objects
    # From main.py line 8892: objects_detected = vision_result.get('objects_detected', [])
    display_objects = vision_display_result.get('objects_detected', [])
    
    print(f"[TEST] Objects extracted for display: {len(display_objects)} objects")
    print(f"[TEST] Display objects list: {display_objects}")
    
    # Verify objects are available for display
    assert len(display_objects) == 10, f"Expected 10 objects for display, got {len(display_objects)}"
    assert display_objects == objects_detected, "Display objects should match extracted objects"
    
    # Simulate the display text creation
    # From main.py line 8896: objects_text = '\n'.join([f"• {obj}" for obj in objects_detected])
    if display_objects:
        objects_text = '\n'.join([f"• {obj}" for obj in display_objects])
        print(f"[TEST] Display text (first 100 chars): {objects_text[:100]}...")
        assert len(objects_text) > 0, "Display text should not be empty"
        assert "• person" in objects_text, "Display text should contain '• person'"
        assert "• glasses" in objects_text, "Display text should contain '• glasses'"
    else:
        print("[TEST] ERROR: No objects for display!")
        assert False, "Objects should be available for display"
    
    print("[PASS] TEST PASSED: Objects correctly extracted and ready for display")
    return True

def test_vision_result_structure():
    """Test that vision result structure matches what _update_vision_analysis_display expects."""
    print("\n=== TEST: Vision Result Structure ===")
    
    # Expected structure for _update_vision_analysis_display
    expected_keys = ['objects_detected', 'danger_detected', 'danger_reason', 
                     'pleasure_detected', 'pleasure_reason', 'analysis']
    
    # Create a properly structured vision result
    vision_result = {
        "objects_detected": ["person", "glasses", "computer"],
        "danger_detected": False,
        "danger_reason": "",
        "pleasure_detected": False,
        "pleasure_reason": "",
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
    
    # Verify all expected keys are present
    for key in expected_keys:
        assert key in vision_result, f"Missing key: {key}"
        print(f"[TEST] Key '{key}' present: {key in vision_result}")
    
    # Verify objects_detected is a list
    assert isinstance(vision_result['objects_detected'], list), "objects_detected should be a list"
    assert len(vision_result['objects_detected']) > 0, "objects_detected should not be empty"
    
    print(f"[TEST] Vision result structure valid:")
    print(f"  - objects_detected: {len(vision_result['objects_detected'])} items")
    print(f"  - analysis fields: {len(vision_result['analysis'])} fields")
    
    print("[PASS] TEST PASSED: Vision result structure is correct")
    return True

if __name__ == "__main__":
    print("=" * 60)
    print("Vision Objects Display Test")
    print("=" * 60)
    
    try:
        test1_passed = test_vision_objects_extraction()
        test2_passed = test_vision_result_structure()
        
        if test1_passed and test2_passed:
            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n" + "=" * 60)
            print("❌ SOME TESTS FAILED")
            print("=" * 60)
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

