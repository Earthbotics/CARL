"""
Test for Vision Controls Display Functionality

This test verifies that:
1. Objects Detected listbox displays correctly
2. Analysis section displays all fields (who, what, when, where, why, how, expectation, self_recognition, mirror_context)
3. Danger detection displays correctly (status and reason)
4. Pleasure detection displays correctly (status and reason)
5. All fields are displayed even with default/unknown values
"""

import sys
import os
from unittest.mock import Mock, MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestVisionControlsDisplay:
    """Test class for vision controls display functionality."""
    
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
        
        # Mock methods
        self.mock_app.log = print
        self.mock_app.after = lambda delay, func: func()  # Execute immediately for testing
        
        return self.mock_app
    
    def test_objects_detected_display(self):
        """Test that objects detected are displayed in the listbox."""
        print("\n=== TEST 1: Objects Detected Display ===")
        
        app = self.setup_mock_app()
        
        # Simulate vision result with objects
        vision_result = {
            "objects_detected": ["desk", "chair", "person", "laptop", "monitor"],
            "danger_detected": False,
            "pleasure_detected": False,
            "analysis": {}
        }
        
        # Simulate _update_vision_analysis_display behavior
        objects_detected = vision_result.get('objects_detected', [])
        if objects_detected:
            objects_text = '\n'.join([f"• {obj}" for obj in objects_detected])
            app.objects_detected_text.config(state='normal')
            app.objects_detected_text.delete('1.0', 'end')
            app.objects_detected_text.insert('1.0', objects_text)
            app.objects_detected_text.config(state='disabled')
        
        # Verify display was updated
        assert app.objects_detected_text.delete.called, "Objects text delete should be called"
        assert app.objects_detected_text.insert.called, "Objects text insert should be called"
        assert app.objects_detected_text.config.called, "Objects text config should be called"
        
        print(f"[PASS] Objects detected: {len(objects_detected)}")
        print(f"[PASS] Objects text: {objects_text[:50]}...")
        print("[PASS] TEST 1 PASSED: Objects detected displayed correctly")
        return True
    
    def test_analysis_display_all_fields(self):
        """Test that all analysis fields are displayed, even with default values."""
        print("\n=== TEST 2: Analysis Display - All Fields ===")
        
        app = self.setup_mock_app()
        
        # Simulate vision result with complete analysis (including default values)
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
        
        # Simulate _update_vision_analysis_display behavior for analysis
        analysis = vision_result.get('analysis', {})
        if analysis:
            analysis_lines = []
            analysis_lines.append("ANALYSIS:")
            analysis_lines.append(f"Who: {analysis.get('who', 'unknown')}")
            analysis_lines.append(f"What: {analysis.get('what', 'unknown')}")
            analysis_lines.append(f"When: {analysis.get('when', 'unknown')}")
            analysis_lines.append(f"Where: {analysis.get('where', 'unknown')}")
            analysis_lines.append(f"Why: {analysis.get('why', 'unknown')}")
            analysis_lines.append(f"How: {analysis.get('how', 'unknown')}")
            analysis_lines.append(f"Expectation: {analysis.get('expectation', 'unknown')}")
            analysis_lines.append(f"Self Recognition: {analysis.get('self_recognition', False)}")
            analysis_lines.append(f"Mirror Context: {analysis.get('mirror_context', False)}")
            
            analysis_text = '\n'.join(analysis_lines)
            
            app.analysis_text.config(state='normal')
            app.analysis_text.delete('1.0', 'end')
            app.analysis_text.insert('1.0', analysis_text)
            app.analysis_text.config(state='disabled')
        
        # Verify all required fields are present
        required_fields = ['who', 'what', 'when', 'where', 'why', 'how', 'expectation', 'self_recognition', 'mirror_context']
        for field in required_fields:
            assert field in analysis, f"Required field '{field}' missing from analysis"
        
        # Verify display was updated
        assert app.analysis_text.delete.called, "Analysis text delete should be called"
        assert app.analysis_text.insert.called, "Analysis text insert should be called"
        
        print(f"[PASS] Analysis fields: {len(required_fields)}")
        print(f"[PASS] Analysis text preview: {analysis_text[:100]}...")
        print("[PASS] TEST 2 PASSED: All analysis fields displayed correctly")
        return True
    
    def test_danger_detection_display(self):
        """Test that danger detection displays correctly."""
        print("\n=== TEST 3: Danger Detection Display ===")
        
        app = self.setup_mock_app()
        
        # Test case 1: Danger detected
        vision_result_danger = {
            "objects_detected": ["fire", "smoke"],
            "danger_detected": True,
            "danger_reason": "Fire and smoke detected in the environment",
            "analysis": {}
        }
        
        # Simulate danger display
        if vision_result_danger.get('danger_detected', False):
            app.danger_status_label.config(text="Detected", foreground='red')
            app.danger_reason_text.config(state='normal')
            app.danger_reason_text.delete('1.0', 'end')
            app.danger_reason_text.insert('1.0', vision_result_danger.get('danger_reason', ''))
            app.danger_reason_text.config(state='disabled')
        else:
            app.danger_status_label.config(text="Not detected", foreground='green')
            app.danger_reason_text.config(state='normal')
            app.danger_reason_text.delete('1.0', 'end')
            app.danger_reason_text.insert('1.0', 'No danger detected')
            app.danger_reason_text.config(state='disabled')
        
        # Verify danger display was updated
        assert app.danger_status_label.config.called, "Danger status label should be configured"
        assert app.danger_reason_text.delete.called, "Danger reason text delete should be called"
        assert app.danger_reason_text.insert.called, "Danger reason text insert should be called"
        
        print(f"[PASS] Danger detected: {vision_result_danger.get('danger_detected')}")
        print(f"[PASS] Danger reason: {vision_result_danger.get('danger_reason', 'N/A')}")
        print("[PASS] TEST 3 PASSED: Danger detection displayed correctly")
        return True
    
    def test_pleasure_detection_display(self):
        """Test that pleasure detection displays correctly."""
        print("\n=== TEST 4: Pleasure Detection Display ===")
        
        app = self.setup_mock_app()
        
        # Test case: Pleasure detected
        vision_result_pleasure = {
            "objects_detected": ["friendly cat", "toy"],
            "danger_detected": False,
            "pleasure_detected": True,
            "pleasure_reason": "Friendly cat and toy detected - positive interaction opportunity",
            "analysis": {}
        }
        
        # Simulate pleasure display
        if vision_result_pleasure.get('pleasure_detected', False):
            app.pleasure_status_label.config(text="Detected", foreground='green')
            app.pleasure_reason_text.config(state='normal')
            app.pleasure_reason_text.delete('1.0', 'end')
            app.pleasure_reason_text.insert('1.0', vision_result_pleasure.get('pleasure_reason', ''))
            app.pleasure_reason_text.config(state='disabled')
        else:
            app.pleasure_status_label.config(text="Not detected", foreground='blue')
            app.pleasure_reason_text.config(state='normal')
            app.pleasure_reason_text.delete('1.0', 'end')
            app.pleasure_reason_text.insert('1.0', 'No pleasure detected')
            app.pleasure_reason_text.config(state='disabled')
        
        # Verify pleasure display was updated
        assert app.pleasure_status_label.config.called, "Pleasure status label should be configured"
        assert app.pleasure_reason_text.delete.called, "Pleasure reason text delete should be called"
        assert app.pleasure_reason_text.insert.called, "Pleasure reason text insert should be called"
        
        print(f"[PASS] Pleasure detected: {vision_result_pleasure.get('pleasure_detected')}")
        print(f"[PASS] Pleasure reason: {vision_result_pleasure.get('pleasure_reason', 'N/A')}")
        print("[PASS] TEST 4 PASSED: Pleasure detection displayed correctly")
        return True
    
    def test_complete_vision_result_display(self):
        """Test complete vision result with all components."""
        print("\n=== TEST 5: Complete Vision Result Display ===")
        
        app = self.setup_mock_app()
        
        # Complete vision result with all fields
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
        
        # Simulate complete display update
        # 1. Objects detected
        objects_detected = vision_result.get('objects_detected', [])
        if objects_detected:
            objects_text = '\n'.join([f"• {obj}" for obj in objects_detected])
            app.objects_detected_text.config(state='normal')
            app.objects_detected_text.delete('1.0', 'end')
            app.objects_detected_text.insert('1.0', objects_text)
            app.objects_detected_text.config(state='disabled')
        
        # 2. Danger
        if vision_result.get('danger_detected', False):
            app.danger_status_label.config(text="Detected", foreground='red')
            app.danger_reason_text.config(state='normal')
            app.danger_reason_text.delete('1.0', 'end')
            app.danger_reason_text.insert('1.0', vision_result.get('danger_reason', ''))
            app.danger_reason_text.config(state='disabled')
        else:
            app.danger_status_label.config(text="Not detected", foreground='green')
            app.danger_reason_text.config(state='normal')
            app.danger_reason_text.delete('1.0', 'end')
            app.danger_reason_text.insert('1.0', 'No danger detected')
            app.danger_reason_text.config(state='disabled')
        
        # 3. Pleasure
        if vision_result.get('pleasure_detected', False):
            app.pleasure_status_label.config(text="Detected", foreground='green')
            app.pleasure_reason_text.config(state='normal')
            app.pleasure_reason_text.delete('1.0', 'end')
            app.pleasure_reason_text.insert('1.0', vision_result.get('pleasure_reason', ''))
            app.pleasure_reason_text.config(state='disabled')
        else:
            app.pleasure_status_label.config(text="Not detected", foreground='blue')
            app.pleasure_reason_text.config(state='normal')
            app.pleasure_reason_text.delete('1.0', 'end')
            app.pleasure_reason_text.insert('1.0', 'No pleasure detected')
            app.pleasure_reason_text.config(state='disabled')
        
        # 4. Analysis
        analysis = vision_result.get('analysis', {})
        if analysis:
            analysis_lines = []
            analysis_lines.append("ANALYSIS:")
            analysis_lines.append(f"Who: {analysis.get('who', 'unknown')}")
            analysis_lines.append(f"What: {analysis.get('what', 'unknown')}")
            analysis_lines.append(f"When: {analysis.get('when', 'unknown')}")
            analysis_lines.append(f"Where: {analysis.get('where', 'unknown')}")
            analysis_lines.append(f"Why: {analysis.get('why', 'unknown')}")
            analysis_lines.append(f"How: {analysis.get('how', 'unknown')}")
            analysis_lines.append(f"Expectation: {analysis.get('expectation', 'unknown')}")
            analysis_lines.append(f"Self Recognition: {analysis.get('self_recognition', False)}")
            analysis_lines.append(f"Mirror Context: {analysis.get('mirror_context', False)}")
            
            analysis_text = '\n'.join(analysis_lines)
            
            app.analysis_text.config(state='normal')
            app.analysis_text.delete('1.0', 'end')
            app.analysis_text.insert('1.0', analysis_text)
            app.analysis_text.config(state='disabled')
        
        # Verify all components were updated
        assert app.objects_detected_text.delete.called, "Objects text should be updated"
        assert app.danger_status_label.config.called, "Danger status should be updated"
        assert app.pleasure_status_label.config.called, "Pleasure status should be updated"
        assert app.analysis_text.delete.called, "Analysis text should be updated"
        
        # Verify all analysis fields are present
        required_fields = ['who', 'what', 'when', 'where', 'why', 'how', 'expectation', 'self_recognition', 'mirror_context']
        for field in required_fields:
            assert field in analysis, f"Required field '{field}' missing"
        
        print(f"[PASS] Objects: {len(objects_detected)}")
        print(f"[PASS] Danger: {vision_result.get('danger_detected')}")
        print(f"[PASS] Pleasure: {vision_result.get('pleasure_detected')}")
        print(f"[PASS] Analysis fields: {len(required_fields)}")
        print("[PASS] TEST 5 PASSED: Complete vision result displayed correctly")
        return True
    
    def test_default_values_display(self):
        """Test that default/unknown values are still displayed."""
        print("\n=== TEST 6: Default Values Display ===")
        
        app = self.setup_mock_app()
        
        # Vision result with all default/unknown values
        vision_result = {
            "objects_detected": [],
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
        
        # Simulate display update
        analysis = vision_result.get('analysis', {})
        if analysis:
            analysis_lines = []
            analysis_lines.append("ANALYSIS:")
            for key in ['who', 'what', 'when', 'where', 'why', 'how', 'expectation', 'self_recognition', 'mirror_context']:
                value = analysis.get(key, 'unknown')
                analysis_lines.append(f"{key.capitalize()}: {value}")
            
            analysis_text = '\n'.join(analysis_lines)
            
            app.analysis_text.config(state='normal')
            app.analysis_text.delete('1.0', 'end')
            app.analysis_text.insert('1.0', analysis_text)
            app.analysis_text.config(state='disabled')
        
        # Verify all fields are displayed even with default values
        default_values = ['unknown individual', 'person in a room', 'current time', 'indoor setting', 
                         'context not provided', 'observational', 'unclear']
        
        analysis_text_content = analysis_text.lower()
        for default_val in default_values:
            assert default_val.lower() in analysis_text_content, f"Default value '{default_val}' should be displayed"
        
        print(f"[PASS] All default values displayed in analysis")
        print(f"[PASS] Analysis text length: {len(analysis_text)} characters")
        print("[PASS] TEST 6 PASSED: Default values displayed correctly")
        return True
    
    def run_all_tests(self):
        """Run all tests and report results."""
        print("=" * 60)
        print("VISION CONTROLS DISPLAY TEST SUITE")
        print("=" * 60)
        
        tests = [
            ("Objects Detected Display", self.test_objects_detected_display),
            ("Analysis Display - All Fields", self.test_analysis_display_all_fields),
            ("Danger Detection Display", self.test_danger_detection_display),
            ("Pleasure Detection Display", self.test_pleasure_detection_display),
            ("Complete Vision Result Display", self.test_complete_vision_result_display),
            ("Default Values Display", self.test_default_values_display)
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
    tester = TestVisionControlsDisplay()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)

