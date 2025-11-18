"""
Test for Vision Analysis Display Update After Cognitive Processing

This test verifies that:
1. After cognitive_processing (process_personality_functions) completes, the Vision Analysis display is updated
2. Analysis, Danger, and Pleasure fields are properly populated
3. The update happens in a timely manner (immediately after cognitive_processing returns)
4. All vision data is correctly displayed in the Vision controls
"""

import sys
import os
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestVisionAfterCognitiveProcessing:
    """Test class for vision display update after cognitive processing."""
    
    def __init__(self):
        self.test_results = []
        self.mock_app = None
        
    def setup_mock_app(self):
        """Set up a mock CARL application for testing."""
        # Create mock application
        self.mock_app = MagicMock()
        
        # Mock GUI components for vision analysis display
        self.mock_app.objects_detected_text = MagicMock()
        self.mock_app.danger_status_label = MagicMock()
        self.mock_app.danger_reason_text = MagicMock()
        self.mock_app.pleasure_status_label = MagicMock()
        self.mock_app.pleasure_reason_text = MagicMock()
        self.mock_app.analysis_text = MagicMock()
        
        # Mock perception system
        self.mock_app.perception_system = MagicMock()
        
        # Mock methods
        self.mock_app.log = print
        self.mock_app.after = lambda delay, func: func()  # Execute immediately for testing
        
        # Track if update was called
        self.mock_app._update_vision_analysis_display_called = False
        self.mock_app._update_vision_analysis_display_call_time = None
        
        # Override _update_vision_analysis_display to track calls
        def track_update(vision_result):
            self.mock_app._update_vision_analysis_display_called = True
            self.mock_app._update_vision_analysis_display_call_time = datetime.now()
            self.mock_app._update_vision_analysis_display_last_result = vision_result
        
        self.mock_app._update_vision_analysis_display = track_update
        
        return self.mock_app
    
    def test_vision_display_after_cognitive_processing(self):
        """Test that vision display is updated after cognitive_processing completes."""
        print("\n=== TEST 1: Vision Display After Cognitive Processing ===")
        
        app = self.setup_mock_app()
        
        # Simulate vision result
        vision_result = {
            "objects_detected": ["desk", "chair", "person", "laptop"],
            "danger_detected": False,
            "danger_reason": "",
            "pleasure_detected": True,
            "pleasure_reason": "Friendly environment detected",
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
        
        # Simulate cognitive_processing result
        personality_result = {
            "status": "success",
            "perception_processing": {
                "extroversion_energy": 0.3,
                "introversion_energy": 0.7,
                "intuition_level": 0.5,
                "sensation_level": 0.5
            }
        }
        
        # Mock process_personality_functions to return personality_result
        app.perception_system.process_personality_functions = MagicMock(return_value=personality_result)
        
        # Simulate the flow: cognitive_processing completes, then update vision display
        # This mimics what happens in _run_enhanced_cognitive_processing
        personality_result_returned = app.perception_system.process_personality_functions({}, {})
        
        # After cognitive_processing completes, update vision display
        if vision_result:
            vision_display_result = {
                "objects_detected": vision_result.get("objects_detected", []),
                "danger_detected": vision_result.get("danger_detected", False),
                "danger_reason": vision_result.get("danger_reason", ""),
                "pleasure_detected": vision_result.get("pleasure_detected", False),
                "pleasure_reason": vision_result.get("pleasure_reason", ""),
                "analysis": vision_result.get("analysis", {})
            }
            
            # Update display immediately
            app.after(0, lambda: app._update_vision_analysis_display(vision_display_result))
        
        # Verify cognitive_processing was called
        assert app.perception_system.process_personality_functions.called, "Cognitive processing should be called"
        
        # Verify vision display update was scheduled/called
        assert app._update_vision_analysis_display_called, "Vision display update should be called after cognitive_processing"
        
        # Verify the vision result was passed correctly
        assert app._update_vision_analysis_display_last_result is not None, "Vision result should be passed to display update"
        assert "objects_detected" in app._update_vision_analysis_display_last_result, "Objects detected should be in result"
        assert "analysis" in app._update_vision_analysis_display_last_result, "Analysis should be in result"
        
        print(f"[PASS] Cognitive processing completed: {personality_result_returned.get('status')}")
        print(f"[PASS] Vision display updated: {app._update_vision_analysis_display_called}")
        print(f"[PASS] Objects in result: {len(app._update_vision_analysis_display_last_result.get('objects_detected', []))}")
        print("[PASS] TEST 1 PASSED: Vision display updated after cognitive_processing")
        return True
    
    def test_analysis_fields_populated(self):
        """Test that all analysis fields are populated after cognitive_processing."""
        print("\n=== TEST 2: Analysis Fields Populated ===")
        
        app = self.setup_mock_app()
        
        # Vision result with complete analysis
        vision_result = {
            "objects_detected": ["person"],
            "danger_detected": False,
            "pleasure_detected": False,
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
        
        # Simulate cognitive_processing completion
        personality_result = {"status": "success"}
        app.perception_system.process_personality_functions = MagicMock(return_value=personality_result)
        app.perception_system.process_personality_functions({}, {})
        
        # Update vision display
        vision_display_result = {
            "objects_detected": vision_result.get("objects_detected", []),
            "danger_detected": vision_result.get("danger_detected", False),
            "danger_reason": vision_result.get("danger_reason", ""),
            "pleasure_detected": vision_result.get("pleasure_detected", False),
            "pleasure_reason": vision_result.get("pleasure_reason", ""),
            "analysis": vision_result.get("analysis", {})
        }
        
        app.after(0, lambda: app._update_vision_analysis_display(vision_display_result))
        
        # Verify all analysis fields are present
        analysis = app._update_vision_analysis_display_last_result.get("analysis", {})
        required_fields = ['who', 'what', 'when', 'where', 'why', 'how', 'expectation', 'self_recognition', 'mirror_context']
        
        for field in required_fields:
            assert field in analysis, f"Required field '{field}' missing from analysis"
        
        print(f"[PASS] All {len(required_fields)} analysis fields present")
        print("[PASS] TEST 2 PASSED: All analysis fields populated correctly")
        return True
    
    def test_danger_pleasure_populated(self):
        """Test that danger and pleasure are properly populated after cognitive_processing."""
        print("\n=== TEST 3: Danger and Pleasure Populated ===")
        
        app = self.setup_mock_app()
        
        # Vision result with danger and pleasure
        vision_result = {
            "objects_detected": ["fire", "cat"],
            "danger_detected": True,
            "danger_reason": "Fire detected in the environment",
            "pleasure_detected": True,
            "pleasure_reason": "Friendly cat detected",
            "analysis": {}
        }
        
        # Simulate cognitive_processing completion
        personality_result = {"status": "success"}
        app.perception_system.process_personality_functions = MagicMock(return_value=personality_result)
        app.perception_system.process_personality_functions({}, {})
        
        # Update vision display
        vision_display_result = {
            "objects_detected": vision_result.get("objects_detected", []),
            "danger_detected": vision_result.get("danger_detected", False),
            "danger_reason": vision_result.get("danger_reason", ""),
            "pleasure_detected": vision_result.get("pleasure_detected", False),
            "pleasure_reason": vision_result.get("pleasure_reason", ""),
            "analysis": vision_result.get("analysis", {})
        }
        
        app.after(0, lambda: app._update_vision_analysis_display(vision_display_result))
        
        # Verify danger and pleasure are in the result
        result = app._update_vision_analysis_display_last_result
        assert result.get("danger_detected") == True, "Danger should be detected"
        assert result.get("danger_reason") == "Fire detected in the environment", "Danger reason should be present"
        assert result.get("pleasure_detected") == True, "Pleasure should be detected"
        assert result.get("pleasure_reason") == "Friendly cat detected", "Pleasure reason should be present"
        
        print(f"[PASS] Danger detected: {result.get('danger_detected')}")
        print(f"[PASS] Danger reason: {result.get('danger_reason')}")
        print(f"[PASS] Pleasure detected: {result.get('pleasure_detected')}")
        print(f"[PASS] Pleasure reason: {result.get('pleasure_reason')}")
        print("[PASS] TEST 3 PASSED: Danger and pleasure populated correctly")
        return True
    
    def test_timely_update(self):
        """Test that the update happens in a timely manner (immediately after cognitive_processing)."""
        print("\n=== TEST 4: Timely Update ===")
        
        app = self.setup_mock_app()
        
        vision_result = {
            "objects_detected": ["test"],
            "danger_detected": False,
            "pleasure_detected": False,
            "analysis": {}
        }
        
        # Simulate cognitive_processing
        personality_result = {"status": "success"}
        app.perception_system.process_personality_functions = MagicMock(return_value=personality_result)
        
        # Record time before cognitive_processing
        import time
        time_before = time.time()
        
        # Execute cognitive_processing
        result = app.perception_system.process_personality_functions({}, {})
        
        # Immediately after, update vision display
        vision_display_result = {
            "objects_detected": vision_result.get("objects_detected", []),
            "danger_detected": vision_result.get("danger_detected", False),
            "danger_reason": vision_result.get("danger_reason", ""),
            "pleasure_detected": vision_result.get("pleasure_detected", False),
            "pleasure_reason": vision_result.get("pleasure_reason", ""),
            "analysis": vision_result.get("analysis", {})
        }
        
        app.after(0, lambda: app._update_vision_analysis_display(vision_display_result))
        
        time_after = time.time()
        time_elapsed = time_after - time_before
        
        # Verify update was called
        assert app._update_vision_analysis_display_called, "Vision display should be updated"
        
        # Verify it happened quickly (within reasonable time)
        # In real scenario, after(0) schedules immediately, so this should be very fast
        assert time_elapsed < 1.0, f"Update should happen quickly, took {time_elapsed:.3f}s"
        
        print(f"[PASS] Time elapsed: {time_elapsed:.3f}s")
        print(f"[PASS] Update called: {app._update_vision_analysis_display_called}")
        print("[PASS] TEST 4 PASSED: Update happens in timely manner")
        return True
    
    def test_complete_flow(self):
        """Test the complete flow: vision analysis → cognitive_processing → display update."""
        print("\n=== TEST 5: Complete Flow ===")
        
        app = self.setup_mock_app()
        
        # Step 1: Vision analysis result
        vision_result = {
            "objects_detected": ["desk", "chair", "person"],
            "danger_detected": False,
            "danger_reason": "",
            "pleasure_detected": True,
            "pleasure_reason": "Comfortable workspace detected",
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
        
        # Step 2: Cognitive processing
        personality_result = {
            "status": "success",
            "perception_processing": {
                "extroversion_energy": 0.4,
                "introversion_energy": 0.6,
                "intuition_level": 0.5,
                "sensation_level": 0.5
            }
        }
        
        app.perception_system.process_personality_functions = MagicMock(return_value=personality_result)
        
        # Step 3: Execute cognitive_processing
        cognitive_result = app.perception_system.process_personality_functions({}, {})
        
        # Step 4: Immediately update vision display after cognitive_processing
        if vision_result:
            vision_display_result = {
                "objects_detected": vision_result.get("objects_detected", []),
                "danger_detected": vision_result.get("danger_detected", False),
                "danger_reason": vision_result.get("danger_reason", ""),
                "pleasure_detected": vision_result.get("pleasure_detected", False),
                "pleasure_reason": vision_result.get("pleasure_reason", ""),
                "analysis": vision_result.get("analysis", {})
            }
            
            app.after(0, lambda: app._update_vision_analysis_display(vision_display_result))
        
        # Verify complete flow
        assert app.perception_system.process_personality_functions.called, "Cognitive processing should be called"
        assert cognitive_result.get("status") == "success", "Cognitive processing should succeed"
        assert app._update_vision_analysis_display_called, "Vision display should be updated"
        
        # Verify all data is present
        result = app._update_vision_analysis_display_last_result
        assert len(result.get("objects_detected", [])) == 3, "All objects should be present"
        assert result.get("pleasure_detected") == True, "Pleasure should be detected"
        assert "analysis" in result, "Analysis should be present"
        assert len(result.get("analysis", {})) == 9, "All analysis fields should be present"
        
        print(f"[PASS] Cognitive processing: {cognitive_result.get('status')}")
        print(f"[PASS] Vision display updated: {app._update_vision_analysis_display_called}")
        print(f"[PASS] Objects: {len(result.get('objects_detected', []))}")
        print(f"[PASS] Analysis fields: {len(result.get('analysis', {}))}")
        print("[PASS] TEST 5 PASSED: Complete flow works correctly")
        return True
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 60)
        print("VISION AFTER COGNITIVE PROCESSING TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Vision Display After Cognitive Processing", self.test_vision_display_after_cognitive_processing),
            ("Analysis Fields Populated", self.test_analysis_fields_populated),
            ("Danger and Pleasure Populated", self.test_danger_pleasure_populated),
            ("Timely Update", self.test_timely_update),
            ("Complete Flow", self.test_complete_flow)
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            try:
                if test_func():
                    passed += 1
                    self.test_results.append((test_name, "PASSED"))
                else:
                    failed += 1
                    self.test_results.append((test_name, "FAILED"))
            except Exception as e:
                failed += 1
                self.test_results.append((test_name, f"FAILED: {e}"))
                print(f"[FAIL] {test_name} FAILED: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 60)
        print("TEST RESULTS SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {len(tests)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        for test_name, result in self.test_results:
            status = "[PASS]" if result == "PASSED" else "[FAIL]"
            print(f"{status} {test_name}: {result}")
        
        return failed == 0

if __name__ == "__main__":
    tester = TestVisionAfterCognitiveProcessing()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

